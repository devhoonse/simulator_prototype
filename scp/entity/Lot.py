
from abstract.manager.AbstractTimer import AbstractTimer
from abstract.entity.AbstractProcessLot import AbstractProcessLot


class Lot(AbstractTimer, AbstractProcessLot):

    def __init__(self):
        pass

    def doSomething(self):
        super().doSomething()

    def doMyThang(self):
        super().doMyThang()
