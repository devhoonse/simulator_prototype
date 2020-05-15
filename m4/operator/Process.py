import datetime
import logging
from typing import List, Dict, Tuple

from m4.operator.AbstractNode import AbstractNode
from ..constraint.AbstractConstraint import AbstractConstraint
from ..operator.Resource import Resource
from ..operator.process.ProcessResource import ProcessResource
from m4.process.ProcessException import ProcessException
from ..process.Item import Item
from ..util.LogHandler import LogHandler


class Process(AbstractNode):
    """
    Process Object
    각 공정 구현한 클래스
    Route로부터 Lot 이 할당되었을 상황에서의
    실제 처리 동작을 수행하도록 설계
    """

    def __init__(self):
        """
        생성자 :
        """
        super().__init__("PROC")

        # 2-1. Public
        self.id: str = ""                       # Process 일련번호
        self.name: str = ""                     # Process 명칭

        # 2-2. Private
        self._process_resources: Dict[str, ProcessResource] = {}              # Process Resource 인스턴스 목록

        #
        self._logger: logging.Logger = LogHandler.instance().get_logger()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id} at {id(self):#018x}>"

    def init(self, info: dict):
        self.id = info['PROC_ID']
        self.name = info['PROC_NM']

    def add_process_resource(self, info: dict, resource: Resource, use_backward_size: bool):
        process_resource = ProcessResource()
        process_resource.init(info, resource, use_backward_size)
        self._process_resources[info['RESC_ID']] = process_resource

    def get_process_resources(self):
        """

        :return:
        """
        return self._process_resources

    def get_process_resource(self, resource_id: str):
        """

        :param resource_id:
        :return:
        """
        return self._process_resources.get(resource_id, None)

    def check_available(self, date: datetime.datetime, item_id: str, product_quantity: float, move_time: int):
        """
        check Available status
        Inventory : CapaConstraint를 체크
        Process : ProcessResource의 queue 사이즈 체크, Time/Capa Constraint 체크
        :param : item_id
        :param : quantity
        :param : move_time
        :return : Inventory일 경우 가용 여부, Process일 경우 Resource ID
        """
        # Todo : 한 Resource 로만 배당되는 문제 있어 처리 필요 (여러 개가 가능하다면 한 쪽으로만 배당하지 않고 골고루 분배하도록) -> (3단계 - Policy)
        # Todo : Policy - 무작위 / EFFICIENCY / ...

        # (1단계) 각 ProcessResource 별로 할당 가능 여부 확인 : ProcessResource.is_available()
        # 1. Resource 가 일정 제약에 걸리는지 ?
        # 2. _min_lot_size <= quantity <= _max_lot_size 만족하는지 ?
        # 3. _process_lot.is_available() ?
        #       - move 중인 Item 들과 Queue 에 쌓여 있는 Item 들의 갯수가 합쳐서 10개가 넘지 않는지?
        _available_resources: List[Tuple[ProcessResource, float]] = []
        for obj in self._process_resources.values():
            resource: ProcessResource = obj
            is_available, input_quantity = resource.is_available(date, item_id, product_quantity, move_time)
            if is_available:
                _available_resources.append((obj, input_quantity))

        # (2단계) ._priority (우선순위) 정렬
        if len(_available_resources) == 0:
            # 할당 가능한 ProcessResource 가 없을 경우 None 반환
            return None
        else:
            # 할당 가능한 Processresource 들 중 priority 가 가장 작은(우선순위 최대인) 것의 id 문자열을 Return
            _available_resources.sort(key=lambda x: x[0].get_priority())
            _available_resource = _available_resources[0]
            return _available_resource[0].resource_id, _available_resource[1]

    def fetch(self, time_index: int, date: datetime.datetime, item_id: str, work_order_id: str, quantity: float = 0):
        """
        get and remove item quantity
        :param : item_id
        :param : quantity
        :return : Item
        """
        product_quantities: Dict[ProcessResource, float] = {}
        remain_quantity: float = quantity
        while remain_quantity > 0:
            for obj in self._process_resources.values():
                resource: ProcessResource = obj
                # product_quantity += resource.get_quantity(item_id, work_order_id)
                wait_quantity: float = resource.get_wait_quantity(item_id=item_id, work_order_id=work_order_id)
                product_quantities[resource] = min(remain_quantity, wait_quantity)
                remain_quantity -= product_quantities[resource]
                if remain_quantity <= 0:    # for Loop 내에서 종료될 경우 대비
                    break
        product_quantity: float = sum(product_quantities.values())

        if quantity != 0:
            if product_quantity < quantity:
                self._logger.debug(
                    f"[Process {self.id}:{self.name}] : {item_id}:{work_order_id}"
                    f" - product quantity less than fetch quantity - {product_quantity} < {quantity}"
                )
                return []
            elif product_quantity > quantity:
                # Todo : Check - Resource 의 Min Lot Size 값 때문에 좀 더 많이 만들어질 수 있음
                self._logger.debug(
                    f"[Process {self.id}:{self.name}] : {item_id}:{work_order_id}"
                    f" - product quantity exceed fetch quantity - {product_quantity} > {quantity}"
                )

        items = []
        for resource in product_quantities:
            ret: list = resource.fetch(time_index, date, item_id, work_order_id, product_quantities[resource])
            items.extend(ret)
        fetched_quantity: float = sum([item.get_quantity() for item in items])

        self._logger.info(f"[Process {self.id}:{self.name}] : {item_id}:{work_order_id} "
                          f"- fetched {fetched_quantity} from {len(items)} items")

        return items

    def put(self, time_index: int, date: datetime.datetime, item: Item, move_time: int, resource_id: str):
        """
        put item
        Inventory, ProcessResource의 ProcessLot의 moves에 Item 추가
        :param : item
        """
        resource: ProcessResource = self._process_resources[resource_id]
        resource.put(time_index=time_index, date=date, item=item, move_time=move_time)

    def run(self, time_index: int, date: datetime.datetime, is_off_day: bool, off_day_type: str,
            factory_const: AbstractConstraint):
        """
        FactorySimulator에서 tick이 발생했을때 aging 처리 전파
        """
        for obj in self._process_resources.values():
            resource: ProcessResource = obj
            resource.run(time_index, date, is_off_day, off_day_type, factory_const)

    def plan_input_quantity(self, quantity: float, item_id: str = ''):
        """
        Backward 에서 현재 Process에 대한 StepPlan 분할을 위한 메서드
        현재는 Default Policy 성격 로직 사용
        # Todo: 이 자체가 최적화 대상으로 여겨짐
        :param item_id:
        :param quantity: 현재 단계에서 생산해야 하는 Plan Quantity
        :return:
        """

        rslt: list = []
        while quantity > 0:
            for res_id, obj in self._process_resources.items():
                res: ProcessResource = obj
                qty = res.calculate_available_input_quantity(quantity)
                rslt.append((res_id, qty))
                quantity -= qty
                if quantity <= 0:
                    return rslt
        return rslt

    def get_items(self, item_id: str, work_order_id: str) -> List[Item]:
        items: List[Item] = []
        for obj in self._process_resources.values():
            process_resource: ProcessResource = obj
            items.extend(
                process_resource.get_items(item_id=item_id, work_order_id=work_order_id)
            )
        return items

    def get_precision(self):
        # Todo: 만약 (그럴 경우는 없을 거라 보여지지만..) RESOURCE 마다 Precision 설정이 다르다면?
        precisions: list = [obj.get_process_precision()
                            for obj in self._process_resources.values()]
        return precisions[0]

    def split_required_quantity(self, required_quantity: float):
        # Todo: 만약 (그럴 경우는 없을 거라 보여지지만..) RESOURCE 마다 Precision 설정이 다르다면?
        res: ProcessResource = list(self._process_resources.values())[0]  # Hard Coded

        rslt: list = []
        while required_quantity > 0:
            input_qty: float = res.calculate_available_input_quantity(required_quantity)  # Todo
            rslt.append(input_qty)
            required_quantity -= input_qty
        return rslt
