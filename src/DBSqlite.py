import sqlite3

class DBSqlite:
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._conn = None

    def __del__(self):
        if self._conn:
            self._conn.close()
        
    def _get_conn(self):
        if not self._conn:
            self._conn = sqlite3.connect(self.db)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    def _close_conn(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _query(self, sql):
        conn = self._get_conn()
        cur = conn.cursor()
        rows = []
        for row in cur.execute(sql):
            rows.append(row)
        cur.close()
        self._close_conn()
        return rows

    def de(self, sql):
        conn = self._get_conn()
        cur = conn.cursor()
        for s in sql.split(";"):
            cur.execute(s)
        conn.commit()
        cur.close()
        self._close_conn()
        return True

    def insert(self, table, rows):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.executemany("insert into %s values (%s)" % (table, ("?,"*len(rows[0]))[:-1]), rows)
        conn.commit()
        cur.close()
        self._close_conn()
        return True

    def qj(self, sql, toDict=False):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        self._close_conn()
        if toDict:
            return self.sqlRowsToDict(rows)
        else:
            return rows
    
    def qv(self, sql):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        self._close_conn()
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None
            
    def qvs(self, sql):
        data = self.qj(sql)
        ret = []
        for d in data:
            ret.append(d[0])
        return ret
            
    def sqlRowsToDict(self, data, toList=False):
        rows = []
        if toList:
            heads = []
            for k in data[0].keys():
                heads.append(k)
            rows.append(heads)
            
        for d in data:
            row = []
            if toList:
                for k in d.keys():
                    row.append(d[k])
            else:
                row = {}
                for k in d.keys():
                    row[k] = d[k]
            rows.append(row)
        return rows