#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: __init__.py.py
@time: 2018/10/28
"""
from flask import Blueprint



auth = Blueprint('auth',__name__)

from . import views