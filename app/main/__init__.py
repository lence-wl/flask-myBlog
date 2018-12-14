#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: __init__.py.py
@time: 2018/10/25
"""
from flask import Blueprint
#__name__ 是包的名字，__main__
main = Blueprint('main',__name__)
from . import views,errors

# 把Permission类加入模板上下文
from ..models import Permission
@main.app_context_processor
def inject_permissions():
    return dict(Permission =Permission)