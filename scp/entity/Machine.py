
from scp.entity.Lot import Lot
from scp.entity.MachineSetup import MachineSetup


class Machine(object):

    def __init__(self):

        # 2. Lot 클래스만의 특수 멤버 변수들 선언
        # 2-1. Public
        self.id: str = ""                   # Machine 일련번호
        self.status: str = ""               # Machine 의 현재 상태. PROC / IDLE / DOWN
        self.setup: MachineSetup = None     # Machine 이 현재

        # 2-2. Private : getter 및 setter 를 통해서만 제어하도록
        self.lot: Lot = None                # Machine 이 현재 처리 중인 Lot. 없으면 None

    def do_something(self):
        pass

    def do_my_thang(self):
        pass
