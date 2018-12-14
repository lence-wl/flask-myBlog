#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: views.py
@time: 2018/10/28
"""
from flask import render_template,redirect,request,url_for,flash
from . import auth
from flask_login import login_required,login_user,logout_user  #用来保护路由，只让通过认证的用户访问，否则把用户发往登录页面
from .forms import LoginForm
from . import auth
from ..models import User
from .forms import LoginForm
from .forms import RegistrationForm
from ..import db

from ..email import send_email


@auth.route('/login',methods=['GET','POST'])
# 这个视图函数创建了一个 LoginForm 对象，当请求是GET类型时，视图函数直接渲染模板显示登录的表单，当
# 表单在POST中提交时，Flask-WTF中的 validate_on_submit() 函数会验证表单数据，尝试登入用户
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data) #若用户名和密码验证通过，login_user函数把用户在会话中标记为已登录
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return  render_template('auth/login.html',form = form)
#更新已登录用户的访问时间
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
#登出路由
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))
#新用户注册路由
@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,
                    username = form.username.data,
                    password = form.passWord.data)
        db.session.add(user)
        db.session.commit()
        subject = 'Flasky-register'
        token = user.generate_confirmation_token()
        send_email('auth/email/confirm',to=[user.email],user=user,token=token,subject=subject)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

#确认账户的路由视图函数
from flask_login import current_user

@auth.route('/confirm/<token>')
@login_required
def confirm(token):

    if current_user.confirmed:
        return  redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your count. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return  redirect(url_for('main.index'))


#在before_app_request处理程序中过滤未确认的账户
@auth.before_app_request
def before_request():
    if current_user.is_authenticated  and not current_user.confirmed  and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/auth/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

#重新发送账户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    subject = 'Flasky-register'
    send_email('auth/email/confirm', to=[current_user.email], user=current_user, token=token, subject=subject)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))



#路由保护视图
@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated user are allowed !'

