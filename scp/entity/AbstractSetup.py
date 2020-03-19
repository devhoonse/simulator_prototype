
from abc import *


class AbstractSetup(metaclass=ABCMeta):
    """

    """

    # Data Source 클래스를 상속받는 자손 클래스들이 공유할 Static 변수들
    staticVar: object = None

    def __init__(self):
        """
        생성자 :
        """
        pass

    @abstractmethod
    def do_something(self):
        pass

    @abstractmethod
    def do_my_thang(self):
        pass
