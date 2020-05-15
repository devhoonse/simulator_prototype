import math
import sys
import datetime
from typing import List

from m4.constraint.AbstractConstraint import AbstractConstraint
from m4.operator.Resource import Resource
from m4.operator.process.ProcessLot import ProcessLot
from m4.process.Item import Item


class ProcessResource(object):
    """
    Process Resource Object
    각 공정 단계 별 생산 장비를 구현한 클래스
    Process 에 종속되며
    Route 로부터 자신이 속한 Process 에 작업이 할당되었을 경우
    실제 처리 동작을 수행하도록 설계
    """

    def __init__(self):
        """
        생성자 :
        """

        # 2-1. Public
        self.process_id: str = ""                       # Process ID
        self.resource_id: str = ""                      # Resource ID
        self.name: str = ""                             # BOR 명칭

        # 2-2. Private
        self._resource: Resource = None
        self._priority: int = 0
        self._production_efficiency: float = 0.0
        self._process_precision: int = 0    # 산출량 계산 시 round 자리수, 0이면 정수부만 남김
        self._min_lot_size: float = 0.0
        self._max_lot_size: float = 0.0
        self._unit_lot_size: float = 0.0
        self._process_time: int = 0
        self._setup_time: int = 0
        self._use_backward_size: bool = True

        self._process_lot: ProcessLot = ProcessLot()        # Resource 의 실제 작업을 수행하는 객체

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.resource_id} at {hex(id(self))}>"

    def init(self, info: dict, resource: Resource, use_backward_size: bool):
        """

        :param use_backward_size:
        :param info:
        :param resource:
        :return:
        """

        self.process_id = info['PROC_ID']
        self.resource_id = info['RESC_ID']
        self.name = info['BOR_NM']

        self._process_lot.init(info=info)

        self._resource = resource
        self._priority: int = info['PRIORITY']
        self._process_precision = info['PROC_PRECSN']

        # 생산 효율
        self._production_efficiency = info['PROD_EFFCNCY']

        # Capacity Constraints
        self._min_lot_size = info['MIN_LOT_SIZE']
        self._max_lot_size = sys.float_info.max if info['MAX_LOT_SIZE'] in [None, 0] else info['MAX_LOT_SIZE']
        self._unit_lot_size = info['UNIT_LOT_SIZE']

        # Resource 의 Default 소요 시간 설정, Item 에 지정 값이 있을 경우 사용하지 않음
        self._process_time: int = info['PROC_TM']
        self._setup_time: int = info['PRE_PROC_SETUP_TM']

        # Backward 에서 세팅되어 넘어온 설정 값을 그대로 사용할 지 Boolean 옵션 설정
        self._use_backward_size = use_backward_size

    def is_available(self, date: datetime.datetime, item_id: str, product_quantity: float, move_time: int):
        """

        :return:
        """
        # Todo: Check - self._resource.check() && self._process_lot.is_available() && self._constraints.check()

        # 1. Resource 가 일정 제약에 걸리는 지 확인
        # 2. 할당 가능 Lot Size 인지 확인
        #       - min / max Capa 에 들어오는지
        #       - unit_lot_size 의 배수인지
        # 3. 아이템
        input_quantity: float = self.calculate_available_input_quantity(product_quantity)
        _is_available: bool = \
            self._resource.check(date=date) is None and \
            self._min_lot_size <= input_quantity <= self._max_lot_size and \
            product_quantity % self._unit_lot_size == 0 and \
            self._process_lot.is_available(date=date, item_id=item_id,
                                           quantity=product_quantity, move_time=move_time)
        return _is_available, input_quantity

    def put(self, time_index: int, date: datetime.datetime, item: Item, move_time: int):

        item.set_setup_time(self._setup_time)
        item.set_process_time(self._get_process_time(item))

        # Todo min_lot_size, max_lot_size process_precision  처리
        # quantity: float = item.get_required_quantity() * self.set_production_efficiency()
        # item.set_quantity(quantity)

        item.set_location_id(self.resource_id)
        self._process_lot.put(time_index=time_index, date=date, item=item, move_time=move_time)

    def run(self, time_index: int, date: datetime.datetime, is_off_day: bool, off_day_type: str,
            factory_const: AbstractConstraint):
        """

        :return:
        """
        # Todo: Work Divisibility (Y/N/I Type) 반영
        if is_off_day or factory_const:     # 공장 일정 제약에 걸리는 경우
            self._process_lot.not_run(date)
        elif self._resource.check(date) is not None:    # Resource 일정 제약에 걸리는 경우
            self._process_lot.not_run(date)
        else:
            self._process_lot.run(time_index, date, is_off_day, off_day_type)

    def fetch(self, time_index: int, date: datetime.datetime, item_id: str, work_order_id: str, quantity: float):
        return self._process_lot.fetch(time_index=time_index,
                                       date=date,
                                       item_id=item_id,
                                       work_order_id=work_order_id,
                                       quantity=quantity)

    def _calculate_output_quantity(self, input_quantity: float):
        return input_quantity / self._production_efficiency

    def calculate_available_input_quantity(self, required_quantity: float):
        if required_quantity == 0:
            return required_quantity
        return min([
            max([
                self._calculate_upper_input_quantity(required_quantity),
                self._calculate_lower_input_quantity(self._min_lot_size)
            ]),
            self._calculate_lower_input_quantity(self._max_lot_size)
        ])

    def _calculate_upper_input_quantity(self, required_quantity: float):
        return round(
            self._unit_lot_size *
            (int(required_quantity // self._unit_lot_size) +
             int(required_quantity % self._unit_lot_size > 0)) / self._production_efficiency,
            self._process_precision
        )

    def _calculate_lower_input_quantity(self, required_quantity: float):
        return round(
            self._unit_lot_size *
            (int(required_quantity // self._unit_lot_size)) / self._production_efficiency,
            self._process_precision
        )

    def _get_process_time(self, item: Item) -> float:
        """
        Item 사이즈에 따른 처리 소요 시간 계산
        process_time = item_size (t) / process_rate (t/h)
        # Todo: Ceil 필요 여부 확인 필요
        :param item:
        :return:
        """
        return math.ceil(item.get_quantity() / self._process_time)

    def get_quantity(self, item_id: str, work_order_id: str):
        return self._process_lot.get_quantity(item_id, work_order_id)

    def get_wait_quantity(self, item_id: str, work_order_id: str):
        return self._process_lot.get_wait_quantity(item_id=item_id,
                                                   work_order_id=work_order_id)

    def get_min_lot_size(self):
        return self._min_lot_size

    def get_max_lot_size(self):
        return self._max_lot_size

    def get_priority(self) -> int:
        return self._priority

    def get_items(self, item_id: str, work_order_id: str) -> List[Item]:
        return self._process_lot.get_wait_items(item_id=item_id, work_order_id=work_order_id)

    def get_process_precision(self):
        return self._process_precision

    def set_priority(self, priority: int):
        self._priority = priority

    def set_production_efficiency(self, production_efficiency: float):
        self._production_efficiency = production_efficiency

    def set_process_precision(self, process_precision: float):
        self._process_precision = process_precision

    def set_min_lot_size(self, min_lot_size: float):
        self._min_lot_size = min_lot_size

    def set_max_lot_size(self, max_lot_size: float):
        self._max_lot_size = max_lot_size

    def set_process_time(self, process_time: float):
        self._process_time = process_time

    def set_setup_time(self, setup_time: float):
        self._setup_time = setup_time

    def get_resource_history(self):
        return self._process_lot.get_history()

    @property
    def status(self):
        return self._process_lot.status
