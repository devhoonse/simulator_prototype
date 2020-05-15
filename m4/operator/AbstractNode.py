from abc import *
import datetime
from typing import List, Dict

from ..constraint.AbstractConstraint import AbstractConstraint
from ..process.Item import Item


class AbstractNode(metaclass=ABCMeta):
    """
    Abstract Node
        - ..operator.Inventory
        - ..operator.Process

    * Route.run() 내에서 사용되는 주요 메서드들만 추상화
    """

    def __init__(self, node_type: str):
        self.node_type = node_type

    @abstractmethod
    def get_items(self, item_id: str, work_order_id: str) -> List[Item]:
        """
        해당 노드에서 처리 완료된 Item(들)의 리스트를 get 하는 처리
        fetch와 달리 삭제하지 않음, 완료 Item 목록 확인 용도
        :return:
        """

    @abstractmethod
    def check_available(self, date: datetime.datetime, item_id: str, quantity: float, move_time: int):
        """
        check Available status
        Inventory : CapaConstraint를 체크
        Process : ProcessResource의 queue 사이즈 체크, Time/Capa Constraint 체크
        :param : date
        :param : item_id
        :param : quantity
        :param : move_time
        :return : Inventory 일 경우 가용 여부, Process일 경우 Resource ID
        """

    @abstractmethod
    def fetch(self, time_index: int, date: datetime.datetime, item_id: str, work_order_id: str, quantity: float = 0):
        """
        다음 노드로 보낼 준비가 된 Item 목록으로부터 Item 을 get & remove 처리
        :return:
        """

    @abstractmethod
    def put(self, time_index: int, date: datetime.datetime, item: Item, move_time: int, target_id: str):
        """
        현재 노드에 Item 을 받아오는 처리
        :return:
        """

    @abstractmethod
    def run(self, time_index: int, date: datetime.datetime, is_off_day: bool, off_day_type: str,
            factory_const: AbstractConstraint):
        """
        aging 및 이벤트 발생 처리
        :return:
        """

    def plan_input_quantity(self, quantity: float, item_id: str = ''):
        """
        Backward 시에 현재 Node 에서 처리 가능한 제약에 맞도록 생산 Plan Quantity 를 분할
        :param item_id:
        :param quantity:
        :return:
        """
