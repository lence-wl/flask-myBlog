#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: forms.py
@time: 2018/10/28
"""
from flask_wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
#用户登录表单
class LoginForm(Form):
    email = StringField("Email",validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('Log In')

#用户注册表单
from wtforms import ValidationError
from ..models import User

class RegistrationForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
                                                    #正则验证，只含有字母 数字 下划线  点号                           #验证失败时显示的信息
    username = StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'username must have only letters, '
                                                 'numbers, dots or underscores')])
    passWord = PasswordField('password',validators=[Required(),EqualTo('password2',message="password must match")])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')





















