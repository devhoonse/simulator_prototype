
from abc import *


class AbstractConstraint(metaclass=ABCMeta):

    varOne: object = ""
    varTwo: object = ""

    def __init__(self):
        self.memberVar1: object = None

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
