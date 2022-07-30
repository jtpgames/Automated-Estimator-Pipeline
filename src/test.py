from abc import abstractmethod, ABC

import pandas.io.sql as psql
import pandas as pd
from sqlalchemy import select, Table, Column, Integer, String, MetaData

from src.regression_analysis.configuration_handler import ConfigurationHandler
from src.regression_analysis.database import Database
from src.regression_analysis.features.list_parallel_command_finished_extractor import \
    ListParallelRequestsFinished


class AbstractClassTest(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    def greet(self) -> str:
        name = self.get_name()
        print("Hello {}".format(name))


class Test1(AbstractClassTest):
    def get_name(self) -> str:
        return "Adrian"

class Test2(AbstractClassTest):
    def get_name(self) -> str:
        return "Luke"

    def greet(self) -> str:
        print(self.get_name())

if __name__=="__main__":
    test1 = Test1()
    test2 = Test2()

    test1.greet()
    test2.greet()