# -*- coding: utf-8 -*-

import init
from DBSqlite import DBSqlite

TableSQL = '''
CREATE TABLE IF NOT EXISTS "table_student" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
    "age" INTEGER,
    "gender" TEXT,
    "class" TEXT
);
'''
conn = DBSqlite('sqlitetest.db')

conn.de(TableSQL)

insert_rows = conn.insert('table_student', [{'name': 'xiaoming', 'age': 12},
                                            {'name': 'xiaohong', 'age': 11,
                                             'gender': 'female'}
                                            ])
print('insert: insert count:%d; ids:%s' % (len(insert_rows),
      ','.join([str(row.get('id')) for row in insert_rows])))

update_rows = conn.update('table_student', [{'id': 1, 'gender': 'female', 'class': '1'},
                                            {'id': 2, 'class': '2', 'age': 10},
                                            {'name': 'cici', 'gender': 'female'}
                                            ])
print('update: update count:%d; ids:%s' % (len(update_rows),
      ','.join([str(row.get('id')) for row in update_rows])))

print('de:', conn.de('update table_student set class="2" where id=3'))
