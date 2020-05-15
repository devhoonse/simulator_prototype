import sys
import datetime

from m4.process.Item import Item
from m4.operator.Runtime import Runtime


class Lot(Runtime):

    def __init__(self, item: Item, time_index: int, date: datetime.datetime, status: str, length: int = sys.maxsize):

        #  Runtime 들이 가지는 공통 변수들
        super().__init__(item, time_index, date, length)

        # Lot 만이 가지는 고유한 변수들
        self._status: str = status

    def process(self, time_index: int, date: datetime.datetime, status: str, length: int = sys.maxsize):

        super().reset(time_index, date, length)
        self._status = status

    def get_status(self):
        return self._status
