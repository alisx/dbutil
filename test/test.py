import init
from pyDBTool import CreateConn

conn = CreateConn('Sqlite', db="sqlitetest.db")

rows = conn.qj("select * from table_student")

print(rows)
