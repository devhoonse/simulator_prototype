
from abc import *


class AbstractDataSource(metaclass=ABCMeta):
    """
    Abstract Class for Managing Connection to Database or File System
    """

    def __init__(self):
        self.connectionName: str = ""               # Connection Setting: "database" or "filesystem"

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
