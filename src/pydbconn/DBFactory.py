
def CreateConn(type, **config):
    if type == 'MySql':
        from pydbconn.Mysql import Mysql
        return Mysql(**config)
    else:
        from pydbconn.Sqlite import Sqlite
        return Sqlite(**config)
