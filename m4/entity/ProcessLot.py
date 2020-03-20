

class ProcessLot(object):
    """
    Process Lot Object
    Machine 객체에 종속되어 Machine 이 할당받은 Lot 을 처리하는 이벤트를 수행하는 클래스
    Setup 객체와 Lot 객체를 포함하며
    Machine 이 Lot 인스턴스를 처리할 때
    Machine 의 Setup Type 변경이 필요할 경우 이를 수행한 후에 하도록 설계
    """

    # Static Variables
    staticVar2: object = None  # Comment

    # Static Constants
    CONSTANT_VARIABLE2: object = None  # Comment

    def __init__(self):
        """

        """

        # 1. AbstractTimer 클래스에 정의된 멤버 변수들을 상속
        super().__init__()

        # 2-1. Public
        self.publicVar: object = None       # Comment

        # 2-2. Private
        self._privateVar: object = None     # Comment

    def do_something_else(self):
        """
        Write a New Code for this Method and Comment Here
        :return: void
        """
        pass
