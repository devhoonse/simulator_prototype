import datetime
from typing import List, Dict
from collections import defaultdict

from m4.common.SingletonInstance import SingletonInstance
from ..backward.BackwardStepPlan import BackwardStepPlan
from ..constraint.AbstractConstraint import AbstractConstraint
from m4.operator.Factory import Factory
from ..operator.AbstractNode import AbstractNode
from ..operator.Inventory import Inventory
from ..operator.Route import Route
from ..operator.RouteAttribute import RouteAttribute
from ..operator.Process import Process
from ..operator.process.ProcessLot import ProcessLot
from ..operator.process.ProcessResource import ProcessResource
from ..process.Item import Item
from ..util.DateTimeUtility import DateTimeUtility


class FactoryManager(SingletonInstance):

    def __init__(self):
        self._factory: Factory = None

        self._optimizer: object = None
        self._work_orders: list = []
        self._base_stock: dict = dict()

        self._qty_by_order_dict: dict = {}

        self._starting_routes: List[Route] = []  # FactoryManager.run() 시에
        self._last_routes: List[Route] = []  # FactoryManager.run() 시에 마지막 Router 부터 이전 Router 로 타고가는 로직의 출발점
        self._route_graph: Dict[Route, List[Route]] = dict()  # Route 네트워크 그래프
        # self._route_paths: List[List[Route]] = []       # Route 네트워크 그래프 역방향 transfer 순서 Path

        self._entire_min: int = 0
        self._entire_max: int = 0

    def init(self, factory: Factory):
        self._factory = factory

    def init_derivative_information(self):
        """
        FactoryBuilder.Build() 완료 후
        Factory 인스턴스에 담긴 기준 정보로부터 파생 정보를 계산하여 self._factory 에 반영
        :return:
        """

        # Work Order 관련 파생 정보 계산 및 세팅
        self._init_due_qty_by_order(work_order_master=self._work_orders)

        # Router 관련 파생 정보 계산 및 세팅
        self._init_router_derivative_info()

        # 전체 Process 들을 모두 고려한 min / max 범위 계산 및 세팅
        self._init_entire_min_max_lot_size()

        # # Factory -> FactoryManager 이동
        # self._init_next_to_curr_item_dict(to_from_item_dict=next_to_curr_item_dict)
        #
        # # Factory -> FactoryManager 이동
        # self._init_item_to_final_item_dict(item_to_final_item_dict=item_to_final_item_dict)
        #
        # # Factory -> FactoryManager 이동
        # self._init_next_to_curr_location_dict(to_from_location_dict=next_to_curr_location_dict)

    def _init_entire_min_max_lot_size(self):
        self._entire_min = max(res.get_min_lot_size()
                               for proc in self._factory.processes.values()
                               for res in proc.get_process_resources().values())
        self._entire_max = min(res.get_max_lot_size()
                               for proc in self._factory.processes.values()
                               for res in proc.get_process_resources().values())

    def init_work_order(self, work_orders: list):
        # self._factory.set_backward_step_plan(orders=orders, plan_version_dict=plan_version_dict)
        # print(f"{self.__class__.__name__}.init_work_order()")
        self._work_orders = work_orders

    def init_base_stock(self, base_stock: dict):
        # self._factory.set_backward_peg_item(peg_result_dict=peg_result)
        pass

    def get_factory(self):
        return self._factory

    def get_work_order(self):
        return self._work_orders

    def get_entire_min_capa_size(self):
        return self._entire_min

    def get_entire_max_capa_size(self):
        return self._entire_max

    def get_location(self, location_id: str):

        inv: Inventory = self._factory.get_inventory(location_id)
        if inv:
            return inv
        proc: Process = self._factory.get_process(location_id)
        return proc

    def run(self, run_time: dict):
        """
        Time Tick 을 Router 를 통해 전파
        End Router(들) 로부터 출발하여 Router 의 역순으로 전파
        :param run_time:
        :return:
        """

        schedule_const = self._factory.get_time_constraints(run_time)

        # 이미 run 을 수행한 Route 오브젝트들을 기억하기 위한 빈 리스트 초기화 : run() 의 이중 호출 방지
        already_executed: List[Route] = []
        previous_routes: List[Route] = []

        # 이전 Route 가 없을 때까지 do-while 패턴 실행 (Python 에 do-while 없음)
        current_routes: List[Route] = self._last_routes  # 마지막 단계 Route 부터 시작
        while True:
            for obj in current_routes:  # 현재 Depth Route 각각에 대해
                route: Route = obj
                if route in already_executed:  # .run() 이 호출된 적이 있다면 .run() 하지 않고
                    continue
                route.run(run_time, schedule_const)  # .run() 이 호출된 적이 없다면 호출 : 이중 호출 방지
                already_executed.append(route)  # .run() 이 호출되었으므로 리스트에 추가
                previous_routes.extend(route.get_previous_routes().values())

            if previous_routes:  # 처리할 이전 Route 가 남아있을 경우 -> 진행
                current_routes = previous_routes  # 다음 Loop 에서는 이전 Route 들이 .run() 대상
                previous_routes = []
                continue
            break  # 이전 Route 가 없으면 break

    def transfer(self, run_time: dict):
        """
        # Todo: fetch, put 로직 분리 ?
        Will be Deprecated
        앞선 단계에서 각 node 마다 .run() 을 수행한 후에
        각 Router를 통해 node 마다 .transfer() 를 호출하는 메서드
        End Router(들) 로부터 출발하여 Router 의 역순으로 전파
        :param run_time:
        :return:
        """

        # 현재 시점이 Off Day 구간 내에 있는 경우, fetch 및 put 작업 할당 할 수 없음
        is_off_day: bool = run_time.get('is_off_day', False)
        if is_off_day:
            return

        # Todo: is_off_day 가 False 일 경우, Divisible (Y/N/I) 타입에 따라 실행 가능한 지 아닌 지 판단

        # 이미 동작을 을 수행한 Route 오브젝트들을 기억하기 위한 빈 리스트 초기화 : run() 의 이중 호출 방지
        already_executed: List[Route] = []
        previous_routes: List[Route] = []

        # 이전 Route 가 없을 때까지 do-while 패턴 실행 (Python 에 do-while 없음)
        current_routes: List[Route] = self._last_routes  # 마지막 단계 Route 부터 시작
        while True:
            for obj in current_routes:  # 현재 Depth Route 각각에 대해
                route: Route = obj
                if route in already_executed:  # 수행된 적이 있다면 수행하지 않고 다음 Route 로
                    continue
                route.transfer(run_time)  # 수행된 적이 없다면 호출 : 이중 호출 방지
                already_executed.append(route)  # 수행되었으므로 리스트에 추가
                previous_routes.extend(route.get_previous_routes().values())

            if previous_routes:  # 처리할 이전 Route 가 남아있을 경우 -> 진행
                current_routes = previous_routes  # 다음 Loop 에서는 이전 Route 들이 .run() 대상
                previous_routes = []
                continue
            break  # 이전 Route 가 없으면 break

    # ================== #
    #   Work Order 관련   #
    # Moved from Factory #
    # ================== #
    def set_backward_step_plan(self, orders: dict, plan_start_date: datetime.datetime):

        for obj in self._factory.get_route_list().values():
            route: Route = obj
            order_items = orders.get(route.get_current_id(), [])
            route.set_work_orders(order_items)

        for route in self._starting_routes:
            router_obj: Route = route
            order_items = orders.get(router_obj.get_current_id(), [])
            for step_plan in order_items:
                if step_plan.required_quantity > 0:
                    item = self._init_backward_step_plan(step_plan=step_plan)
                    # 최초 Setting
                    router_obj.get_current().put(time_index=0,
                                                 date=plan_start_date,
                                                 item=item,
                                                 move_time=0,
                                                 target_id=item.location_id)

    def set_backward_peg_item(self, plan_version_dict: dict, peg_result_dict: dict):
        """
        Backward Pegging 계산 결과 정보를 실제 Inventory 인스턴스의 stock 에 반영하는 처리
        이를 통해 각 기존 재고 Item 들은
        저마다 Pegging 수량만큼 Cut 되어 해당 Work Order ID 를 부여받고
        부여받은 Work Order ID 를 통해
        이후 Forward 에서 해당 Item 인스턴스를 가져갈 수 있도록 함
        :param plan_version_dict:
        :param peg_result_dict:
        :return:
        """

        plan_start_date = DateTimeUtility.convert_str_to_date(plan_version_dict['START_DT_HMS'])

        after_peg_stock: Dict[str, Dict[str, List[Item]]] = dict()
        for key, value in peg_result_dict.items():
            dict_: dict = after_peg_stock.get(key[0], dict())
            list_: list = dict_.get(key[1], [])
            # list_new: list = [self._init_peg_item(info, key) for info in value]
            list_new: list = [info for info in value]
            dict_.update(
                {key[1]: list_ + list_new}
            )
            after_peg_stock.update(
                {key[0]: dict_}
            )

        for peg_inv in after_peg_stock.keys():
            inv: Inventory = self._factory.get_inventory(peg_inv)
            if inv is None:
                continue
            # 기존 방식: Inventory._stock dict 객체를 아예 덮어쓰면서 앞서 factory builder 에서 세팅된 내용이 없어졌는데
            #  - Inventory.set_backward_peg_items() 를 따로 정의하여 기존 문제점 방지
            inv.set_backward_peg_items(plan_start_date, after_peg_stock[peg_inv])

    def _init_peg_item(self, item: dict, key: tuple):
        info = Item()
        work_order_id = item.get('WORK_ORDER_ID', '')

        info.init(item_id=item.get('ITEM_ID', ''),
                  location_id=item.get('LOC_ID', key[0]),
                  quantity=item.get('PEG_QTY', 0),
                  work_order_id=work_order_id,
                  order_item_id=item.get('ORDER_ITEM_ID', ''),
                  order_quantity=self._qty_by_order_dict.get(work_order_id, 0),
                  req_quantity=item.get('REQ_QTY', 0),
                  peg_quantity=item.get('PEG_QTY', 0),
                  due_date=self._due_date_by_order_dict.get(work_order_id, None),
                  lpst=item.get('LPST', None),
                  priority=item.get('PRIORITY', -1))

        return info

    def _init_backward_step_plan(self, step_plan: BackwardStepPlan):
        item: Item = Item()

        item.init(item_id=step_plan.item_id,
                  location_id=step_plan.location_id,
                  quantity=step_plan.required_quantity,
                  work_order_id=step_plan.work_order_id,
                  order_item_id=step_plan.order_item_id,
                  order_quantity=step_plan.order_quantity,
                  req_quantity=step_plan.required_quantity,
                  due_date=self._due_date_by_order_dict.get(step_plan.work_order_id, None),
                  lpst=step_plan.lpst,
                  priority=step_plan.priority)

        return item

    def _init_due_qty_by_order(self, work_order_master: list):
        due_date_by_order_dict = {}
        qty_by_order_dict = {}

        for work_order in work_order_master:
            due_date_str = work_order['DUE_DT']
            due_date = DateTimeUtility.convert_str_to_date(due_date_str) if isinstance(due_date_str, str) \
                else due_date_str if isinstance(due_date_str, datetime.datetime) else None
            due_date_by_order_dict.update({work_order['WORK_ORDER_ID']: due_date})
            qty_by_order_dict.update({work_order['WORK_ORDER_ID']: work_order['ORDER_QTY']})

        self._due_date_by_order_dict = due_date_by_order_dict
        self._qty_by_order_dict = qty_by_order_dict

    # ======================= #
    # Router 파생 정보 세팅 관련 #
    # ======================= #
    def _init_router_derivative_info(self):
        """

        :return:
        """

        # FactoryManager.run() 시에 마지막 Router 부터 이전 Router 로 타고가는 로직의 출발점 및 종착점 설정
        self._starting_routes = self._get_starting_routers()
        self._last_routes = self._get_last_routers()

        # Route 마다 연결 정보 부여, Route 네트워크 그래프 작성
        for obj in self._factory.get_route_list().values():
            route: Route = obj
            route.set_previous_routes(self._get_previous_routes(route=route))
            route.set_next_routes(self._get_next_routes(route=route))
            route.set_from_route_attribute_dict(self._get_from_route_attribute_dict(route))
            route.set_next_route_attribute_dict(self._get_to_route_attribute_dict(route))
            self._route_graph.update({route: list(route.get_previous_routes().values())})

    @staticmethod
    def _get_to_route_attribute_dict(route: Route):
        """

        :param route:
        :return: dict {
            (curr_item_id, end_item_id, node_instance): [..., RouteAttribute, ...]
        }
        """
        ret: dict = defaultdict(list)
        next_route_dict: dict = route.get_next_route_dict()
        for row in next_route_dict.items():
            current_item_id: str = row[0]
            attributes: list = row[1]
            for attribute in attributes:
                end_item_id: str = attribute[0]
                node: AbstractNode = attribute[2]
                route_attribute: RouteAttribute = attribute[1]
                ret[(current_item_id, end_item_id, node)].append(route_attribute)
        return ret

    @staticmethod
    def _get_from_route_attribute_dict(route: Route):
        return {
            (tup[1].to_item_id, tup[2]): tup[1]
            for row in route.get_previous_route_dict().values()
            for tup in row
        }

    def _get_starting_routers(self):
        starting_routers: list = []
        for obj in self._factory.get_route_list().values():
            router: Route = obj
            if not router.has_previous():
                starting_routers.append(obj)
        return starting_routers

    def _get_last_routers(self):
        last_routers: list = []
        for obj in self._factory.get_route_list().values():
            router: Route = obj
            if not router.has_next():
                last_routers.append(obj)
        return last_routers

    def _get_next_routes(self, route: Route) -> dict:
        return {
            route.id: route
            for route in
            set([self._factory.get_route(route_attr[1].to_location_id)
                 for rows in route.get_next_route_dict().values()
                 for route_attr in rows])
        }

    def _get_previous_routes(self, route: Route) -> dict:
        return {
            route.id: route
            for route in
            set([self._factory.get_route(route_attr[1].from_location_id)
                 for rows in route.get_previous_route_dict().values()
                 for route_attr in rows])
        }

    def get_resource_history(self, plan_version: str, simulation_id: str):
        """
        forward 종료 후 Factory 인스턴스 내 각 Resource 인스턴스들이 가진 Work History 들을 취합하여 리스트로 반환
        :return:
        """

        convert_time_info: callable = lambda x: \
            {key:
                 DateTimeUtility.convert_date_to_str(val) if key in ["START_DT_HMS", "END_DT_HMS"] else
                 DateTimeUtility.convert_timedelta_to_numeric(val, "HOUR") if key == "DUR" else     # Todo: Hard-Coded UOM
                 val
             for key, val in x.items()}
        append_version_info: callable = lambda x: \
            dict(zip(['PLAN_VER_ID', 'SIM_ID'] + list(x.keys()),
                     [plan_version, simulation_id] + list(x.values())))

        res_history: list = list()
        for proc_id, proc in self._factory.processes.items():
            process: Process = proc
            for res_id, res in process.get_process_resources().items():
                process_resource: ProcessResource = res
                rows: list = list(map(lambda x: append_version_info(convert_time_info(x)),
                                      process_resource.get_resource_history()))
                res_history.extend(rows)

        return list(map(lambda x: list(x.values()), res_history))
