
from abc import *

from .AbstractDataSource import AbstractDataSource


class AbstractDao(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    def __init__(self):
        self.dataSource: AbstractDataSource = None

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
