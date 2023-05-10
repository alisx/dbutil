# -*- coding: utf-8 -*-
"""
    封装对MYSQL的操作
    使用时直接简单的操作
    对于多个库，可以自己去创建链接
    支持链接池
    支持日志
"""
import pymysql
import logging
from queue import Queue

logger = logging.getLogger(__name__)


class DBMySql(object):
    _config = {
        'charset': 'utf8',
        'use_unicode': True,
        'port': 3306
    }

    def __del__(self):
        while not self.pool.empty():
            self.pool.get().close()
        self.close = True

    def __init__(self, **config):
        self.__config = DBMySql._config.copy()
        if config:
            self.__config.update(config)

        self.poolcount = self.__config.get('poolcount', 10)
        self.pool = Queue(self.poolcount)
        self.__close = False
        self.readycount = 0
        self.inusecount = 0
        for _ in range(self.poolcount):
            self.pool.put(self.__create_conn())
            self.readycount += 1

    def __create_conn(self):
        conn = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor, **self.__config)
        return conn

    def __get_conn(self):
        if self.inusecount + self.readycount != self.poolcount:
            logger.warning("链接数量不等于链接池容量！")

        try:
            if self.__close:
                raise Exception("模块已关闭，无法获取链接")
            if self.pool.empty():
                logger.warning("链接池没有空余链接，将创建。")
                conn = self.__create_conn()  # 有可能超拿
            else:
                conn = self.pool.get()
            if not conn.open:
                conn = self.__create_conn()
            self.inusecount += 1
            self.readycount = self.pool.qsize()
        except Exception as e:
            logger.exception(f'获取链接出错:{e}')
            raise e
        return conn

    def __back_conn(self, conn):
        if self.inusecount + self.readycount != self.poolcount:
            logger.warning("链接数量不等于链接池容量！")

        if conn.open:
            if self.pool.full():
                logger.warning("链接池已满，将释放。")
                conn.close()  # 放弃掉
            else:
                self.pool.put(conn)
        else:  # 补充
            logger.warning("要还回的链接已关闭，将丢弃")

        self.inusecount -= 1
        self.readycount = self.pool.qsize()

    def qj(self, sql, conn=None):
        is_inner = True if conn is None else False
        if is_inner:
            conn = self.__get_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql)
            ret = cursor.fetchall()
        if is_inner:
            self.__back_conn(conn)
        return ret
        pass

    def qv(self, sql, conn=None):
        values = self.qvs(sql, conn)
        if len(values) == 0:
            return None
        return values[0]
        pass

    def qvs(self, sql, conn=None):
        rows = self.qj(sql, conn)
        if len(rows) == 0:
            return []
        values = []
        key = next(iter(rows[0]))
        for row in rows:
            values.append(row.get(key))
        return values
        pass

    def qo(self, sql, conn=None):
        rows = self.qj(sql, conn)
        if len(rows) > 0:
            return rows[0]
        else:
            return None
        pass

    def de(self, sql, conn=None):
        is_inner = True if conn is None else False
        if is_inner:
            conn = self.__get_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            ret = cursor.execute(sql)
        if is_inner:
            conn.commit()
            self.__back_conn(conn)
        return ret
        pass

    def get_table_fields(self, *args, **kargs):
        return self.__get_table_fields(*args, **kargs)

    def __get_table_fields(self, table_name, conn=None):
        is_inner = True if conn is None else False
        if is_inner:
            conn = self.__get_conn()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("show fields from %s " % table_name)
            field_names = []
            primary_keys = []
            for f in cursor.fetchall():
                field_names.append(f.get('Field'))
                if f.get('Key') == 'PRI':
                    primary_keys.append(f.get('Field'))
            ret = {
                'fields': field_names,
                'primary_keys': primary_keys
            }
        if is_inner:
            self.__back_conn(conn)
        return ret
        pass

    def insert(self, table_name, rows, conn=None):
        # is_innser 表示是否属于处理内部，比如update可能会调用insert，此时insert是内部的
        is_inner = True if conn is None else False
        if is_inner:
            conn = self.__get_conn()
        # 获取表的字段
        all_fields = self.__get_table_fields(table_name, conn)
        logger.debug(
            f"DBUtil insert after gettable fields  pool size:{self.pool.size()}")
        # insert_sqls = []
        insert_fields = all_fields.get('fields')
        insert_sql = "insert into %s (%s) " % (
            table_name, '`'+'`,`'.join(insert_fields)+'`')
        insert_sql += "values(" + ','.join(['%s'] * len(insert_fields)) + ")"

        values = []
        for row in rows:
            insert_values = []
            for f in insert_fields:
                val = row.get(f, None)
                if val:
                    insert_values.append(row.get(f))
                else:
                    insert_values.append(None)
            values.append(insert_values)
        if len(values) == 0:
            return rows
        logger.debug(
            f"DBUtil insert after mark rows  pool size:{self.pool.size()}")
        try:
            effect_count = 0
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                if len(values) > 1:
                    effect_count = cursor.executemany(insert_sql, values[:-1])
                    logger.debug(
                        f"DBUtil insert after cursor.executemany  pool size:{self.pool.size()}")
                _effect_count = cursor.execute(insert_sql, values[-1])
                logger.debug(
                    f"DBUtil insert after cursor.execute  pool size:{self.pool.size()}")
                effect_count += _effect_count
                sql = 'select * from %(tb)s where %(pk)s>%(bid)d and %(pk)s<%(eid)d' % {
                    'tb': table_name,
                    'pk': all_fields.get('primary_keys')[0],
                    'bid': cursor.lastrowid-effect_count,
                    'eid': cursor.lastrowid+effect_count
                }
            if is_inner:
                conn.commit()
                logger.debug(
                    f"DBUtil insert after conn.commit()  pool size:{self.pool.size()}")
            rows = self.qj(sql, conn)
            logger.debug(
                f"DBUtil insert after self.qj(sql, conn)  pool size:{self.pool.size()}")
            if type(rows) == tuple:
                rows = list(rows)
        except pymysql.Error as e:
            logger.error(f"insert error:{e}")
            if is_inner:
                conn.rollback()
            raise e
        finally:
            if is_inner:
                self.__back_conn(conn)
        return rows
        pass

    """
    有主键就更新，无主键则新增
    """

    def update(self, table_name, rows, conn=None):
        is_inner = True if conn is None else False
        if is_inner:
            conn = self.__get_conn()

        all_fields = self.__get_table_fields(table_name, conn)

        update_rows = []
        insert_rows = []

        for row in rows:
            for pk in all_fields.get('primary_keys'):
                if row.get(pk):
                    # update
                    update_rows.append(row)
                else:
                    # insert
                    insert_rows.append(row)
        try:

            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                for row in update_rows:
                    key_list = []
                    for f in all_fields.get('fields'):
                        if f in all_fields.get('primary_keys'):  # 主键不参与更新
                            continue
                        val = row.get(f, None)
                        if val is not None:  # 有值
                            placeholder = "{}=".format(f) + "%({})s".format(f)
                            key_list.extend([placeholder])
                    if len(key_list) > 0:
                        val_list = ",".join(key_list)
                        sql = "UPDATE `{table}` SET {values} WHERE `{idDirectConnect_ID}`= %({idDirectConnect_ID})s;" \
                            .format(table=table_name, values=val_list, idDirectConnect_ID=all_fields.get('primary_keys')[0])
                        logger.debug(f'Update sql:{sql}')
                        cursor.execute(sql, row)
            insert_rows = self.insert(table_name, insert_rows, conn)

            update_rows.extend(insert_rows)
            if is_inner:
                conn.commit()
        except pymysql.Error as e:
            if is_inner:
                conn.rollback()
            raise e
        finally:
            if is_inner:
                self.__back_conn(conn)

        return update_rows
        pass


if __name__ == '__main__':
    sets = {
        'host': '127.0.0.1',
        'user': 'user',
        'passwd': 'passwd',
        'database': 'db'
    }
    tconn = DBMySql(
        host=sets['host'], user=sets['user'], passwd=sets['passwd'],
        database=sets['database']
    )

    print(tconn.qj("select sysdate()"))
