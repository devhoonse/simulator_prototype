import datetime
from collections import defaultdict
from itertools import chain
from typing import List

from m4.util.LogHandler import LogHandler
from m4.operator.AbstractNode import AbstractNode
from m4.process.ProcessException import ProcessException
from ..constraint.AbstractConstraint import AbstractConstraint
from ..process.Item import Item
from m4.operator.Runtime import Runtime
from ..constraint.CapacityConstraint import CapacityConstraint


class Inventory(AbstractNode):
    """
    Inventory Object
    각 공정 단계 별 중간 제품 보관 창고를 구현한 클래스
    Route 로부터 Lot 이 할당되었을 상황에서의
    실제 처리 동작을 수행하도록 설계
    """

    def __init__(self):
        """
        생성자 :
        """
        super().__init__("INV")

        # 2-1. Public
        self.id: str = ""                       # Inventory 일련번호
        self.name: str = ""                     # Inventory 명칭
        self.plant_id: str = ""
        self.type: str = ""

        # 2-2. Private
        # logger
        self._logger = LogHandler.instance().get_logger()
        self._constraints: CapacityConstraint = None

        # Item별로 재고
        self._moves: list = []      # 이전 장소 -> 현재 인벤토리 이동 관리 리스트
        self._stock: dict = {}      # { ItemID: [..., Item, ...] }

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.type}) {self.id} at {id(self):#018x}>"

    def init(self, info: dict, item_constraint_data: list):
        self.id = info['INV_ID']
        self.name = info['INV_NM']
        self.plant_id = info['PLANT_ID']
        self.type = info['INV_TYP']

        self._constraints = CapacityConstraint()
        self._constraints.init(info['MAX_QTY'], item_constraint_data)

    def _get_moves_dict(self):
        ret: dict = defaultdict(list)
        for obj in self._moves:
            item: Item = obj.get_item()
            ret[item.item_id].append(item)
        return ret

    def check_available(self, date: datetime.datetime, item_id: str, quantity: float, move_time: int):
        """
        check Available status
        Inventory : CapaConstraint를 체크
        Process : ProcessResource의 queue 사이즈 체크, Time/Capa Constraint 체크
        :param : item_id
        :param : quantity
        :param : move_time
        :return : Inventory일 경우 가용 여부, Process일 경우 Resource ID
        """
        moves_dict: dict = self._get_moves_dict()
        items = defaultdict(list)
        for key, val in chain(self._stock.items(), moves_dict.items()):
            items[key].extend(val)

        if self._constraints.check(item_id, items, quantity) is None:
            return self.id, quantity

        return None

    def fetch(self,
              time_index: int,
              date: datetime.datetime,
              item_id: str,
              work_order_id: str,
              quantity: float = 0):
        """
        get and remove item quantity
        :param : item_id
        :param : quantity
        :return : Item
        """
        if quantity == 0:   # 현재 위치에 대한 내보내야 할 Plan Quantity 가 0 이면 동작 할 필요 없으므로
            return []

        stock_items: List[Item] = self.get_items(item_id, work_order_id)
        if not stock_items:
            # Item ID, Work Order ID 동시 일치하는 Item 이 stock 에 없을 경우
            return []
        stock_items.sort(key=lambda x: -x.get_quantity())

        stock_quantity: float = sum([obj.get_quantity() for obj in stock_items])
        fetch_items: list = []
        if stock_quantity < quantity:  # Todo: fetch 해야 할 수량이 모자랄 경우
            if self.type == "RMINV":
                # Todo: 출발지 창고일 경우 - Route 에 있는 flag 가 False 일 경우 BackwardStepPlan 혹은 내보내는 Item 재조정 필요
                return []
            elif self.type == "IPINV":
                # 중간 창고일 경우 - 일단 지금은 빈 리스트 리턴하고 나중에 수량이 맞춰졌을 때 fetch 하도록
                return []
            else:
                # 최종 창고일 경우 - 최종 창고 Route 에서 fetch 메서드 실핼될 일 없음
                return []
        elif stock_quantity == quantity:
            # 수량이 맞으므로 전부 그대로 fetch 하고 조건문 블록 뒤에서 _remove 처리
            fetch_items = [self._pop(item_id, item) for item in stock_items]
        else:   # 가져 갈 수량보다 재고 수량이 더 많을 경우
            remain_qty: float = quantity
            cut_items: list = []
            while remain_qty > 0:
                for obj in stock_items:
                    if remain_qty == 0:     # for Loop 안에서 수량 처리가 모두 끝날 경우 대비
                        break

                    item: Item = obj
                    item_qty: float = item.get_quantity()
                    if item_qty <= remain_qty:
                        # 그대로 fetch
                        fetch_items.append(self._pop(item_id, item))
                        remain_qty -= item_qty
                    else:
                        # Cut 필요
                        fetch_items.append(item.cut(time_index, date, self.id, remain_qty))
                        cut_items.append(item)
                        remain_qty = 0
                        break

        self._logger.info(
            f"[Inventory {self.id}:{self.name}] : {item_id}:{work_order_id}"
            f" - fetched {quantity} from {len(fetch_items)} items")

        return fetch_items

    def put(self, time_index: int, date: datetime.datetime, item: Item, move_time: int, target_id: str):
        """
        put item
        Inventory, ProcessResource 의 ProcessLot 의 moves에 Item 추가
        :param : item
        """
        # Item 위치 정보 업데이트
        item.set_location_id(self.id)

        # item archive 처리
        item.archive(time_index=time_index, date=date, action="INVENTORY PUT", location=self.id)  # Todo: Action Name ?
        item.archive(time_index=time_index, date=date, action="MOVE START", location=self.id)  # Todo: Action Name ?

        if move_time != 0:
            runtime: Runtime = Runtime(item, time_index, date, move_time)

            self._moves.append(runtime)
            return

        item.archive(time_index=time_index, date=date, action="STOCK IN", location=self.id)  # Todo: Action Name ?
        items: list = self._stock.get(item.item_id, [])
        items.append(item)
        self._stock.update({item.item_id: items})

    def run(self, time_index: int, date: datetime.datetime, is_off_day: bool, off_day_type: str,
            factory_const: AbstractConstraint = None):
        """
        FactorySimulator에서 run 발생 시 aging 처리 전파
        Todo: 공장 달력상 휴무일일 시점에도 move 진행 ?
        :param factory_const:
        :param time_index:
        :param date:
        :param is_off_day:
        :param off_day_type:
        """

        arrived_items: list = []
        for obj in self._moves:
            runtime: Runtime = obj
            runtime.run()
            if runtime.is_end():
                runtime.archive(time_index=time_index, date=date, action="STOCK IN",
                                location=self.name)  # Todo: Action Name ?

                item: Item = runtime.get_item()
                items: list = self._stock.get(item.item_id, [])
                items.append(item)
                self._stock.update({item.item_id: items})

                arrived_items.append(runtime)

        for obj in arrived_items:
            self._moves.remove(obj)

    def _pop(self, item_id: str, item: Item):
        """
        stock 에서 remove 하는 처리
        :param item:
        :return:
        """
        return self._stock[item_id].pop(self._stock[item_id].index(item))

    def get_item_dict(self):
        return self._stock

    def set_backward_peg_items(self, plan_start_date: datetime.datetime, backward_peg_items_dict: dict):
        """
        Backward pegging 결과 정보를 stock 내 Item 에 반영
        :param plan_start_date: 계획 시작 시점 정보 - Item 인스턴스마다 stock 에 put 되는 당시 archive 처리 위해 필요
        :param backward_peg_items_dict: Backward 전개 결과 Pegging 여부 정보가 포함된 Item 정보
        :return: void
        """
        # 기존 로직 - 단순 덮어쓰기로 인해
        # 앞서 FactoryBuilder 를 통해 세팅된 재고들 중
        # backward_peg_items_dict 에 없는 Item 들이 없어지는 현상 있었음
        # self._stock = stock_dict

        for item_id, item_infos in backward_peg_items_dict.items():
            for info in item_infos:
                stock_items: list = self._stock.get(info['ITEM_ID'], [])
                pegged_items: List[Item] = []

                remain_qty: float = info['PEG_QTY']
                cut_items: list = []
                while remain_qty > 0:
                    for obj in stock_items:
                        if remain_qty == 0:  # for Loop 안에서 수량 처리가 모두 끝날 경우 대비
                            break

                        item: Item = obj
                        item_qty: float = item.get_quantity()
                        if item_qty <= remain_qty:
                            # 그대로 fetch
                            pegged_item: Item = self._pop(item_id, item)
                            pegged_item.init(
                                item_id=info['ITEM_ID'],
                                location_id=info['INV_ID'],
                                quantity=pegged_item.get_quantity(),
                                work_order_id=info['WORK_ORDER_ID'],
                                order_item_id=info['ORDER_ITEM_ID'],
                                order_quantity=info['ORDER_QTY'],
                                req_quantity=info['REQ_QTY'],
                                peg_quantity=info['PEG_QTY'],
                                due_date=None,
                                setup_time=pegged_item.get_setup_time(),
                                process_time=pegged_item.get_process_time(),
                                lpst=info['LPST']
                            )
                            pegged_items.append(pegged_item)
                            remain_qty -= item_qty
                        else:
                            # Cut 필요
                            pegged_item: Item = item.cut(0, plan_start_date, self.id, remain_qty)
                            pegged_item.init(
                                item_id=info['ITEM_ID'],
                                location_id=info['INV_ID'],
                                quantity=pegged_item.get_quantity(),
                                work_order_id=info['WORK_ORDER_ID'],
                                order_item_id=info['ORDER_ITEM_ID'],
                                order_quantity=info['ORDER_QTY'],
                                req_quantity=info['REQ_QTY'],
                                peg_quantity=info['PEG_QTY'],
                                due_date=None,
                                setup_time=pegged_item.get_setup_time(),
                                process_time=pegged_item.get_process_time(),
                                lpst=info['LPST']
                            )
                            pegged_items.append(pegged_item)
                            cut_items.append(item)
                            remain_qty = 0
                            break
                self._stock.update(
                    {info['ITEM_ID']: self._stock.get(info['ITEM_ID'], []) + pegged_items}
                )

    def plan_input_quantity(self, quantity: float, item_id: str = ''):
        item_capa: float = self._constraints.get_item_capa_constraint(item_id)
        if quantity <= item_capa:
            return [(self.id, quantity)]

        rslt: list = []
        while quantity > 0:
            qty: float = min(quantity, item_capa)
            rslt.append((self.id, qty))
            quantity -= qty
            if quantity <= 0:
                return rslt
        return rslt

    def get_constraint(self):
        return self._constraints

    def get_items(self, item_id: str, work_order_id: str) -> List[Item]:
        items: List[Item] = self._stock.get(item_id, [])
        if not items:
            return items
        return [item for item in items
                if item.work_order_id in [work_order_id]]
