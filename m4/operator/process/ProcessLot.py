
import datetime
import logging
from collections import defaultdict
from typing import List, Dict

from ..process.Lot import Lot
from ..process.ProcessQueue import ProcessQueue
from m4.process.ProcessException import ProcessException
from m4.process.Item import Item
from m4.util.LogHandler import LogHandler
from ...util.DateTimeUtility import DateTimeUtility


class ProcessLot(object):
    """
    Process Lot Object
    Machine 객체에 종속되어 Machine 이 할당받은 Lot 을 처리하는 이벤트를 수행하는 클래스
    Setup 객체와 Lot 객체를 포함하며
    Machine 이 Lot 인스턴스를 처리할 때
    Machine 의 Setup Type 변경이 필요할 경우 이를 수행한 후에 하도록 설계
    """

    def __init__(self):
        """
        생성자 :
        """

        self.process_id: str = ""                       # Process ID
        self.resource_id: str = ""                      # Resource ID
        self.name: str = ""

        # MOVE -> QUEUE -> (SETUP) -> PROCESS
        self._moves: list = []                      # 현재 Process 위치로 오는 중인 Item 들의 시간 정보를 관리하는 dict
        self._queue: ProcessQueue = ProcessQueue()  # 이전 Route 로부터 도착한 Item 들의 QUEUE 대기열
        self._lot: Lot = None                       # 현재 처리중인 Item, Idle 일 경우 None

        # 다음 Router로 보낼 처리 완료 Item 들을 보관
        self._waits: dict = defaultdict(list)             # { ItemCode : [..., Item, ...] }

        # Resource History 관리용
        self._history: List[Dict[str, ...]] = []

        #
        self._logger: logging.Logger = LogHandler.instance().get_logger()

    def init(self, info: dict):
        """
        self._logger 가 log 출력 시 표시할 id, name 정보 세팅
        :return: void
        """
        self.process_id = info['PROC_ID']
        self.resource_id = info['RESC_ID']
        self.name = info['BOR_NM']

        self._queue.init(max_queue_size=info['MAX_QUEUE_SIZE'])

    def put(self, time_index: int, date: datetime.datetime, item: Item, move_time: int):
        if move_time != 0:
            lot: Lot = Lot(item, time_index, date, "MOVE", move_time)
            self._moves.append(lot)
            lot.archive(time_index=time_index, date=date, action="MOVE START", location=self.name)  # Todo: Action Name ?

            return lot

        lot: Lot = Lot(item, time_index, date, "QUEUE")
        putted: bool = self._queue.put(lot, time_index, date)

        if self._lot is None:
            lot = self._queue.get()
            if lot is None:
                raise ProcessException(
                    f"[Process Lot {self.process_id}:{self.resource_id}:{self.name}]"
                    f" : {item.item_id}:{item.work_order_id} - illegal Lot from queue")

            item = lot.get_item()
            if item.get_setup_time() > 0:
                lot.process(time_index, date, "SETUP", item.get_setup_time())
                lot.archive(time_index=time_index, date=date, action=f"SETUP START", location=self.name)    # Todo : Action Name ?
                self._append_history_step(date, item, 'SETUP')
                self._lot = self._queue.fetch()
            else:
                lot.process(time_index, date, "PROCESS", item.get_process_time())
                lot.archive(time_index=time_index, date=date, action=f"PROCESS START",
                            location=self.name)  # Todo : Action Name ?
                self._end_history_step(date)
                self._append_history_step(date, item, 'PROCESS')

        return lot

    def run(self, time_index: int, date: datetime.datetime, is_off_day: bool, off_day_type: str):

        if self._lot is not None:
            # Todo: 현재 시점이 Off Day 구간 내에 있는 경우,
            #  Divisible (Y/N/I) 타입에 따라 tick 가능 여부 판단 로직 필요
            self._lot.run()
            self._restart_history_step(date)

            if self._lot.is_end():
                item: Item = self._lot.get_item()
                if self._lot.get_status() == "SETUP":
                    self._lot.process(time_index, date, "PROCESS", item.get_process_time())
                    # Todo: Action Name ?
                    self._lot.archive(time_index=time_index, date=date,
                                      action="PROCESS START", location=self.name)
                    self._end_history_step(date)
                    self._append_history_step(date, item, 'PROCESS')
                else:
                    self._waits[item.item_id].append(item)
                    self._lot = None
                    self._end_history_step(date)

        self._queue.run()

        self._run_moves(time_index=time_index, date=date)
        # if len(self.arrived_items) > 0:
        #     self.receive_arrived(time_index, date)  # Move 가 완료된 Lot 들을 Que 에 등록

        if self._lot is None:
            lot = self._queue.get()
            if lot is None:
                return

            item = lot.get_item()
            if item.get_setup_time() > 0:
                lot.process(time_index, date, "SETUP", item.get_setup_time())
                lot.archive(time_index=time_index, date=date, action=f"SETUP START", location=self.name)    # Todo: Action Name ?
                self._append_history_step(date, item, 'SETUP')

            else:
                lot.process(time_index, date, "PROCESS", item.get_process_time())
                lot.archive(time_index=time_index, date=date, action=f"PROCESS START", location=self.name)  # Todo: Action Name ?
                self._end_history_step(date)
                self._append_history_step(date, item, 'PROCESS')

            self._lot = self._queue.fetch()

    def not_run(self, date: datetime.datetime):
        self._end_history_step(date)

    def _end_history_step(self, date: datetime.datetime):
        if len(self._history) == 0:
            return

        if not self._history[-1].get('END_DT_HMS'):
            self._history[-1].update({
                'END_DT_HMS': date,
                'DUR': date - self._history[-1]['START_DT_HMS']
            })

    def _restart_history_step(self, date: datetime.datetime):
        if len(self._history) == 0:
            return

        if self._history[-1].get('END_DT_HMS'):
            self._history.append(
                {'CURR_LOC_ID': self.process_id,
                 'CURR_RESOURCE_ID': self.resource_id,
                 'NEXT_LOC_ID': 'TODO',
                 'LOT_ID': 'TODO',
                 'WORK_ORDER_ID': self._history[-1].get('WORK_ORDER_ID', ''),
                 'ORDER_ITEM_ID': self._history[-1].get('ORDER_ITEM_ID', ''),
                 'ITEM_ID': self._history[-1].get('ITEM_ID', ''),
                 'PROD_QTY': self._history[-1].get('PROD_QTY', ''),
                 'EVENT': self._history[-1].get('EVENT', ''),
                 'START_DT_HMS': date}
            )

    def _append_history_step(self, date: datetime.datetime, item: Item, event_id: str):
        self._history.append(
            {'CURR_LOC_ID': self.process_id,
             'CURR_RESOURCE_ID': self.resource_id,
             'NEXT_LOC_ID': 'TODO',
             'LOT_ID': 'TODO',
             'WORK_ORDER_ID': item.get_work_order_id(),
             'ORDER_ITEM_ID': item.get_order_item_id(),
             'ITEM_ID': item.get_item_id(),
             'PROD_QTY': item.get_quantity(),
             'EVENT': event_id,
             'START_DT_HMS': date
             }
        )

    def _run_moves(self, time_index: int, date: datetime.datetime):
        arrived_lots: list = []
        for obj in self._moves:
            lot: Lot = obj
            lot.run()
            if lot.is_end():
                putted: bool = self._queue.put(lot, time_index, date)
                if putted:
                    lot.archive(time_index=time_index, date=date, action="QUEUE IN", location=self.name)
                    arrived_lots.append(lot)
        for obj in arrived_lots:
            self._moves.remove(obj)

    def is_available(self, date: datetime.datetime, item_id: str, quantity: float, move_time: int):
        # Todo : 이동 중인 Item 처리(?)
        is_available: bool = \
            (self._queue.get_available_size() - len(self._moves) > 0)
        return is_available

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

        wait_quantity: float = self.get_wait_quantity(item_id, work_order_id)
        if quantity != 0:
            if wait_quantity < quantity:
                return []
            elif wait_quantity > quantity:
                # Fixme: 수량 초과하는 경우 ?
                self._logger.debug(
                    f"[Process Lot {self.process_id}:{self.resource_id}:{self.name}] : {item_id}:{work_order_id}"
                    f" - wait quantity exceed fetch quantity"
                )

        wait_items: List[Item] = self.get_wait_items(item_id, work_order_id)
        cut_items: list = []
        fetch_items: list = []
        remain_qty: float = quantity
        while remain_qty > 0:
            for obj in wait_items:
                if remain_qty == 0:  # for Loop 안에서 수량 처리가 모두 끝날 경우 대비
                    break

                item: Item = obj
                item_qty: float = item.get_quantity()
                if item_qty <= remain_qty:
                    # 그대로 fetch
                    fetch_items.append(self._pop(item_id, item))
                    remain_qty -= item_qty
                else:
                    # Cut 필요
                    fetch_items.append(item.cut(time_index, date, self.resource_id, remain_qty))
                    cut_items.append(item)
                    remain_qty = 0
                    break

        # items = []
        # for item in wait_items:
        #     items.append(self._pop(item_id, item))

        self._logger.info(
            f"[Process Lot {self.process_id}:{self.resource_id}:{self.name}] : {item_id}:{work_order_id}"
            f" - fetched {quantity} from {len(fetch_items)} items")

        return fetch_items

    def _pop(self, item_id: str, item: Item):
        """
        stock 에서 remove 하는 처리
        :param item:
        :return:
        """
        # self._stock[item_id].remove(item)
        return self._waits[item_id].pop(self._waits[item_id].index(item))

    def get_quantity(self, item_id: str, work_order_id: str):
        """
        Process.fetch() 시에 수량 파악을 위한 계산 메서드
        :param item_id: 수량 파악 대상 품목 id
        :param work_order_id: 수량 파악 대상 주문 id
        :return: float
        """
        return \
            self.get_move_quantity(item_id=item_id, work_order_id=work_order_id) + \
            self.get_queue_quantity(item_id=item_id, work_order_id=work_order_id) + \
            self.get_process_quantity(item_id=item_id, work_order_id=work_order_id) + \
            self.get_wait_quantity(item_id=item_id, work_order_id=work_order_id)

    def get_move_quantity(self, item_id: str, work_order_id: str) -> float:

        move_items: list = [lot.get_item() for lot in self._moves]

        items = []
        for item in move_items:
            if item.item_id != item_id or item.work_order_id != work_order_id:
                continue
            items.append(item)

        return sum([
            item.get_quantity() for item in items
        ])

    def get_queue_quantity(self, item_id: str, work_order_id: str) -> float:

        queue_items: list = [lot.get_item() for lot in self._queue]

        items = []
        for item in queue_items:
            if item.item_id != item_id or item.work_order_id != work_order_id:
                continue
            items.append(item)

        return sum([
            item.get_quantity() for item in items
        ])

    def get_process_quantity(self, item_id: str, work_order_id: str) -> float:

        process_items: list = [] if self._lot is None else [self._lot.get_item()]

        items = []
        for item in process_items:
            if item.item_id != item_id or item.work_order_id != work_order_id:
                continue
            items.append(item)

        return sum([
            item.get_quantity() for item in items
        ])

    def get_wait_quantity(self, item_id: str, work_order_id: str) -> float:

        wait_items: list = self._waits.get(item_id, [])

        items = []
        for item in wait_items:
            if item.work_order_id != work_order_id:
                continue
            items.append(item)

        return sum([
            item.get_quantity() for item in items
        ])

    def get_wait_items(self, item_id: str, work_order_id: str) -> List[Item]:
        """
        get items
        :param : item_id
        :param : quantity
        :return : List[Item]
        """
        # Todo : 수정 필요
        wait_items: list = self._waits.get(item_id, [])
        items = []
        for item in wait_items:
            if item.work_order_id != work_order_id:
                continue
            items.append(item)
        return items

    def get_history(self):
        return self._history

    @property
    def status(self):
        if self._lot is None:
            return "IDLE"
        return self._lot.get_status()
