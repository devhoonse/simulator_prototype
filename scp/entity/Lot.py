
from scp.manager.AbstractTimer import AbstractTimer


class Lot(AbstractTimer):

    def __init__(self):

        # 1. AbstractTimer 클래스에 정의된 멤버 변수들을 상속
        super().__init__()

        # 2. Lot 클래스만의 특수 멤버 변수들 선언
        # 2-1. Public
        self.id: str = ""           # Lot 일련번호
        self.prodCode: str = ""     # Lot 제품번호
        self.dueDate: object = ""   # Lot 납기일 : Type ??
        self.qty: float = 0.0       # Lot 수량

        # 2-2. Private

