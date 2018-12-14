
1.#根据已经安装的包生成依赖包列文件
    pip freeze > requirements.txt
    #根据requirements.txt中列出的包安装依赖包
    pip install -r requirements.txt
2.#可以从环境中以kv的形式读取变量
    pip install --upgrade python-dotenv
3.__init__.py 的作用

    # 作为package的标示
    # 定义 __all__列表，用于模糊导入
4.创建数据库,会把已存在的数据库删掉
    # db.create_all()
    # db.drop_all()
    # db.create_all()

4.数据库迁移
    # 先要创建迁移仓库  python manage.py db init
    # 运行 >python manage.py db migrate -m"initial migration" 生成迁移脚本
    # 查看改动信息
    # 运行   >python manage.py db upgrade
6. 迁移数据库报错  sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) near "DROP": syntax error [SQL: 'ALTER TABLE roles DR
                    OP COLUMN suoxf']
    #解决办法 修改迁移脚本
        with op.batch_alter_table('roles') as batch_op:
                batch_op.drop_column('suoxf')

7.pip install forgerpy   生成虚拟数据

8.Pagedown 使用javas实现的客户端Markdown到html的转换程序
9.flask-pagedowm 把pagedown集成到flask-wtf表单中
10.Markdown  使用python实现的 服务器端markdown到html 的转换程序
11.bleach  使用python实现的html清理器