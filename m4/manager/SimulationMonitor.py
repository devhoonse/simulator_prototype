from m4.common.SingletonInstance import SingletonInstance
from m4.dao.HIstoryDAO import HistoryDAO
from m4.manager.FactoryManager import FactoryManager
from m4.dao.AbstractDataSource import AbstractDataSource
from m4.dao.AbstractSession import AbstractSession


class SimulationMonitor(SingletonInstance):

    def __init__(self):
        self._factory_manager: FactoryManager = None
        self._data_source: AbstractDataSource = None

    def init(self, factory_manager: FactoryManager, data_source: AbstractDataSource):
        self._factory_manager = factory_manager
        self._data_source = data_source

    def snapshot(self):
        session: AbstractSession = self._data_source.get_session()

        print("\t\tSimulationMonitor.snapshot()")

        session.close()

    def send_res_history(self, plan_version_dict: dict, simulation_dict: dict):
        """
        Gantt Chart 에 표현될 Resource 별 Work History 이력을 담은 리스트 반환
        :return:
        """
        plan_version: str = plan_version_dict.get('PLAN_VER_ID')
        simulation_id: str = simulation_dict.get('SIM_ID')

        resource_history: list = self._factory_manager.get_resource_history(plan_version, simulation_id)
        HistoryDAO.instance().execute(
            session=self._data_source.get_session(),
            data_list=resource_history
        )
        return resource_history
