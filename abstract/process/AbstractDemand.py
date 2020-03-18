
from abc import *


class AbstractDemand(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
