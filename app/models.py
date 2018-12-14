#!sur/bin/env python
#-*- coding:utf-8 -*-
"""
@author: lence
@file: models.py.py
@time: 2018/10/25
"""

#定义数据库模型，模型这个术语表示程序使用的持久化实体，在orm中，模型一般是一个python类，类中的属性对应数据库表中的列
#定义 Role 和 user模型

#在user模型中加入密码散列值
from werkzeug.security import generate_password_hash,check_password_hash
#使用flask_login库，支持用户登录
from flask_login import UserMixin,AnonymousUserMixin
#生成用来确认登录的加密令牌
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

from datetime import datetime
from . import db,login_manager
import hashlib
from flask import request

from markdown import markdown
import bleach

#用户角色模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    #用户注册后其角色设置为默认角色
    default = db.Column(db.Boolean,default=False,index=True)
    # 各个角色都对应一个permission标志位，能执行某项操作，其标志位会被设置为1
    # 操作          标志位值         说明
    """ 关注用户
        在他人的文章中发表评论   10
        写文章              100
        管理他人发表的评论  1000
        管理员权限           10000000
    """
    permissions = db.Column(db.Integer)
    #关联user表
    users = db.relationship("User",backref='role',lazy = 'dynamic')

    #添加角色的方法
    @staticmethod
    def insert_roles():
        roles = {
            'User':(
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLES, True),
            'Moderator':(
                Permission.FOLLOW |
                Permission.COMMENT |
                Permission.WRITE_ARTICLES |
                Permission.MODERATE_COMMENTS, False),
            'Adminstrator':(0xff,False)

        }
        for r in roles:
            role = Role.query.filter_by(name=r).first() #查看数据库中是有这个角色
            if role is None: # 没有再添加
                role = Role(name = r)   #往数据库中添加角色
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' %self.name
#权限表示
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80
"""
    用户角色及其使用的权限位

    匿名  0x00 未登录用户 只有阅读权限
    用户  0x07 发布文章 发表评论 关注其他用户 新用户角色
    协管员 0x0f 审查不当评论
    管理员 0xff 具有所有权限 包括修改其他用户所属角色的权限
"""
#实现关注关联表的模型
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow())


#用户信息模型
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    #定义默认的用户角色
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        # 构建用户时，把自己用户设置为自己的关注着


        if self.role is None:
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        #头像地址保存到数据库
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    # 支持用户登录,emial作为登录账号
    email = db.Column(db.String, unique=True, index=True)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 添加字段，丰富用户的资料信息
    name = db.Column(db.String(64))  # 真实姓名
    location = db.Column(db.String(64))  # 所在地
    about_me = db.Column(db.Text())  # 自我介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 注册日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 最后访问日期
    # 关联 role表
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    #生成头像
    avatar_hash = db.Column(db.String(32))
    #关联文章post表
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    ##使用两个一对多关系实行多对多关系，一种关系中用户为关注着，一种关系中用户为被关注着
    followed = db.relationship('Follow',
                               foreign_keys = [Follow.followed_id],
                               backref = db.backref('follower',lazy='joined'),
                               lazy = 'dynamic',
                               cascade = 'all,delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys = [Follow.follower_id],
                                #joined 实现立即从联结表中加载相关对象
                                #如果一个用户关注了一百个用户，调用user.followed.all()后会返回一个列表
                                #其中包含100个Follow实例，每一个follower和followed回引属性都指向相应的用户
                                backref = db.backref('followed',lazy='joined'),
                                lazy = 'dynamic',
                                #cascade 参数配置在父对象上执行的操作对相关对象的影响
                                cascade = 'all,delete-orphan')
    #关联评论字段
    comments = db.relationship('Comment', backref="author",lazy='dynamic')
    #关系关注的辅助方法

    #把follow实例插入关联表，关注着和被关注着关联起来
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower = self,followed = user)
            db.session.add(f)
            db.session.commit()
    #解除关注关系
    def unfollow(self,user):
        f = self.followed.filter_by(follower_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    #判断两个用户的是不是关注关系
    def is_following(self,user):
        if user.id is None:
            return False
        return self.followed.filter_by(follower_id=user.id).first() is not None
    def is_followed_by(self,user):
        if user.id is None:
            return False
        return self.followers.filter_by(followed_id = user.id).first() is not None
    #获取该用户所关注的用户的文章
    @property
    def followed_post(self):

        data = Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)
        print('+++++',data)
        return data
    #把用户设置为自己的关注者
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import InterfaceError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     location=forgery_py.address.city(),
                     name=forgery_py.name.full_name(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            # 可能生成重复的数据，则回滚丢弃这条数据，所以生成的数据可能比预期的少
            try:
                db.session.commit()
            except InterfaceError:
                db.session.rollback()
    #刷新用户的最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    # 检查用户是否有某项权限
    def can(self,permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions
    def is_administrator(self):
        return  self.can(Permission.ADMINISTER)
    #生成url头像地址
    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = "http://www.gravatar.com/avatar"
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url = url,hash=hash,size=size,default=default,rating=rating
        )
    def change_email(self,token):
        #...
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)




    @property  #可以将python定义的函数当做属性来访问
    def password(self):
        #读取时报错，手动改为不可读的属性
        raise ArithmeticError('password is not a readable attribute')

    @password.setter #同时有 password和x.setter表示可读可写
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return  check_password_hash(self.password_hash,password)

        def __repr__(self):
            return '<User %r>' % self.username
    #确认注册 生成加密令牌
    confirmed = db.Column(db.Boolean,default=False)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    def confirm(self,token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True



    class AnonymousUser(AnonymousUserMixin):
        def can(self, permissions):
            return False

        def is_administrator(self):
            return False

    login_manager.anonymous_user = AnonymousUser



#文章模型
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    #连接用户表的外键
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    #保存文章的html形式
    body_html = db.Column(db.Text)
    #关联评论
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    #把纯文本转换为html格式
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags =  ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,output_formate='html'),
            tags = allowed_tags,strip = True)
        )



    #生成文章模拟数据
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count - 1)).first() #获取随机用户
            p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),timestamp = forgery_py.date.date(True),author = u)
            db.session.add(p)
            db.session.commit()
#on_changed_body 注册在body字段上，只要body改变，这个韩阿叔就会被调用
db.event.listen(Post.body, 'set', Post.on_changed_body)

#comment 评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))
db.event.listen(Comment.body, 'set', Comment.on_changed_body)




#flask_login 要求程序实现一个回调函数，使用指定的标识符加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))