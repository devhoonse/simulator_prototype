import math

from m4.common.SingletonInstance import SingletonInstance
from m4.util.LogHandler import LogHandler

from m4.ApplicationConfiguration import ApplicationConfiguration
from m4.dao.AbstractDataSource import AbstractDataSource
from m4.dao.AbstractSession import AbstractSession
from m4.dao.PlanVersionDAO import PlanVersionDAO
from m4.dao.SimulationDAO import SimulationDAO
from m4.dao.WorkOrderDAO import WorkOrderDAO
from m4.process.WorkOrder import WorkOrder
from m4.manager.FactoryBuilder import FactoryBuilder
from m4.manager.FactoryManager import FactoryManager
from m4.manager.ScheduleManager import ScheduleManager
from m4.manager.BackwardPlanner import BackwardPlanner
from m4.manager.SimulationMonitor import SimulationMonitor
from m4.backward.BackwardManager import BackwardManager
from m4.backward.BackwardBuilder import BackwardBuilder


class FactorySimulator(SingletonInstance):

    def __init__(self):
        # logger
        self._logger = LogHandler.instance().get_logger()
        # 생산 일정 계획 버전 정보
        self._plan_version_dict: dict = dict()
        # 시뮬레이션 정보
        self._simulation_dict: dict = dict()
        # Schedule Manager Object
        self._schedule_manager = ScheduleManager()  # Simulator 전체 runTime 범위 관리하는 ScheduleManager 객체
        # Factory Manager Object
        self._factory_manager: FactoryManager = FactoryManager.instance()  # Simulator 전체 runTime 범위 관리하는 ScheduleManager 객체
        # Backward Planner
        self._backward_planner: BackwardPlanner = BackwardPlanner()

        self.backward_step_plan_result: list = []
        self.backward_step_plan_by_loc: dict = {}
        self.backward_step_peg_result: dict = {}

    def init(self, plan_version_id: str, simulation_id: str, config: ApplicationConfiguration, data_source: AbstractDataSource):
        session: AbstractSession = data_source.get_session()

        plan_version_dao = PlanVersionDAO.instance()
        self._plan_version_dict = plan_version_dao.map(plan_version_dao.instance().select_one(session, plan_version_id=plan_version_id))[0]
        simulation_dao = SimulationDAO.instance()
        self._simulation_dict = simulation_dao.map(simulation_dao.instance().select_one(session, simulation_id=simulation_id))[0]

        # ScheduleManager 객체 setup
        self._schedule_manager.init(self._plan_version_dict, self._simulation_dict, session)

        # FactoryBuilder.build(self._plan_version_dict, self._simulation_dict, session)
        self._factory_manager.init(FactoryBuilder.build(plan_version_dict=self._plan_version_dict,
                                                        simulation_dict=self._simulation_dict,
                                                        config=config,
                                                        session=session))

        # Factory 인스턴스에 세팅된 기준 정보(DB)로부터 파생되는 정보 계산 및 반영
        self._factory_manager.init_derivative_information()

        # Backward Planner
        self._backward_planner.init(self._factory_manager.get_factory(), config)

        work_orders = []
        work_order_dao = WorkOrderDAO.instance()
        work_order_data = work_order_dao.map(work_order_dao.select(session, plan_version_id=plan_version_id))
        for info in work_order_data:
            order: WorkOrder = WorkOrder()
            order.init(info)
            work_orders.append(order)
        self._factory_manager.init_work_order(work_orders)

        session.close()

    def backward(self):
        """

        :return:
        """
        pass
        # 임시 잠금
        # backward_orders, backward_peggings = self._backward_planner.plan(self._factory_manager.get_work_order())
        # self._factory_manager.init_work_order(backward_orders)
        # self._factory_manager.init_base_stock(backward_peggings)

    def backward_old(self, data_source: AbstractDataSource, config: ApplicationConfiguration):
        """

        :return:
        """

        # config 객체로부터 설정 정보 받아오기
        use_backward_size: bool = bool(config.find('Backward', 'backward.res.size'))

        # Session 취득
        session: AbstractSession = data_source.get_session()

        ########################################################################
        # Backward Process
        ########################################################################

        # 싱글톤 BackwardManager 인스턴스 가져오기
        backward_manager: BackwardManager = BackwardManager.instance()
        work_order_list, route_list, inventory_list, inventory_item_list, wip_list, bor_list = \
            BackwardBuilder.build(plan_version_dict=self._plan_version_dict,
                                  simulation_dict=self._simulation_dict,
                                  session=session)

        setup_time_dict, proc_time_dict, move_time_dict = \
            BackwardBuilder.create_time_dict(route_list=route_list, bor_list=bor_list)

        # Initialize Backward Process
        backward_manager.init(plan_version_dict=self._plan_version_dict,
                              work_order_list=work_order_list,
                              route_list=route_list,
                              inventory_list=inventory_list,
                              inventory_item_list=inventory_item_list,
                              wip_list=wip_list,
                              bor_list=bor_list,
                              setup_time_dict=setup_time_dict,
                              proc_time_dict=proc_time_dict,
                              move_time_dict=move_time_dict)

        # Execute Backward Process
        backward_step_plan_result, backward_step_plan_by_loc, backward_step_peg_result = \
            backward_manager.run(use_backward_size)
        self.backward_step_plan_result = backward_step_plan_result
        self.backward_step_plan_by_loc = backward_step_plan_by_loc
        self.backward_step_peg_result = backward_step_peg_result

        # Set
        factory_manager: FactoryManager = FactoryManager.instance()
        factory_manager.set_backward_peg_item(self._plan_version_dict,
                                              self.backward_step_peg_result)
        factory_manager.set_backward_step_plan(self.backward_step_plan_by_loc,
                                               self._schedule_manager.get_start_date())

    def forward(self, data_source: AbstractDataSource):
        """
        실제 Simulation 을 구동하는 메서드
        :return: void
        """

        print("\nFactorySimulator.forward()")

        # 싱글톤 FactoryManager 인스턴스 가져오기
        factory_manager: FactoryManager = FactoryManager.instance()

        # 싱글톤 SimulationMonitor 인스턴스 가져오기
        monitor: SimulationMonitor = SimulationMonitor.instance()
        monitor.init(factory_manager=self._factory_manager, data_source=data_source)

        # 시뮬레이션 시작 전 상황 snapshot
        monitor.snapshot()

        # number_of_digits = 콘솔 출력용 자릿수 값
        # 예를 들어 calendar 갯수가 86400 개라고 하면,
        # number_of_digits 값은 5 가 됨.
        # 콘솔에 출력 시 00000 ~ 86400 으로 캘린더 번호의 자릿수를 맞추기 위한 변수
        horizon: int = self._schedule_manager.length()
        number_of_digits: int = math.floor(math.log(horizon, 10)) + 1

        # 다음 시간 정보가 있는 한 계속 시간을 앞으로 보내도록 설계
        while self._schedule_manager.has_next():
            time: dict = self._schedule_manager.next()
            self._logger.debug(time)

            # 현재 캘린더의 리스트 내 위치 index 를 문자열 Formatting     ex: 00000 ~ 86400
            # idx_string: str = "%0{}d".format(number_of_digits) % time["index"]

            # 현재 RunTime 정보를 Console 에 출력
            # self._logger.debug(f"[{idx_string}] {time['date']}")

            # FactoryManager 인스턴스를 통해 Factory 내 각 operator 들의 시간 진행 상태를 1 tick
            # Todo: 공장 달력 상 Off Day 일 경우 기존에 진행 중이던 작업들을
            #   Work Divisibility 옵션에 따라 작업 진행도를 tick 할지 말지 판단
            factory_manager.run(run_time=time)

            # available, fetch, put
            # - 공장 달력 상 Off Day 가 아닐 경우에만 Route 간 Item 이동 및 할당이 이루어지도록
            # - Item 의 이동 및 할당은 곧 다음 Route 에 대한 새 작업 할당인 셈인데,
            #   Work Divisibility 가 어떻게 설정 되어있든 간에 현재 시각이 Off Day 이면 새 작업을 시작할 수 없기 때문
            # Todo: 다만 지금이 Off Day 는 아니지만 Off Day 가 곧 다가오는 경우는
            #   Work Divisibility 옵션에 따라 작업 transfer 및 할당 동작이 실행되도록 설계 필요
            factory_manager.transfer(run_time=time)

            # 현재 RunTime 에서의 시뮬레이션 상황 snapshot 저장
            monitor.snapshot()

        # Gantt Chart 표현을 위한 Resource 별 Work History 데이터
        res_history: list = monitor.send_res_history(self._plan_version_dict, self._simulation_dict)

        print("debug point")
