#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: test.py
@time: 2018/10/22
"""
#把命令行解析功能添加到程序中  安装flask-script
from flask_script import Manager
#引入bootstrap
from flask_bootstrap import Bootstrap
from flask import Flask,request,make_response,g,render_template,session,redirect,url_for,flash
#render_template函数把jinja2模板引擎集成到了程序中，函数的第一个参数是模板的文件名，随后的参数是键值对，表示模板中变量对应的键值对

#使用flask-moment 本地化时间和日期
from flask_moment import Moment
#初始化及配置一个简单的 SQLite数据库
from flask_sqlalchemy import SQLAlchemy
#配置数据库迁移功能，不用每次修改数据库模型后重新创建数据库
from flask_migrate import Migrate,MigrateCommand
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime
app = Flask(__name__)
#设置秘钥，建立跨站请求伪造保护
app.config['SECRET_KEY'] = 'big big world'
#发送电子邮件
from flask_mail import Mail,Message

#配置163邮箱服务器
app.config.update(
    DEBUG = True,
    MAIL_SERVER='smtp.163.com',
    MAIL_PROT=25,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'lence0516@163.com',
    MAIL_PASSWORD = '13523424823sxf',
    MAIL_DEBUG = True
)

#发送邮件时，浏览器会有延迟无响应，修改为异步发送电子邮件

from threading import Thread
#实际开发中发送大量电子邮件时，我们可以把执行send_async_email()函数的操作发送给Celery任务队列
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

mail = Mail(app)

def send_email(sender,to,subject,template,**kwargs):
    #sender发送方，recipients 邮件接收方列表
    msg = Message(sender=sender,recipients=to,subject=subject)
    #body 邮件正文
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    #msg.attach 邮件附加添加     msg.attach(文件名，类型，读取文件)
    with app.open_resource('E:\home_work\content\images\\1539171481.8828568.jpg') as fp:
        msg.attach('meinv.jpg','image/jpg',fp.read())
    #异步发送电子邮件
    thr = Thread(target=send_async_email,args = [app,msg])
    thr.start()
    return thr
    # mail.send(msg)




@app.route('/',methods=['GET','POST'])
def index():
    """#flask使用上下文让特定的变量在一个线程中全局可访问
#线程是可单独管理的最小指令集，进程经常使用多个活动线程，有时还会共享内存和文件句柄等资源，多线程web服务器会创建一个线程池，再去线程池中选择一个线程用于处理接收到的请求
user_agent = request.headers.get("User-Agent")
#响应值可以是元祖形式，也可以是由 make_response生成的对象
return "<h1>hello world</h1><br/><p>your browser is %s</p>" % user_agent , 400
    # 使用模板引擎返回请求视图

    form = NameForm()
    if form.validate_on_submit():
        #解决如果post请求是客户端最后一个请求，刷新页面会再次请求的问题，使用重定向和用户会话
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have changed your name!!")

        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',current_time = datetime.utcnow(),form = form,name=session.get('name'))
    """
    ###在视图函数中操作数据库
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            #如果是第一次登陆系统，发送欢迎邮件
            send_email(sender="lence0516@163.com",to =['664471149@qq.com'],subject="Flsk-web 发送邮件测试",template='mail',name=form.name.data)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
                           form = form,name = session.get('name'),
                           known = session.get('known',False),current_time = datetime.utcnow())
# @app.route('/user/<name>')
# #app.route 是路由装饰器，用来将请求的URL与视图函数绑定
# #/static/<filename> 路由时Flask添加的特殊路由，用于访问静态文件
# def user(name):
#     response = make_response("<h1>hello, %s!</h1>" %name)
#     response.set_cookie('answer','42')
#     print(g)
#     return  response



#app.config 字典可用来存储框架、扩展和程序本身的配置变量，这个对象还提供了一些方法可以从文件或者环境中导入配置
bootstrap = Bootstrap(app)
manager = Manager(app)
moment = Moment(app)




#处理表单的库

from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required

#配置sqlite数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)  #db对象是SQLALchemy类的实例，表示程序使用的数据库，同时还获得了flask-sqlalchemy提供的所有功能
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)
print(__name__)

#定义数据库模型，模型这个术语表示程序使用的持久化实体，在orm中，模型一般是一个python类，类中的属性对应数据库表中的列
#定义 Role 和 user模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    #关联user表
    users = db.relationship("User",backref='role')

    def __repr__(self):
        return '<Role %r>' %self.name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True,index=True)
    #关联 role表
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username
# 为避免每次启动shell都要导入数据库实例和模型，配置让shell命令自动导入特定的对象
from flask_script import Shell

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))

#定义表单类
class NameForm(Form):
    name = StringField("what is your name ?",validators=[Required()])
    submit = SubmitField('Submit')




from flask import redirect  #请求重定向

@app.route('/other')
def redirectRequest():
    return  redirect('http://127.0.0.1:5000')  # 参数 location code response
    re
## abort 函数，用于处理错误，比如请求不存在,name  模拟用户
from flask import abort
@app.route('/user/<name>')
def check_user(name):
    """if name != 'lence':
        abort(404)
    return "hello %s" % name"""

    #使用模板引擎返回视图函数
    return render_template('user.html',name = name)



#自定义错误页面
@app.errorhandler(404)
def page_nat_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500





if __name__ == "__main__":
    manager.run()

"""
Flask 中有两种上下文 ： 程序上下文和请求上下文
current_app   程序上下文  当前激活程序的程序实例
g  程序上下文   处理请求时用作临时存储的对象，每次存储都会重新设定这个变量
request   请求上下文   请求对象，封装了客户端发出的HTTP请求中的内容
session  请求上下文   用户会话，用于存储请求直接需要“记住”的值的字典
"""
####falsk 请求钩子函数，在请求的不同阶段执行函数，求求钩子函数由装饰器实现
"""
1.before_first_request  注册一个函数，在处理第一个请求之前运行
2.before_request  在每次请求之前运行
3.after_request   如果没有未处理的异常抛出，在每次请求之后运行
4.teardown_request    即使有未处理的异常抛出，也在每次其你去之后运行

"""