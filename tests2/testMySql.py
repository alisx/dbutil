# -*- coding: utf-8 -*-

import init
from pydbconn.DBMySql import DBMySql

TableSql = '''
CREATE TABLE `table_student` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `class` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
'''
# 换成自己的mysql服务器连接信息
conn = DBMySql(host='127.0.0.1', user='user',
               passwd='password', database='test')
conn.de(TableSql)

print('链接创建成功')
print('测试qj:', conn.qj("select * from table_student"))
print('qvs:', conn.qvs("select name from table_student"))
print('qv:', conn.qv("select age from table_student"))
print('qo:', conn.qo('select * from table_student'))
insert_rows = conn.insert('table_student', [{'name': 'xiaoming', 'age': 12},
                                            {'name': 'xiaohong', 'age': 11,
                                                'gender': 'female'}
                                            ])
print('insert: insert count:%d; ids:%s' % (len(insert_rows),
      ','.join([str(row.get('id')) for row in insert_rows])))

update_rows = conn.update('table_student', [{'id': 1, 'gender': 'male', 'class': '1'},
                                            {'id': 2, 'class': '2'},
                                            {'name': 'cici', 'gender': 'female'}
                                            ])
print('update: update count:%d; ids:%s' % (len(update_rows),
      ','.join([str(row.get('id')) for row in update_rows])))

print('de:', conn.de('update table_student set class="2" where id=3'))
