
from abc import *


class AbstractProcess(metaclass=ABCMeta):
    """
    Process Object
    Factory 에 정의된 각 Process(공정) 들의 상위 클래스
    공정 단계에 따라 다르게 구현
        Start Process   : 시작 단계 Process
        Process         : 중간 단계 Process
        End Process     : 완료 단계 Process
    """

    # Dao 클래스를 상속받는 자손 클래스들이 공유할 Static 변수들
    staticVar: object = None

    def __init__(self):
        """
        생성자 : Process 클래스를 상속받는 자손 클래스들이 공통으로 가질 멤버 변수들
        """
        self.memberVar1: object = None

    @abstractmethod
    def do_something(self):
        pass

    @abstractmethod
    def do_my_thang(self):
        pass
