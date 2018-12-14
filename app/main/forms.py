#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: forms.py.py
@time: 2018/10/25
"""
#处理表单的库

from flask_wtf import Form
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import Required,Length,Email,Regexp
from ..models import Permission, Role
from flask_pagedown.fields import PageDownField #启用markdown文章表单

#定义表单类
class NameForm(Form):
    name = StringField("what is your name ?",validators=[Required()])
    submit = SubmitField('Submit')


#资料编辑表单
class EditProfileForm(Form):
    name = StringField('Real name',validators=[Length(0,64)])
    location = StringField('Location',validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
#管理员使用的资料编辑表单
class EditProfileAdminForm(Form):
    email = StringField('Username',validators=[Required(),Length(1,64),Email()])
    username = StringField('Username',validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Username must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    #coerce 把选项的标识符转换为整数
    role = SelectField('Role',coerce=int)
    name = StringField('Real name',validators=[Length(1,64)])
    location = StringField('Location',validators=[Length(1,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField()

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        #列表解析语法,定义下拉列表的选项，是一个元祖的形式
        self.role.choices = [(role.id,role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and User.query.filter_by(email = filed.data).first():
            raise ValueError('Email already registered')

    def validate_username(self,field):
        if field.data != self.user.username and User.query.filter_by(username = field.data).first():
            raise ValueError('Username already in use')
#博客文章表单
class PostForm(Form):
    body = PageDownField("what's your mind?",validators=[Required()])
    submit = SubmitField('Submit')

#评论表单
class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')




