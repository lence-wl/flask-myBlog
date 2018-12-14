#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: test.py
@time: 2018/10/22
"""
from flask import Flask,request,make_response,g,render_template,session,redirect,url_for,flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from config import config

from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from datetime import datetime
from flask_mail import Mail,Message
from threading import Thread
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask import redirect  #请求重定向
from flask_pagedown import PageDown #支持富文本markdown

pagedown = PageDown()


# from .models import Permission
db = SQLAlchemy()

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()




#支持用户登录
from flask_login import LoginManager
login_manager = LoginManager()
#可以设置为 None \ basic \ strong 已提供不同的安全等级防止用户的会话早篡改
#设置为strong时，flask_login会记录客户端的Ip地址和浏览器对的代理信息，发现异常就登出
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['MAIL_DEBUG'] = 1   #跳过报错
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    #初始化 flask_login
    login_manager.init_app(app)

    #附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # 把auth蓝本附加到app主程序上
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')


    return app


































