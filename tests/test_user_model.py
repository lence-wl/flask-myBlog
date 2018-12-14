import unittest
from app.models import User

class UserModelTestCase(unittest.TestCase):
    #判断是否会根据密码值生成 哈希散列值
    def test_password_setter(self):
         u = User(password = 'dog')
         self.assertTrue(u.password_hash is not None)

    # 判断密码字段是不是只写字段
    def test_no_password_getter(self):
        u = User(password = 'dog')
        with self.assertRaises(AttributeError):
            u.password
    #判断密码校验是否生效,第一个校验为True 第二个校验为false
    def test_password_verifycation(self):
        u = User(password = "dog")
        self.assertTrue(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cat'))
    #判断两个密码相同时，散列值是否相同
    def test_password_salts_are_random(self):
        u = User(password = 'cat')
        u2 = User(password = 'cat')
        self.assertTrue(u.password_hash != u2.password_hash)
    #角色和权限的单元测试
    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email = 'john@example.com',password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))