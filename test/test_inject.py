import unittest
import time
import threading

from mock import patch, Mock

from hutils.inject import (require,
                           Registry,
                           Dependency,
                           LazyDependency,
                           DynamicDependency,
                           InjectException)


class TestInject(unittest.TestCase):

    def test_dependency_not_found(self):
        @require('not_existent_dependency')
        class A(object): pass

        Registry().install()

        with self.assertRaises(InjectException):
            A().not_existent_dependency

    def test_default_name(self):
        @require('my_component', 'component', 'my_func')
        class A(object): pass
        class MyComponent(object): pass
        class Component(object): pass
        def my_func(): pass

        my_component = MyComponent()
        Registry(
            Dependency(my_component),
            LazyDependency(Component),
            Dependency(my_func)
        ).install()

        a = A()
        self.assertIs(a.my_component, my_component)
        self.assertIsInstance(a.component, Component)
        self.assertIs(a.my_func, my_func)

    def test_manual_setter_injection(self):
        @require('b')
        class A(object): pass
        a = A()
        a.b = 1
        self.assertEqual(a.b, 1)

    def test_manual_constructor_injection(self):
        @require('b')
        class A(object): pass
        a = A(b=1)
        self.assertEqual(a.b, 1)

    def test_pertarget_lazy_dependency(self):
        @require('b', 'c')
        class A(object): pass
        class B(object):
            def b(self): pass
        class C(object):
            def c(self): pass

        Registry(LazyDependency(B, pertarget=True, name='b'),
                 LazyDependency(C, pertarget=True, name='c')
        ).install()

        a = A()
        a.b.b()
        a.c.c()

    def test_lazy_dependency(self):
        @require('tt', 'tf', 'ft', 'ff')
        class A(object): pass
        class B(object): pass

        Registry(
            LazyDependency(B, name="tt", perthread=True, pertarget=True),
            LazyDependency(B, name="tf", pertarget=True),  # perthread=False
            LazyDependency(B, name="ft", perthread=True),  # pertarget=False
            LazyDependency(B, name="ff")  # pertarget=False, perthread=False
        ).install()

        a1 = A()
        a2 = A()

        tt11 = a1.tt
        tt11.x = 11
        tt12 = a2.tt
        tt12.x = 12
        def onthread():
            tt21 = a1.tt
            tt21.x = 21
            self.assertIsInstance(tt11, B)
            self.assertIsInstance(tt21, B)
            self.assertIsNot(tt11, tt21)
            self.assertEqual(tt11.x, 11)
            self.assertEqual(tt21.x, 21)
            tt22 = a2.tt
            tt22.x = 22
            self.assertIsInstance(tt12, B)
            self.assertIsInstance(tt22, B)
            self.assertIsNot(tt12, tt22)
            self.assertEqual(tt12.x, 12)
            self.assertEqual(tt22.x, 22)
        threading.Thread(target=onthread).start()

        a1.tf.x = 1
        a2.tf.x = 2
        self.assertIsInstance(a1.tf, B)
        self.assertIsInstance(a2.tf, B)
        self.assertIsNot(a1.tf, a2.tf)
        self.assertEqual(a1.tf.x, 1)
        self.assertEqual(a2.tf.x, 2)

        ft1 = a1.ft
        ft1.x = 1
        def onthread():
            ft2 = a1.ft
            ft2.x = 2
            self.assertIsInstance(ft1, B)
            self.assertIsInstance(ft2, B)
            self.assertIsNot(ft1, ft2)
            self.assertEqual(ft1.x, 1)
            self.assertEqual(ft2.x, 2)
        threading.Thread(target=onthread).start()

        a1.ff.x = 1
        self.assertIsInstance(a1.ff, B)
        self.assertIs(a1.ff, a2.ff)
        self.assertEqual(a1.ff.x, 1)

    def test_merge(self):
        @require('x', 'y', 'z')
        class A(object):
            pass

        Registry(
            Dependency(1, name='x')
        ).install()
        self.assertEqual(A().x, 1)

        Registry(
            Dependency(2, name='y')
        ).install(merge=True)
        self.assertEqual(A().x, 1)
        self.assertEqual(A().y, 2)

        Registry(
            Dependency(3, name='z')
        ).install()
        self.assertRaises(Exception, lambda: A().x)
        self.assertRaises(Exception, lambda: A().y)
        self.assertEqual(A().z, 3)

    def test_dynamic_dependency(self):
        @require('foo')
        class A(object):
            pass
        foo = Mock()
        Registry(
            DynamicDependency(foo, name='foo')
        ).install()
        a = A()
        a.foo
        a.foo
        self.assertEqual(foo.call_count, 2)
