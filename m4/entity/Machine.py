
from m4.entity.Lot import Lot
from m4.entity.MachineSetup import MachineSetup


class Machine(object):
    """
    Machine Object

    """

    def __init__(self):

        # 2. 멤버 변수
        # 2-1. Public
        self.id: str = ""                   # Machine 일련번호
        self.status: str = ""               # Machine 의 현재 상태. PROC / IDLE / DOWN
        self.setup: MachineSetup = None     # Machine 의 작업에 필요한 정보들만 모은 객체

        # 2-2. Private : getter 및 setter 를 통해서만 제어하도록
        #              : 값 직접 할당문 사용 금지
        #              : e.g. self._privateVar = value
        self._lot: Lot = None               # Machine 이 현재 처리 중인 Lot. 없으면 None

    def do_something(self):
        pass

    def do_something_else(self):
        pass
