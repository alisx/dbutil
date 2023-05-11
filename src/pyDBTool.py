
def CreateConn(type, **config):
    if type == 'MySql':
        from DBMySql import DBMySql
        return DBMySql(**config)
    else:
        from DBSqlite import DBSqlite
        return DBSqlite(**config)
