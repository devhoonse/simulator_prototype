from typing import Deque
import datetime

from m4.operator.Runtime import Runtime


class ProcessQueue(Deque[Runtime]):
    """
        [ ..., Runtime,... ]
    """

    def __init__(self):
        super(ProcessQueue, self).__init__()

        self._max_queue_size: int = 10

    def init(self, max_queue_size: int):
        self._max_queue_size = max_queue_size

    def put(self, lot: Runtime, time_index: int, date: datetime.datetime):
        if len(self) == self._max_queue_size:
            return False
        self.appendleft(lot)
        return True

    def run(self):
        for lot in self:
            lot.run()

    def get(self):
        return self[-1] if self.length() > 0 else None

    def fetch(self):
        return self.pop() if self.length() > 0 else None

    def length(self):
        return len(self)

    def get_available_size(self):
        return self._max_queue_size - self.length()

    def is_available(self) -> bool:
        return self.get_available_size() > 0

    def get_max_queue_size(self) -> int:
        return self._max_queue_size
