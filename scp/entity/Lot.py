
from scp.manager.AbstractTimer import AbstractTimer


class Lot(AbstractTimer):
    """
    Lot Object
    정의된 공정을 흘러가는 Lot 객체 클래스
    Machine, Warehouse 에 할당되어 처리 소요 시간이 모두 경과된 후에 다음 공정으로 넘어가는 이벤트 구현을 위해
    Timer 클래스를 상속
    """

    # Static Variables
    staticVar2: object = None           # Comment

    # Static Constants
    CONSTANT_VARIABLE2: object = None   # Comment

    def __init__(self):
        """

        """

        # 1. AbstractTimer 클래스에 정의된 멤버 변수들을 상속
        super().__init__()

        # 2-1. Public
        self.id: str = ""               # Lot 일련번호
        self.prodCode: str = ""         # Lot 제품번호
        self.dueDate: object = ""       # Lot 납기일 : Type ?? datetime ? int ?
        self.qty: float = 0.0           # Lot 수량

        # 2-2. Private

    def do_something_else(self):
        """
        Write a New Code for this Method and Comment Here
        :return: void
        """
        pass
