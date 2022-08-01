from abc import ABC, abstractmethod


class BaseClass(ABC):
    def __init__(self):
        pass

    def test(self):
        print("base")

    def get_bla(self):
        print("get_bla")


class Child1(BaseClass):
    def test(self):
        print("child1")

    def call_get_bla(self):
        return self.get_bla()


class Child2(BaseClass):
    pass


child1 = Child1()
child2 = Child2()
child1.get_bla()

