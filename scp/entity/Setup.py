
from abstract.manager.AbstractTimer import AbstractTimer
from abstract.entity.AbstractSetup import AbstractSetup


class Setup(AbstractTimer, AbstractSetup):

    def __init__(self):
        pass

    def doSomething(self):
        super().doSomething()

    def doMyThang(self):
        super().doMyThang()
