## pyDBUtil 库

### 简介

#### DBMySql

是基于 pymsql的mysql数据库类，且**支持链接池**;

pymsql模块很强大，但是操作Mysql数据库还是很繁琐，比如insert时需要拼接插入语句的
于是依据以往使用习惯，编写了DBUtil类，目前只支持mysql，未来会扩展其他数据库

默认创建 10 个链接。

使用时可以不用关注链接池，模块方法会自动处理链接，对于失效链接会自动做替换。

例子：

```python
import DBMysql

db = DBMysql.DBConn(poolcount=10, host='127.0.0.1', user='user', passwd='password', database='test')

rows = [{'name': 'xiaoming', 'age': '12', 'gender': 'male'},
        {'name': 'xiaohong', 'age': '11', 'gender': 'female'}]
ret = db.insert('table_student', rows)
print('ret:',ret)

# print
# ret:[{'id': 1, 'name': 'xiaoming', 'age': '12', 'gender': 'male', 'class': None}, {'id': 2, 'name': 'xiaohong', 'age': '11', 'gender': 'female', 'class': None}]
```

> **注意**
> 如果需要写库表，请确保该库表 **必须有且有唯一的自增长主键**

#### DBSqlite

是在 DBMySql 的基础上，改造的基于 Sqlite3 的数据操控工具，目前不支持连接池

除了创建连接对象接口，其他接口均和 DBMySql 一致。

例子：

```python

import DBSqlite

db = DBSqlite('mydb.db')

rows = [{'name': 'xiaoming', 'age': '12', 'gender': 'male'},
        {'name': 'xiaohong', 'age': '11', 'gender': 'female'}]
ret = db.insert('table_student', rows)
print('ret:',ret)

# print
# ret:[{'id': 1, 'name': 'xiaoming', 'age': '12', 'gender': 'male', 'class': None}, {'id': 2, 'name': 'xiaohong', 'age': '11', 'gender': 'female', 'class': None}]
```

### 依赖

- python3.6+
- pymysql: `pip install pymysql`
- sqlite3: `pip install pysqlite3`

### 方法

- **`DBConn`** 创建一个数据库工具实例
  
   `DBMySQL`:

  *必选参数*：
  - `host`
  - `user`
  - `passwd`
  
  *可选参数*：
  - `database` 如果不提供，必须在语句中指定数据库，如 `select * from mydb.mytable`
  - `charset` 默认 `utf8`
  - `use_unicode` 默认`True`
  - `poolcount` 链接池中链接数量
  
  `DBSqlite`:

  *必选参数*：
  - `db`：数据库文件路径

  *返回*：数据库连接对象
  
- **`qj`** 执行一个查询语句，query json 的简写
  
  *参数*：
  - `sql` 查询语句字符串
  
  *返回*：查询结果，数据结构为 `list`
  
- **`qvs`** 执行一个查询语句， query values 的简写
  
  *参数*：
  - `sql` 查询语句字符串
  
  *返回*：查询结果集的第一列组成的 `list`
  
- **`qv`** 执行一个查询语句， query value 的简写
  
  *参数*：
  - `sql` 查询语句字符串

  *返回*：查询结果集的第一行第一列的值
  
- **`qo`** 执行一个查询语句 query object 的简写
  
  *参数*：
  - `sql` 查询语句字符串
  
  *返回*：查询结果集的第一行的`dict`
  
- **`de`** 执行一个sql语句 do execute 的简写
  
  *参数*：
  - `sql` 查询语句字符串

  *返回*：影响行数
  
- **`insert`** 向库表中插入多行记录
  > *说明*
  >
  >1. 以库表字段为主，记录中不提供视为None
  >2. 每行记录的字段可以不一致
  >3. 记录中不属于库表的字段会被忽略
  
  *参数*：
  - `table_name` 库表名称
  - `rows` 需要插入的记录，`list`类型

  *返回*：插入库表的结果，`list`类型
  
- **`update`** 更新库表中的多行记录
  > *说明*
  >
  >  1. 只更新库表中存在且记录中提供的字段
  >  2. 每行记录的字段可以不一致
  >  3. 如果记录中没有提供主键，会被做插入处理

    *参数*
  - `table_name` 库表名称
  - `rows` 需要更新的记录，`list`类型

  *返回*：更新库表的结果，`list`类型

### 许可

本项目采用 **MPL 2**，大体含义是：

1. 他人修改后不能闭源
2. 新增代码可以不采用本许可证
3. 需要对源码修改处提供文档说明
