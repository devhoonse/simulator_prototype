
from scp.manager.AbstractTimer import AbstractTimer


class Lot(AbstractTimer):
    """

    """

    # Static Variables
    staticVar2: object = None           # Comment

    # Static Variables
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
