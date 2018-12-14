#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: decorators.py.py
@time: 2018/11/01
"""

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission
#检查常规权限的装饰器
def permission_required(Permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(Permission):
                abort(403)
            return  f(*args,**kwargs)
        return decorated_function
    return  decorator

#检查管理员权限的装饰器
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)