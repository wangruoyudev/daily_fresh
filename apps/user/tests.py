# from django.test import TestCase

# Create your tests here.


print("******多继承使用类名.__init__ 发生的状态******")


class Parent(object):
    def __init__(self, name):
        print('parent的init开始被调用')
        self.name = name
        print('parent的init结束被调用')


class Son1(Parent):
    def __init__(self, name, age):
        print('Son1的init开始被调用')
        self.age = age
        Parent.__init__(self, name)
        print('Son1的init结束被调用')


class Son2(Parent):
    def __init__(self, name, gender):
        print('Son2的init开始被调用')
        self.gender = gender
        Parent.__init__(self, name)
        print('Son2的init结束被调用')


class Grandson(Son1, Son2):
    def __init__(self, name, age, gender):
        print('Grandson的init开始被调用')
        Son1.__init__(self, name, age)  # 单独调用父类的初始化方法
        Son2.__init__(self, name, gender)
        print('Grandson的init结束被调用')


Grandson('22', 12, 1)





class MixinView():
    @classmethod
    def as_view(cls):
        print('MixinView')
        view = super(View, cls).as_view() # 这里调用的其实是class View的as_view方法
        return view


class View():
    @classmethod
    def as_view(cls):
        print('View22222')


class ViewSon():
    @classmethod
    def as_view(cls):
        print('View33333')


class TestObject(MixinView, View, ViewSon):
    def get(self):
        print('1111')


TestObject.as_view()
print(TestObject.__mro__)


str1 = 'fsdfds1.sfs.fsd'
ls = str.split(str1, '.')
if len(ls) > 1:
    print(ls[-1])
else:
    print('null')

dic1 = dict()
dic1.update(a='2121212')
print(dic1)




