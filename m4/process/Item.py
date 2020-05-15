import datetime
import copy


class Item(object):

    def __init__(self):
        # 기본 속성
        self.item_id: str = ''
        self.location_id: str = ''
        self._quantity: float = 0

        # 주문 정보 추가 속성
        self.work_order_id: str = ''
        self.order_item_id: str = ''
        self._order_quantity: float = 0             # Order Item의 Order 주문 수량
        self._required_quantity: float = 0          # 현 시점의 생산 요구 수량
        self._peg_quantity: float = 0               # 재고/재공의 경우 Pegging 수량
        self._due_date: datetime.datetime = None

        # Lot 처리 속성
        self._setup_time = 0
        self._process_time = 0
        self._lpst: datetime.datetime = None
        self._priority: int = -1

        # runtime 처리 속성
        # 이전 단계 수량 조합 (product, stock, wip)

        # 이력 관련 속성
        self._history: list = []
        self._merged_items: list = []

    def __eq__(self, other) -> bool:
        """
        인스턴스 주소 값이나 쌓인 history 가 달라도 나머지 속성들이 서로 일치하면 같은 것으로 간주
        Inventory.set_backward_peg_items( ) 메서드에서 _stock 재고 Item 에 대한 처리를 구분하기 위함
        :param other: Item
        :return: bool
        """
        eq: bool = \
            isinstance(other, self.__class__) and \
            {attr: val for attr, val in self.__dict__.items() if attr != '_history'} \
            == {attr: val for attr, val in other.__dict__.items() if attr != '_history'}
        return eq

    def init(self,
             item_id: str, location_id: str, quantity: float,
             work_order_id: str, order_item_id: str,
             order_quantity: float = 0, req_quantity: float = 0, peg_quantity: float = 0,
             due_date: datetime.datetime = None, setup_time: int = 0, process_time: int = 0,
             lpst: datetime.datetime = None, priority: int = -1):

        # 기본 속성 setting
        self.item_id = item_id
        self.location_id = location_id
        self._quantity = quantity                   # 현재 수량

        # 주문 정보 추가 속성 setting
        self.work_order_id = '' if work_order_id is None else work_order_id
        self.order_item_id = '' if order_item_id is None else order_item_id
        self._order_quantity = order_quantity       # work order 주문 수량 (과정 중에 변하지 않음)
        self._required_quantity = req_quantity      # 현재 위치에서 생산해야할 총 수량
        self._peg_quantity = peg_quantity           # 현재 위치에서 Peg 될 수량

        # Lot 처리 속성
        self._due_date = due_date
        self._setup_time = setup_time
        self._process_time = process_time
        self._lpst = lpst
        self._priority = priority

    def cut(self, time_index: int, date: datetime.datetime, location: str, quantity: float):
        new_item: Item = copy.deepcopy(self)
        new_item.set_quantity(quantity)
        new_item.archive(time_index, date, 'CUT', location)
        self.set_quantity(self._quantity - quantity)
        return new_item

    def archive(self, time_index: int, date: datetime.datetime, action: str, location: str):
        history: dict = {
            'TIME_INDEX': time_index,
            'DATE': date,
            'ACTION': action,
            'LOCATION': location,
            'WORK_ORDER': self.work_order_id,
            'QTY': self._quantity
        }
        self._history.append(history)

    def is_peg_info_appended_to(self, other) -> bool:
        """
        인스턴스 주소 값이나 쌓인 history 가 달라도 나머지 속성들이 서로 일치하면 같은 것으로 간주
        Inventory.set_backward_peg_items( ) 메서드에서 _stock 재고 Item 에 대한 처리를 구분하기 위함
        :param other: Item
        :return: bool
        """
        exceptional_attributes: list = ['_history', 'order_item_id', 'work_order_id', '_lpst',
                                        '_peg_quantity', '_required_quantity']
        eq: bool = \
            isinstance(other, self.__class__) and \
            {attr: val for attr, val in self.__dict__.items() if attr not in exceptional_attributes} \
            == {attr: val for attr, val in other.__dict__.items() if attr not in exceptional_attributes}
        return eq

    def append_merged_item(self, item):
        self._merged_items.append(item)

    def get_order_item_id(self):
        return self.order_item_id

    def get_item_id(self):
        return self.item_id

    def get_work_order_id(self):
        return self.work_order_id

    def set_work_order_id(self, work_order_id: str):
        self.work_order_id = work_order_id

    def set_item_id(self, item_id: str):
        self.item_id = item_id

    def set_location_id(self, location_id: str):
        self.location_id = location_id

    def get_quantity(self) -> float:
        return self._quantity

    def set_quantity(self, quantity: float):
        self._quantity = quantity

    def get_due_date(self):
        return self._due_date

    def set_due_date(self, due_date: float):
        self._due_date = due_date

    def get_setup_time(self):
        return self._setup_time

    def set_setup_time(self, time: int):
        self._setup_time = time

    def get_process_time(self):
        return self._process_time

    def set_process_time(self, time: int):
        self._process_time = time

    def set_src_quantity(self, src_quantity: tuple):
        self._src_quantity = src_quantity

    def get_required_quantity(self):
        return self._required_quantity

    def set_required_quantity(self, quantity: float):
        self._required_quantity = quantity

    def get_order_quantity(self):
        return self._order_quantity

    def get_peg_quantity(self):
        return self._peg_quantity
