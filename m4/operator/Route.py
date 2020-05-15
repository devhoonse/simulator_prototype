import datetime
from typing import List, Dict, Callable, Tuple

from m4.backward.BackwardStepPlan import BackwardStepPlan
from m4.constraint.AbstractConstraint import AbstractConstraint
from m4.operator.AbstractNode import AbstractNode
from m4.operator.RouteAttribute import RouteAttribute
from m4.operator.Process import Process
from m4.operator.Inventory import Inventory
from m4.operator.RouteException import RouteException
from m4.process.Item import Item
from m4.util.LogHandler import LogHandler


class Route(object):
    """
        Route Object
        Lot Control
    """

    def __init__(self):

        # logger
        self._logger = LogHandler.instance().get_logger()

        # Identification
        self.id: str = ''
        self.type: str = ''

        # Route 연결 정보
        self._current: AbstractNode = None
        self._previous_node_dict: dict = {}
        self._next_node_dict: dict = {}
        self._previous_route_dict: dict = {}
        self._next_route_dict: dict = {}

        # 현재 Route StepPlan 목록
        self._order_items: List[BackwardStepPlan] = []
        self._order_items_finished: List[BackwardStepPlan] = []
        self._shipped_items: dict = {}

        # Backward 에서 세팅된 Quantity 정보를 그대로 사용할 지 여부 설정 정보
        self._use_backward_size: bool = True
        self._transfer_policy: callable = None

        # Derived Properties
        self._next_routes: dict = dict()
        self._previous_routes: dict = dict()
        self._previous_route_attribute_dict: dict = dict()
        self._next_route_attribute_dict: dict = dict()

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.type}) {self._current.id} at {id(self):#018x}>"

    def init(self,
             route_id: str,
             route_type: str,
             route_location: AbstractNode,
             previous_node_dict: dict,
             next_node_dict: dict,
             previous_route_dict: dict,
             next_route_dict: dict,
             use_backward_size: bool):
        self.id = route_id
        self.type = route_type

        self._current = route_location
        self._previous_node_dict = previous_node_dict
        self._next_node_dict = next_node_dict
        self._previous_route_dict = previous_route_dict
        self._next_route_dict = next_route_dict

        self._set_transfer_policy(use_backward_size)

    def _set_transfer_policy(self, use_backward_size: bool):
        self._use_backward_size = use_backward_size
        self._transfer_policy = {
            True: self._execute_backward_plan,
            False: None
        }.get(use_backward_size)

    def run(self, run_time: dict, factory_const: AbstractConstraint):
        """
        현재 Route 가 위치한 Node(Inventory OR Process) 에 대해 .run() 실행
        :param factory_const:
        :param run_time:
        :return:
        """
        self._current.run(run_time['index'], run_time['date'], run_time['is_off_day'], run_time.get('constraint_type'), factory_const)

    def transfer(self, run_time: dict):
        """
        실제 .check_available(), .fetch(), .put() 을 수행하는 메서드
        # Todo: 실제 check, fetch, put 동작 분리 작성 (다형성/BFS)
        :param run_time:
        :return:
        """

        # 현재 시뮬레이션 run_time 정보
        time_index: int = run_time['index']
        time: datetime.datetime = run_time['date']

        # 현재 Route 에서 처리할 대상 BackwardStepPlan 리스트 (LPST 값이 현재 시점 이전인 Plan들만 추출)
        plans: List[BackwardStepPlan] = sorted([obj for obj in self._order_items],
                                               key=lambda x: x.lpst)

        # 다음 Route 없을 경우 (최종 종착지, Inventory (PDINV) 일 것)
        # for Debugging : Ship 을 통해 처리 완료된 Work Order 목록을 파악하기 위한 메서드
        if not self._next_routes:
            for plan in plans:
                self._ship(time_index, time, plan)
            return

        # 각 BackwardStepPlan 별 처리 ( Plan 의 LPST 순으로 탐색 - 긴급한 계획 먼저 )
        for plan in plans:
            self._transfer_policy(time_index, time, plan)

    def _execute_backward_plan(self, time_index: int, time: datetime.datetime, plan: BackwardStepPlan):
        """
        Forward 시 BackwardStepPlan 에 설정된 값을 있는 그대로 실행하는 메서드
        self._use_backward_size: bool 이 True 이면 Route.transfer() 에서 호출됨
        :param time_index:
        :param time:
        :param plan:
        :return:
        """

        work_order_id: str = plan.work_order_id
        order_item_id: str = plan.order_item_id
        required_item_id: str = plan.item_id
        required_quantity: float = plan.required_quantity
        pegging_quantity: float = plan.peg_quantity
        fetch_quantity: float = required_quantity + pegging_quantity

        # 주문에 대한 Item 목록 - 없을 경우 메서드 종료 후 다음 주문(BackwardStepPlan) 처리로 넘어가도록
        current_items: List[Item] = self.get_items(required_item_id, work_order_id)
        if not current_items:
            return

        # 현재 위치에 Plan 에서 요구하는 Item 이 있으면 수량 및 제약 체크 후 각 다음 Route 로 Put 처리
        fetched_quantity: float = 0.0
        for obj in self.get_next_routes().values():  # Todo: 만약 다음 Route 들 중 할당 우선순위가 구분된다면 ?
            next_route: Route = obj
            next_node: AbstractNode = next_route.get_current()

            # Route 간 연결 정보 취득 - 검색되지 않을 경우 Error 레벨 로그 출력 후 아무 동작 없이 다른 Route 에 대한 처리로 이동
            next_attribute: RouteAttribute
            next_attributes: List[RouteAttribute] = self._next_route_attribute_dict.get((required_item_id, order_item_id, next_node), [])
            if len(next_attributes) < 1:
                self._logger.error(
                    f"No RouteAttribute for {required_item_id}, {order_item_id} Has been Found "
                    f"at Route {self.__repr__()}"
                )
                continue
            elif len(next_attributes) == 1:
                next_attribute = next_attributes[0]
            else:
                next_attributes_ = [obj for obj in next_attributes if obj.to_item_id == order_item_id]
                if len(next_attributes_) != 1:
                    self._logger.error(
                        f"No RouteAttribute for {required_item_id}, {order_item_id} Has been Found at Route {self.__repr__()}"
                    )
                    continue
                next_attribute = next_attributes_[0]

            # Route 간 연결 정보로부터 필요한 정보 취득
            next_item_id: str = next_attribute.to_item_id
            move_time: int = next_attribute.move_time

            # 다음 Node 가 할당 가능하지 않을 경우 -> 다른 다음 Route 탐색
            available_info = next_node.check_available(time, next_item_id, fetch_quantity, move_time)
            if available_info is None:
                continue

            # 다음 Node 할당 가능 위치 및 수량 정보 Unwrap
            target_id: str = available_info[0]
            required_input_quantity: float = available_info[1]

            # Backward 에서 세팅된 Target ID 와 현재 할당 가능한 Target ID 가 다를 경우
            if target_id != plan.to_location_id:
                # continue
                pass

            # 아직 수량이 갖춰지지 않아 fetch 가능하지 않은 경우 -> 다른 다음 Route 탐색
            fetched_items: List[Item] = self._current.fetch(time_index, time, required_item_id, work_order_id,
                                                            required_input_quantity)
            if not fetched_items:
                continue

            # fetch 된 Item 을 하나의 아이템으로 뭉쳐주는 처리
            merged_item: Item = self._merge_items(time_index, time, plan, *fetched_items)

            # fetch 로 받아와서 합쳐진 Item 을 다음 Node 에 Put 처리
            merged_item.set_item_id(next_item_id)
            next_node.put(time_index, time, merged_item, move_time, target_id)
            fetched_quantity = merged_item.get_quantity()
            # for item in fetched_items:
            #     item.set_item_id(next_item_id)
            #     next_node.put(time_index, time, item, move_time, target_id)
            #     fetched_quantity += item.get_quantity()

        if fetch_quantity == fetched_quantity:  # Todo: 주문 수량 만큼의 Fetch 및 다음 Node 로의 Put 이 이루어졌을 경우 판단할 조건식
            self._finish_plan(plan)

    def _ship(self, time_index: int, time: datetime.datetime, plan: BackwardStepPlan):
        """
        다음 Route 없을 경우 (최종 종착지, Inventory (PDINV) 일 경우 ) Route.transfer() 내에서 호출
        :return:
        """

        # 각 BackwardStepPlan 별 처리 ( Plan 의 LPST 순으로 탐색 - 긴급한 계획 먼저 )
        work_order_id: str = plan.work_order_id
        order_item_id: str = plan.order_item_id
        required_item_id: str = plan.item_id
        required_quantity: float = plan.required_quantity
        pegging_quantity: float = plan.peg_quantity
        fetch_quantity: float = required_quantity + pegging_quantity

        # 주문에 대한 Item 목록 - 없을 경우 메서드 종료 후 다음 주문(BackwardStepPlan) 처리로 넘어가도록
        current_items: List[Item] = self.get_items(required_item_id, work_order_id)
        if not current_items:
            return

        # fetch 가능하지 않은 경우 -> 다른 다음 Route 탐색
        fetched_items: List[Item] = self._current.fetch(time_index, time, required_item_id, work_order_id,
                                                        fetch_quantity)
        if not fetched_items:   # 해당 주문에 대한 Item 들의 수량이 미비되어 빈 리스트가 반환되었을 경우
            return

        # fetch 로 받아온 Item 들의 수량 체크
        fetched_quantity: float = sum(item.get_quantity() for item in fetched_items)

        if fetch_quantity == fetched_quantity:  # Todo: 주문 수량 만큼의 Fetch 및 다음 Node 로의 Put 이 이루어졌을 경우 판단할 조건식
            self._shipped_items.update({(plan.work_order_id, plan.order_item_id, plan.order_quantity): fetched_items})
            self._finish_plan(plan)

    def _merge_items(self, time_index: int, time: datetime.datetime, plan: BackwardStepPlan, *items):
        """
        Forward 진행 중 Res, Inv 수량 제약 등에 의해 쪼개져 처리된 Item 들을 Merge 하기 위한 메서드
        :param items:
        :return:
        """
        if len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]

        merged_item: Item = Item()
        merged_item.init(
            item_id=plan.item_id,
            location_id=plan.location_id,
            quantity=0,
            work_order_id=plan.work_order_id,
            order_item_id=plan.order_item_id,
            order_quantity=plan.order_quantity,
            req_quantity=plan.required_quantity,
            peg_quantity=plan.peg_quantity,
            due_date=None,
            setup_time=0,
            process_time=0,
            lpst=plan.lpst
        )

        for obj in items:
            item: Item = obj
            item.archive(time_index, time, 'MERGED', self._current.id)
            merged_item.append_merged_item(item)
            merged_item.set_quantity(merged_item.get_quantity() + item.get_quantity())

        merged_item.archive(time_index, time, 'MERGED', self._current.id)

        return merged_item

    def _finish_plan(self, plan: BackwardStepPlan):
        """
        현재 Route 에 할당된 처리 완료된 생산 계획을 삭제 후 완료 목록에 append 하는 처리
        :param plan:
        :return:
        """
        self._order_items_finished.append(self._order_items.pop(self._order_items.index(plan)))

    def set_next_route_attribute_dict(self, to_route_attribute_dict: dict):
        self._next_route_attribute_dict = to_route_attribute_dict

    def set_from_route_attribute_dict(self, from_route_attribute_dict: dict):
        self._previous_route_attribute_dict = from_route_attribute_dict

    def set_work_orders(self, order_items: list):
        self._order_items = order_items

    def get_items(self, item_id: str, work_order_id) -> List[Item]:
        return self._current.get_items(item_id, work_order_id)

    def set_next_routes(self, next_routes: dict):
        self._next_routes = next_routes

    def set_previous_routes(self, previous_routes: dict):
        self._previous_routes = previous_routes

    def get_next_routes(self):
        return self._next_routes

    def get_previous_routes(self):
        return self._previous_routes

    def get_current_id(self):
        return self._current.id

    def get_current(self) -> AbstractNode:
        return self._current

    def get_next_route_dict(self):
        return self._next_route_dict

    def get_previous_route_dict(self):
        return self._previous_route_dict

    def has_next(self) -> bool:
        return len(self._next_node_dict) > 0

    def has_previous(self) -> bool:
        return len(self._previous_node_dict) > 0
