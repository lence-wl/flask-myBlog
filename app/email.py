#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: email.py.py
@time: 2018/10/25
"""
from flask_mail import Mail,Message
from threading import Thread
from flask import current_app,render_template
from manage import app
import os
#配置163邮箱服务
app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.163.com',
    MAIL_PROT=25,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='lence0516@163.com',
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_DEBUG=True
)
mail = Mail(app)
#实际开发中发送大量电子邮件时，我们可以把执行send_async_email()函数的操作发送给Celery任务队列
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(template,to,subject,**kwargs):
    sender = 'lence0516@163.com'
    subject = 'Flasky-test'
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
    #mail.send(msg)

