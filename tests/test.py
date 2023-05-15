import init
from pydbconn.DBFactory import CreateConn
import unittest

# -------


class TestDB(unittest.TestCase):
    def test_Sqlite_conncat(self):
        conn = CreateConn('Sqlite', db="sqlitetest.db")
        rows = conn.qj("select * from table_student")
        self.assertLess(0, len(rows), "得到了数据")
        self.assertEqual(3, rows[0].get('id'), "第一行第一列的值为 1")
