
from abc import *

from scp.process.AbstractProcess import AbstractProcess
from scp.entity.Lot import Lot


class AbstractTransfer(metaclass=ABCMeta):
    """
    시뮬레이션에서 이벤트 발생을 담당하기 위한 상위 Transfer 클래스
    담당 이벤트 종류에 따라 Transfer 클래스가 구분됨
        - InitialTransfer   : Lot 을 처음 시작지로부터 출발시키는 이벤트를 담당
        - WarehouseTransfer : Initial 과 End 사이 시점에서 Lot 을 Warehouse 로 보내는 이벤트를 담당
        - MachineTransfer   : Initial 과 End 사이 시점에서 Lot 을 Machine 으로 보내는 이벤트를 담당
        - EndTransfer       : Lot 을 마지막 종착지로 보내는 이벤트를 담당
    """

    # Transfer 클래스를 상속받는 자손 클래스들이 공유할 Static 변수들
    staticVar: object = None

    # Transfer 클래스 Static Constants
    CONSTANT_VARIABLE: object = None

    def __init__(self):
        """
        생성자 : Transfer 클래스를 상속받는 자손 클래스들이 공통으로 가질 멤버 변수들
        """

        # 1. Public
        self.Id: str = ""

        # 2. Private
        self._fromProcess: AbstractProcess = None   #
        self._finishedLot: Lot = None               #
        self._toProcess: AbstractProcess = None     #
        self._privateVar: object = None             #

    @abstractmethod
    def pick_finished_lot(self):
        """

        :return: void
        """
        pass

    @abstractmethod
    def transfer_lot(self):
        """

        :return: void
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
