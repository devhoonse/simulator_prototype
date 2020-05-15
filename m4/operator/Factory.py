import datetime

from ..constraint.AbstractConstraint import AbstractConstraint
from ..constraint.ScheduleConstraint import ScheduleConstraint
from ..operator.Inventory import Inventory
from ..operator.Process import Process
from ..operator.Route import Route
# from ..process.Router import Router   # Will be Deprecated
from ..process.Item import Item
from ..backward.BackwardStepPlan import BackwardStepPlan
from ..util.DateTimeUtility import DateTimeUtility


class Factory(object):
    """
    Factory Object

    """

    def __init__(self):

        # 멤버 변수 목록
        self.id: str = ""  #
        self.name: str = ""  #
        self.location_id: str = ""  #

        # 2-2. Private 멤버 변수 목록
        self._schedule_constraint: ScheduleConstraint = None  # 공장 비가용 계획 캘린더 인스턴스 사전 {CalendarID: Calendar}
        self._inventories: dict = {}  # Inventory 객체 리스트
        self.processes: dict = {}  # Process 객체 리스트
        self._routes: dict = {}  # Route 객체 리스트 = inventory 및 process 간 연결 관계 정의

        # Demand
        # self._demand_list: list = []

        # Route 관련
        self._work_order_list: list = []
        # self._route_sequence: dict = {}   # Deprecated
        self._starting_routers: dict = {}
        self._next_to_curr_item_dict: dict = {}
        self._item_to_final_item_dict: dict = {}
        self._next_to_curr_location_dict: dict = {}
        self._due_date_by_order_dict: dict = {}
        self._qty_by_order_dict: dict = {}

    def init(self,
             info: dict,
             schedule_constraint: ScheduleConstraint,
             inventories: dict,
             processes: dict,
             work_order_master: list,
             routes: dict):

        # 공장 정보 설정
        self._init_info(info=info)

        # 공장 비가용 Calendar 정보 세팅
        self._init_schedule_constraint(schedule_constraint=schedule_constraint)

        # 공장 내 Inventory 객체들을 초기화
        self._init_inventories(inventories=inventories)

        # 공장 내 Process 객체들을 초기화 : Propagate
        self._init_processes(processes=processes)

        # 공장 내 Route 객체들을 초기화
        self._init_routes(routes=routes)

        # Work Order 정보 초기화
        self._init_work_orders(work_order_master=work_order_master)

        # FactoryManager 로 이동
        # self._init_due_qty_by_order(work_order_master=work_order_master)

        # FactoryManager 로 이동
        # self._init_next_to_curr_item_dict(to_from_item_dict=next_to_curr_item_dict)

        # Factory Manager 로 이동
        # self._init_item_to_final_item_dict(item_to_final_item_dict=item_to_final_item_dict)

        # Factory Manager 로 이동
        # self._init_next_to_curr_location_dict(to_from_location_dict=next_to_curr_location_dict)

        # 최초 출발지 Inventory 에 Work Order Item 인스턴스들을 할당
        # self._init_initial_items(work_order_items=work_order_items)

    # <!> Moved to FactoryManager
    # def set_backward_step_plan(self, orders: dict, plan_version_dict: dict):
    #
    #     plan_start_date = DateTimeUtility.convert_str_to_date(plan_version_dict['START_DT_HMS'])
    #
    #     for obj in self._routes:
    #         router: Route = obj
    #         step_plans = orders.get(router.current_route.id, [])
    #         router.set_production_orders(production_orders=step_plans)
    #
    #     for router in self._starting_routers:
    #         router_obj: Route = router
    #         step_plans = orders.get(router_obj.current_route.id, [])
    #         for step_plan in step_plans:
    #             if step_plan.required_quantity > 0:
    #                 item = self._init_backward_step_plan(step_plan=step_plan)
    #                 # 최초 Setting
    #                 router_obj.current_route.put(time_index=0, date=plan_start_date, item=item, move_time=0)

    # <!> Moved to FactoryManager
    # def set_backward_peg_item(self, peg_result_dict: dict):
    #     after_peg_stock = {}
    #     for key, value in peg_result_dict.items():
    #         if key[0] not in after_peg_stock.keys():
    #             temp_list = []
    #             for item in value:
    #                 info = self._init_peg_item(item=item, key=key)
    #                 temp_list.append(info)
    #             after_peg_stock.update({key[0]: {key[1]: temp_list}})
    #         else:
    #             temp_dict = after_peg_stock[key[0]]
    #             if key[1] not in temp_dict.keys():
    #                 temp_list = []
    #                 for item in value:
    #                     info = self._init_peg_item(item=item, key=key)
    #                     temp_list.append(info)
    #                 temp_dict.update({key[1]: temp_list})
    #                 after_peg_stock.update({key[0]: temp_dict})
    #             else:
    #                 temp_dict = after_peg_stock[key[0]]
    #                 temp_list = temp_dict[key[1]]
    #                 for item in value:
    #                     info = self._init_peg_item(item=item, key=key)
    #                     temp_list.append(info)
    #                 temp_dict.update({key[1]: temp_list})
    #                 after_peg_stock.update({key[0]: temp_dict})
    #
    #     for peg_inv in after_peg_stock.keys():
    #         for inventory in self._inventories.keys():
    #             if inventory == peg_inv:
    #                 inv: Inventory = self._inventories[inventory]
    #                 inv.set_item_dict(after_peg_stock[peg_inv])

    def run(self, run_time: dict, time_constraint: object = None):
        """

        :param run_time:
        :param time_constraint:
        :return:
        """
        self._run_reverse(run_time=run_time, time_constraint=time_constraint)

    def _run_reverse(self, run_time: dict, time_constraint: object = None):
        for route_step in sorted(self._route_sequence.keys()):
            for obj in self._route_sequence[route_step]:
                router: Route = obj
                router.run_(run_time=run_time)

    # # <!> Moved to FactoryManager
    # def _init_backward_step_plan(self, step_plan: BackwardStepPlan):
    #     item: Item = Item()
    #
    #     item.init(item_id=step_plan.item_id,
    #               location_id=step_plan.location_id,
    #               quantity=step_plan.required_quantity,
    #               work_order_id=step_plan.work_order_id,
    #               order_item_id=step_plan.order_item_id,
    #               order_quantity=step_plan.order_quantity,
    #               req_quantity=step_plan.required_quantity,
    #               due_date=self._due_date_by_order_dict.get(step_plan.work_order_id, None),
    #               lpst=step_plan.lpst,
    #               priority=step_plan.priority)
    #
    #     return item

    # <!> Moved to FactoryManager
    # def _init_peg_item(self, item:dict, key: tuple):
    #     info = Item()
    #     work_order_id = item.get('WORK_ORDER_ID', '')
    #
    #     info.init(item_id=item.get('ITEM_ID', ''),
    #               location_id=item.get('LOC_ID', key[0]),
    #               quantity=item.get('STOCK_QTY', 0),
    #               work_order_id=work_order_id,
    #               order_item_id=item.get('ORDER_ITEM_ID', ''),
    #               order_quantity=self._qty_by_order_dict.get(work_order_id, 0),
    #               req_quantity=item.get('REQ_QTY', 0),
    #               peg_quantity=item.get('PEG_QTY', 0),
    #               due_date=self._due_date_by_order_dict.get(work_order_id, None),
    #               lpst=item.get('LPST', None),
    #               priority=item.get('PRIORITY', -1))
    #
    #     return info

    def get_time_constraints(self, run_time: dict):
        """

        :param run_time:
        :return:
        """

        if run_time['is_off_day']:
            return run_time
        else:
            current_time_constraint: AbstractConstraint = self._get_current_schedules(run_time=run_time['date'])
            return current_time_constraint

    def get_router_by_location_id(self, route_id: str):
        """

        :param route_id:
        :return:
        """
        if route_id in self._routes.keys():
            return self._routes[route_id]
        else:
            return None

    def get_process(self, process_id: str) -> Process:
        """

        :param process_id:
        :return:
        """
        # if process_id in self.processes.keys():
        #     return self.processes[process_id]
        # else:
        #     return None
        return self.processes.get(process_id, None)

    def get_inventory(self, inventory_id: str) -> Inventory:
        """

        :param inventory_id:
        :return:
        """
        return self._inventories.get(inventory_id, None)

    def get_previous_location(self, next_location: str):
        """

        :return:
        """
        return self._next_to_curr_location_dict[next_location]

    def _get_current_schedules(self, run_time: datetime.datetime):
        """

        :param run_time:
        :return:
        """

        return self._schedule_constraint.check(run_time)

    def _init_work_orders(self, work_order_master: list):
        """

        :param work_order_master:
        :return:
        """
        self._work_order_list = work_order_master

    # Deprecated
    # def _init_initial_items(self, work_order_items: list):
    #     """
    #
    #     :param work_order_items:
    #     :return:
    #     """
    #     starting_routers: list = self._get_initial_routers()
    #     if len(starting_routers) == 0:
    #         raise AssertionError(
    #             ""
    #         )
    #     elif len(starting_routers) == 1:
    #         starting_router: Route = starting_routers[0]
    #         starting_inventory: Inventory = starting_router.current_route
    #         for item in work_order_items:
    #             starting_inventory.put_initial_item(item=item)
    #     else:
    #         # 2 군데 이상의 Starting Inventory 가 있는 경우
    #         # 구현 필요
    #         pass

    # Deprecated
    # def _get_initial_routers(self):
    #     """
    #     <Hard Coding>
    #     구현 필요
    #     self._routers 리스트로부터 가장 출발점 Route 들을 반환
    #     :return:
    #     """
    #     return [router for router in self._routes
    #             if isinstance(router.current_route, Inventory) and router.current_route.start_flag is True]

    def _init_routes(self, routes: dict):
        """

        :param routes:
        :return:
        """
        self._routes = routes

    def _init_router_sequence(self, router_sequence: dict):
        """

        :param router_sequence:
        :return:
        """
        self._route_sequence = router_sequence

    def _init_processes(self, processes: dict):
        """

        :param process_master:
        :return:
        """
        self.processes = processes

    def _init_inventories(self, inventories: dict):
        """

        :param inventories:
        :return:
        """
        self._inventories = inventories

    def _init_info(self, info: dict):
        """

        :param info:
        :return:
        """

        self.id = info['PLANT_ID']
        self.name = info['PLANT_NM']
        self.location_id = info['LOC_ID']

    def _init_schedule_constraint(self, schedule_constraint: ScheduleConstraint):
        """

        :param schedule_constraint:
        :return:
        """
        self._schedule_constraint = schedule_constraint

    def _init_loc_to_route_dict(self, loc_to_route_dict: dict):
        """

        :param loc_to_route_dict:
        :return:
        """
        self._loc_to_route_dict = loc_to_route_dict

    # <!> Moved to FactoryManager
    # def _init_due_qty_by_order(self, work_order_master: list):
    #     due_date_by_order_dict = {}
    #     qty_by_order_dict = {}
    #
    #     for work_order in work_order_master:
    #         due_date_str = work_order['DUE_DT']
    #         due_date = DateTimeUtility.convert_str_to_date(due_date_str) if isinstance(due_date_str, str) \
    #             else due_date_str if isinstance(due_date_str, datetime.datetime) else None
    #         due_date_by_order_dict.update({work_order['WORK_ORDER_ID']: due_date})
    #         qty_by_order_dict.update({work_order['WORK_ORDER_ID']: work_order['ORDER_QTY']})
    #
    #     self._due_date_by_order_dict = due_date_by_order_dict
    #     self._qty_by_order_dict = qty_by_order_dict

    # Deprecated
    # @property
    # def _starting_routers(self, route_sequence: dict) -> dict:
    #     sequence_indices: list = sorted(route_sequence.keys())
    #     sequence_depth: int = max(sequence_indices)
    #
    #     routes: dict = dict()
    #     for index in sequence_indices:
    #         for obj in route_sequence[index]:
    #             route: Route = obj
    #             prior_routers: list = \
    #                 [] if index == sequence_depth else \
    #                 [pr for pr in route_sequence[index + 1]
    #                  if route.get_current() in pr.next_route_list]
    #
    #             if len(prior_routers) == 0:
    #                 routes.update({index: routes.get(index, []) + [route]})
    #     return routes

    def get_route_list(self) -> dict:
        return self._routes

    def get_route(self, current_location_id: str):
        return self._routes.get(current_location_id)
