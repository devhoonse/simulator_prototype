
from abc import *


class AbstractSetup(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    def __init__(self):
        pass

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
