
from abc import *


class AbstractConstraint(metaclass=ABCMeta):
    """
    각종 제약 조건들의 처리를 담당하는 Constraint 클래스 들의 상위 클래스
    이벤트를 관장하는 Transfer 인스턴스가 이벤트를 결정할 때 참고하도록
    처리할 제약 조건의 종류에 따라 Constraint 클래스가 구분됨
        - CapaConstraint    : Capacity (일별 보관 가능량 혹은 처리 가능량)에 관한 제약을 담당
        - TimeConstraint    : Time (가동 불가 시간 등)에 관한 제약을 담당
    """

    # Constraint 클래스를 상속받는 자손 클래스들이 공유할 Static 변수들
    staticVar: object = None

    def __init__(self):
        """
        생성자 : Constraint 클래스를 상속받는 자손 클래스들이 공통으로 가질 멤버 변수들
        """

        # 1. Public
        self.memberVar1: object = None

        # 2. Private
        self._privateVar: object = None

    @abstractmethod
    def do_something(self):
        pass

    @abstractmethod
    def do_my_thang(self):
        pass
