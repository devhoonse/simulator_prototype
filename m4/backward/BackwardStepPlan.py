import datetime


class BackwardStepPlan(object):

    def __init__(self):
        self.step: int = 0
        self.item_id: str = ''
        self.location_id: str = ''
        self.to_location_id: str = ''
        self.plant_id: str = ''

        self.work_order_id: str = ''
        self.order_item_id: str = ''
        self.order_quantity: int = 0
        self.required_quantity: int = 0
        self.peg_quantity: int = 0

        #
        self.due_date: datetime.datetime = None
        self.lpst: datetime.datetime = None
        self.priority: int = -1

    def init(self,
             work_order_id: str,
             finished_item_id: str,
             work_order_qty: int,
             remain_production_qty: int,
             step: int,
             item_id: str,
             location_id: str,
             to_location_id: str,
             due_date: datetime.datetime,
             lpst: datetime.datetime):

        self.work_order_id = work_order_id
        self.order_item_id = finished_item_id
        self.item_id = item_id
        self.step = step
        self.location_id = location_id
        self.to_location_id = to_location_id
        self.order_quantity = work_order_qty
        self.required_quantity = remain_production_qty
        self.due_date = due_date
        self.lpst = lpst

    def peg(self, peg_qty: int):
        self.peg_quantity = peg_qty
        self.required_quantity = round(self.required_quantity - peg_qty, 3)     # Todo: Hard Coded - 자릿수
