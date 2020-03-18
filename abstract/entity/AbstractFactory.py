
from abc import *


class AbstractFactory(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
