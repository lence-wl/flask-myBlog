#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: config.py.py
@time: 2018/10/25
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__)) #获取当前执行脚本的绝对路径

# 基类，包含通用配置
class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"    #从环境中读取秘钥
    SQLALCHEMY_TRACK_MODIFICATIONS = True # 该配置为True,则每次请求结束都会自动commit数据库的变动
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_FOLLOWERS_PER_PAGE = 10
    FLASKY_COMMENTS_PER_PAGE = 10
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    # os.environ.get 从系统的环境变量中读取相关字段
    DEBUG = True
    MAIL_DEBUG = True,
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PROT = 25,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #配置开发环境数据库地址
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


#配置测试环境数据库地址
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


#配置生产环境数据库地址
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or  'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,

}