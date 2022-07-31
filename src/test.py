from abc import ABC, abstractmethod


class BaseClass(ABC):
    def __init__(self, name):
        self.__name = name
        pass

    def test(self):
        print("base")


class Child1(BaseClass):
    def test(self):
        print("child1")


class Child2(BaseClass):
    pass


child1 = Child1
child2 = Child2
child1.test("test")
child2.test("test")
