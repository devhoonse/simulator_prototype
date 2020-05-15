
import datetime

from m4.process.Item import Item
from m4.operator.Runtime import Runtime
from m4.operator.process.ProcessQueue import ProcessQueue


if __name__ == '__main__':

    queue: ProcessQueue = ProcessQueue()

    queue.put(lot=Runtime(item=Item(), time_index=0, date=datetime.datetime(2020, 4, 17, 1)))
    queue.put(lot=Runtime(item=Item(), time_index=1, date=datetime.datetime(2020, 4, 17, 2)))

    queue.run()

    queue.put(lot=Runtime(item=Item(), time_index=2, date=datetime.datetime(2020, 4, 17, 3)))
    queue.put(lot=Runtime(item=Item(), time_index=3, date=datetime.datetime(2020, 4, 17, 4)))
    queue.put(lot=Runtime(item=Item(), time_index=4, date=datetime.datetime(2020, 4, 17, 5)))

    queue.run()
    queue.run()

    r1: Runtime = queue.get()
    r1: Runtime = queue.fetch()

    queue.run()
    queue.run()
    queue.run()
    queue.run()
    queue.run()
    queue.run()
    queue.run()

    # items: list = []
    # while queue.has_items:
    #     items.append(queue.fetch())

    print("DEBUG POINT")
