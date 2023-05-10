# -*- coding: utf-8 -*-
"""
  执行测试前需要确认的事情：
  1 确定mysql服务器是否ready
  2 创建数据库test
  3 创建库表 table_student
    确保为唯一主键，且为自增长
  4 Good luck!
"""
from ..DBMySql import DBConn

# 换成自己的mysql服务器信息
conn = DBConn(host='127.0.0.1', user='user',
              passwd='password', database='test')
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

update_rows = conn.update('t_jobs', [{'id': 1, 'gender': 'male', 'class': '1'},
                                     {'id': 2, 'class': '2'},
                                     {'name': 'cici', 'gender': 'female'}
                                     ])
print('update: update count:%d; ids:%s' % (len(update_rows),
      ','.join([str(row.get('id')) for row in update_rows])))

print('de:', conn.de('update table_student set class="2" where id=3'))
