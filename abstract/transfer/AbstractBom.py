
from abc import *


class AbstractBom(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
