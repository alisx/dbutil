# -*- coding: utf-8 -*-
"""
    封装对MYSQL的操作
    使用时直接简单的操作
    对于多个库，可以自己去创建链接
"""
import pymysql


class DBConn(object):
    _config = {
        'charset': 'utf8',
        'use_unicode': True
    }

    def __init__(self, **config):
        self.__config = DBConn._config.copy()
        if config:
            self.__config.update(config)
        pass

    def __get_conn(self, **config):
        config = config if config else dict(self.__config, **config)
        conn = {}
        try:
            conn = pymysql.connect(
                host=config['host'],
                user=config['user'],
                passwd=config['passwd'],
                database=config['database'],
                charset=config['charset'],
                use_unicode=config['use_unicode']
            )
        except pymysql.Error as e:
            print('链接数据库出错:', e)
            raise
        return conn
        pass

    def qj(self, sql, conn=None):
        if conn is None:
            conn = self.__get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        return cursor.fetchall()
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
        if conn is None:
            conn = self.__get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        return cursor.execute(sql)
        pass

    def __get_table_fields(self, table_name, conn=None):
        if conn is None:
            conn = self.__get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("show fields from %s " % table_name)
        field_names = []
        primary_keys = []
        for f in cursor.fetchall():
            field_names.append(f.get('Field'))
            if f.get('Key') == 'PRI':
                primary_keys.append(f.get('Field'))
        return {
            'fields': field_names,
            'primary_keys': primary_keys
        }
        pass

    def insert(self, table_name, rows, conn=None):
        # 获取表的字段
        all_fields = self.__get_table_fields(table_name)
        insert_sqls = []
        insert_fields = all_fields.get('fields')
        insert_sql = "insert into %s (%s) " % (table_name, '`'+'`,`'.join(insert_fields)+'`')
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
        if conn is None:
            conn = self.__get_conn()

        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            insert_sql += ','.join(insert_sqls)
            effect_count = cursor.executemany(insert_sql, values)
            rows = self.qj('select * from %s where %s>=%d' % (
                table_name,
                all_fields.get('primary_keys')[0],
                cursor.lastrowid-effect_count+1,
            ))
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            raise
        finally:
            conn.close()
        return rows
        pass

    """
    有主键就更新，无主键则新增
    """
    def update(self, table_name, rows, conn=None):
        all_fields = self.__get_table_fields(table_name)
        key_list = []
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
            if conn is None:
                conn = self.__get_conn()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            for row in update_rows:
                for f in all_fields.get('fields'):
                    if f in all_fields.get('primary_keys'):  # 主键不参与更新
                        continue
                    val = row.get(f, None)
                    if val:  # 有值
                        placeholder = "{}=".format(f) + "%({})s".format(f)
                        key_list.extend([placeholder])
                if len(key_list) > 0:
                    val_list = ",".join(key_list)
                    sql = "UPDATE `{table}` SET {values} WHERE `{idDirectConnect_ID}`= %({idDirectConnect_ID})s;" \
                        .format(table=table_name, values=val_list, idDirectConnect_ID=all_fields.get('primary_keys')[0])
                    cursor.execute(sql, row)
            insert_rows = self.insert(table_name, insert_rows, conn)

            update_rows.extend(insert_rows)
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            raise
        finally:
            conn.close()
            
        return update_rows
        pass
