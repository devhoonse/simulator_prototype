
from abc import *


class AbstractFactoryManager(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
