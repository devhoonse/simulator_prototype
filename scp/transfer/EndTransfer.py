from scp.transfer.AbstarctTransfer import AbstractTransfer


class EndTransfer(AbstractTransfer):
    """
    End Transfer Object
    Lot 을 마지막 종착지로 보내는 이벤트를 담당
    """

    # Static 변수들
    staticVar2: object = None           # Comment

    # Static Constants
    CONSTANT_VARIABLE2: object = None   # Comment

    def __init__(self):
        super().__init__()

        # 1. Public
        self.memberVar1: object = None

        # 2. Private
        self._privateVar: object = None

    def pick_finished_lot(self):
        pass

    def transfer_lot(self):
        pass
