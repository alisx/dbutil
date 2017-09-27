# dbutil
基于pymsql的mysql数据库类

pymsql模块很强大，但是操作Mysql数据库还是很繁琐，比如insert时需要拼接插入语句的
于是依据以往使用习惯，编写了DBUtil类，目前只支持mysql，未来会扩展其他数据库

例子
```python
import DBUtil

conn = DBUtil.DBConn(host='127.0.0.1', user='user', passwd='password', database='test')

rows = [{'name': 'xiaoming', 'age': '12', 'gender': 'male'},
        {'name': 'xiaohong', 'age': '11', 'gender': 'female'}]
ret = conn.insert('table_student', rows)
print('ret:',ret)

# print
# ret:[{'id': 1, 'name': 'xiaoming', 'age': '12', 'gender': 'male', 'class': None}, {'id': 2, 'name': 'xiaohong', 'age': '11', 'gender': 'female', 'class': None}]
```
### 注意 ###
+ 库表必须有且有唯一的自增长主键

### 方法 ###
+ ```DBConn```<br>
  创建一个数据库工具实例<br>
  必须提供参数 ```host```，```user```，```passwd```<br>
  可选参数 ``database``，不提供，需要在语句中指定数据库<br>
          ``charset`` 默认 ``utf8``<br>
          ``use_unicode`` 默认``True``<br>
+ qj
  执行一个查询语句，query json 的简写<br>
  参数：``sql``<br>
  返回：查询结果``list``<br>
  
+ qvs
  执行一个查询语句 query values 的简写<br>
  参数：``sql``<br>
  返回：查询结果集的第一列组成的``list``<br>
  
+ qv
  执行一个查询语句 query value 的简写<br>
  参数：``sql``<br>
  返回：查询结果集的第一行第一列的值<br>
  
+ qo
  执行一个查询语句 query object 的简写<br>
  参数：``sql``<br>
  返回：查询结果集的第一行的``dict``<br>
  
+ de
  执行一个sql语句 do execute 的简写<br>
  参数：``sql``<br>
  返回：影响行数<br>
  
+ insert
  向库表中插入多行记录<br>
  参数：``table_name`` 库表名称<br>
        ``rows`` 需要插入的记录，``list``类型<br>
  返回：插入库表的结果，``list``类型<br>
  说明：<br>
    1. 以库表字段为主，记录中不提供视为None
    2. 每行记录的字段可以不一致
    3. 记录中不属于库表的字段会被忽略
 
+ update
  更新库表中的多行记录
  参数：``table_name`` 库表名称<br>
        ``rows`` 需要更新的记录，``list``类型<br>
  返回：更新库表的结果，``list``类型<br>
  说明：<br>
    1. 只更新库表中存在且记录中提供的字段
    2. 每行记录的字段可以不一致
    3. 如果记录中没有提供主键，会被做插入处理
