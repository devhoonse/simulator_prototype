
from abc import *


class AbstractDao(metaclass=ABCMeta):
    """
    Data Access Object
    실제 데이터를 들고 있는 클래스
    들고 있는 데이터의 종류에 따라 다르게 구현
        DemandDao   : Demand 관련 정보 데이터를 보관     (Demand)
        FactoryDao  : Factory 관련 정보 데이터를 보관    (Routing, BOD, BOM, PS 등)
    """

    # Dao 클래스 Static 변수들
    staticVar: object = None                # Comment

    # Dao 클래스 Static 상수들
    CONSTANT_VARIABLE: object = None        # Comment

    def __init__(self):
        """
        생성자 : Dao 클래스를 상속받는 자손 클래스들이 공통으로 가질 멤버 변수들
        """

        # 1. Public
        self.memberVar: object = None       # Comment

        # 2. Private
        self._privateVar: object = None     # Comment

    @abstractmethod
    def set_data(self):
        """
        Connection 인스턴스를 통해 get 데이터를 현재 Dao 인스턴스에 세팅하는 처리
        :return: void
        """
        pass

    @abstractmethod
    def get_data(self):
        """
        현재 Dao 인스턴스에 세팅된 데이터를 반환하는 처리
        :return: Array-like Object  ex: pandas.DataFrame / list<list> / ...
        """
        pass

    def get_private_var(self):
        """
        Private Variable Getter
        :return: self._privateVar.__class__
        """
        return self._privateVar

    def set_private_var(self, value: object):
        """
        Private Variable Value Setter
        :param value: self._privateVar.__class__
        :return: void
        """
        self._privateVar = value
