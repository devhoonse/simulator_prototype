import datetime


class WorkOrder(object):
    """
    Work Order Object
    """
    def __init__(self):
        # 기본 속성
        self.id: str = ''
        self.order_item_id: str = ''
        self.priority: int = -1
        self.detail_priority: int = -1
        self.order_quantity: float = 0             # Order Item의 Order 주문 수량
        self.due_date: datetime.datetime = None
        self.location_id: str = ''

    def init(self, info: dict):
        self.id = info["WORK_ORDER_ID"]
        self.order_item_id = info["ORDER_ITEM_ID"]
        self.priority = info["PRIORITY"]
        self.detail_priority = info["DTL_PRIORITY"]
        self.order_quantity = info["ORDER_QTY"]
        self.due_date = info["DUE_DT"]
        self.location_id = info["LOC_ID"]

