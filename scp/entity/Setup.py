
from scp.manager.AbstractTimer import AbstractTimer


class Setup(AbstractTimer):

    def __init__(self):
        # 1. AbstractTimer 클래스에 정의된 멤버 변수들을 상속
        super().__init__()

        # 2. Setup 클래스만의 특수 멤버 변수들 선언
        # 2-1. Public
        self.fromType: str = ""     # 출발 Setup 타입
        self.toType: str = ""       # 목표 Setup 타입

        # 2-2. Private
