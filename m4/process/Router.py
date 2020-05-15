import copy
from typing import List

from ..operator.AbstractNode import AbstractNode
from m4.operator.process.Lot import Lot
from m4.operator.Inventory import Inventory
from m4.operator.Process import Process
from m4.process.Item import Item


class Router(object):
    """
        Route Object
        Lot Control
    """
    # route_location: AbstractRouteNode

    def __init__(self):
        self.route_id: str = ''         # Current Location 기준
        self.plant_id: str = ''
        self.route_type: str = ''
        self._production_orders: list = []

        # Route 연결 정보
        self.current_route: AbstractNode = None   # Route Location
        self.previous_route_list: List[AbstractNode] = []
        self.next_route_list: list = []
        self.curr_to_next_route_dict: dict = {}
        self._loc_to_route_dict: dict = {}

    def init(self,
             route_id: str,
             route_location: object,
             route_type: str,
             previous_route_list: list,
             next_route_list: list,
             curr_to_next_route_dict: dict):
        self.route_id = route_id
        self.current_route = route_location
        self.route_type = route_type
        self.previous_route_list = previous_route_list
        self.next_route_list = next_route_list
        self.curr_to_next_route_dict = curr_to_next_route_dict

    def run_(self, run_time: dict):
        """
        AbstractNode Pseudo Code : 다형성 활용 간소화
        ** 한 Runtime 내에서의 동작 **
            Simulation() {
                for runtime in scheduleManager {
                    Route.run() {
                        <Node n> run -> <Node n> _check -> <Node n-1> fetch -> <Node n> put -> ...
                        <Node n-1> run -> <Node n-1> _check -> <Node n-2> fetch -> <Node n-1> put -> ...
                            ...
                        <Node 2> run -> <Node 2> _check -> <Node 1> fetch -> <Node 2> put
                    }
                }
            }
        :return: void
        """

        # self.current_route.fetch()    # 마지막 Inventory Route 에서도 읿반적으로 동작하려면 여기서 하면 안될 것으로 생각
        self.current_route.run(time_index=run_time['index'], date=run_time['date'])                            # 1. 현재 Route 상황 해소

        for obj in self.previous_route_list:                # 2. 이전 각 노드들로부터
            previous_route: AbstractNode = obj

            waiting_items = previous_route.get_items()      # 2. 받아올 수 있는 item 별로
            for obj_ in waiting_items:
                item: Item = obj_

                work_order_id: str = None
                move_time: int = None

                # 2. 현재 노드에 할당 가능한 지 체크
                if not self.current_route.check(date=run_time['date'], item_id=item.item_id,
                                                quantity=item.get_quantity(), move_time=move_time):
                    return  # 3-1. 현재 위치에 해당 Item 을 할당할 수 없을 경우 동작 그만

                # 3-2. 현재 노드에 해당 Item을 할당할 수 있다면 이전 Route 에서 Fetch
                items: List[Item] = previous_route.fetch(time_index=run_time['index'],
                                                         date=run_time['date'],
                                                         item_id=item.item_id,
                                                         work_order_id=work_order_id,
                                                         quantity=item.get_quantity())
                # 4. Fetch 한 Item 들을 현재 노드에 Put
                for item in items:
                    self.current_route.put(time_index=run_time['index'],
                                           date=run_time['date'],
                                           item=item, move_time=move_time,
                                           target_id=None)

    def run(self, run_time: dict):
        """

        :return:
        """
        print(f"\t\t\tRunning Route: {self.route_id} ")    # Debugging Log

        # Step1.
        if isinstance(self.current_route, Process):
            pass

        elif isinstance(self.current_route, Inventory):
            inv_item_dict = self.current_route.get_item_dict()
            curr_capa = self._get_inv_item_qty(inv_item_list=inv_item_dict)
            max_capa = self.current_route.get_constraint().max_quantity
            available_capa = max_capa - curr_capa

            if available_capa > 0:
                for previous_route in self.previous_route_list:
                    # 이전 Route가 Process 인 경우
                    if isinstance(previous_route, Process):
                        pass

                    # 이전 Route가 inventory 인 경우
                    elif isinstance(previous_route, Inventory):
                        previous_item_dict = previous_route.get_item_dict()
                        for prev_item in previous_item_dict.values():
                            prev_stock_list: list = prev_item
                            for prev_stock in prev_stock_list:
                                prev_stock_obj: Item = prev_stock
                                # if prev_stock_obj.get_quantity() < available_capa:
                                if self.check(item=prev_stock_obj, available_capa=available_capa):
                                    fetched_items = previous_route.fetch(time_index=run_time['index'],
                                                                         date=run_time['date'],
                                                                         item_id=prev_stock_obj.item_id,
                                                                         work_order_id=prev_stock_obj.work_order_id,
                                                                         quantity=0)      # 이전 route item fetch 처리
                                    for fetched_item in fetched_items:
                                        self.current_route.put(time_index=run_time['index'],
                                                               date=run_time['date'],
                                                               item=prev_stock_obj,
                                                               move_time=0)    # 현재 route로 item put 처리
                    else:
                        raise AssertionError(print("Error: 존재하지 않는 type"))
                pass

        else:
            raise AssertionError("Error: 존재하지 않는 type")

    def check(self, item: Item, available_capa: float):
        return item.get_quantity() < available_capa

    # def check(self, route_type: str, item: Item, available_capa: float):
    #     if route_type == "PROC":
    #         pass
    #
    #     elif route_type == "INV":
    #         return item.get_quantity() < available_capa

        # # Step1. 현재 route에 item이 존재하는지 확인
        # route_item_list = curr_node.get_item_list()
        # route_item_count = len(route_item_list)

        # # Step2. 현재 route에 item이 존재하는 경우
        # if route_item_count > 0:
        #     check_count = 1
        #     while route_item_count >= check_count:
        #         for route_item in route_item_list.values():
        #             for item in route_item:
        #                 next_item_id, route = self.curr_to_next_route_dict.get(item.item_id, [])
        #                 if isinstance(route, Inventory):
        #                     print("")
        #                 if isinstance(route, Process):
        #                     print("")
        #
        #                 print("")
        #         check_count += 1

        # next_nodes = self._next_locations

        # Pseudo Code
        # print(f"\t\t\t\tRunning Post Nodes...")
        # for next_node in next_nodes:
        #     next_node.run()
        # print(f"\t\t\t\tRunning Prior Nodes...")
        # curr_node.run()
        # print(f"\t\t\t\tChecking Post Nodes...")
        # for next_node in next_nodes:
        #     next_node.check()
        # print(f"\t\t\t\tPutting Item to Post Nodes...")
        # for next_node in next_nodes:
        #     next_node.put(item=curr_node.fetch())

    def set_production_orders(self, production_orders: list):
        self._production_orders = production_orders

    def _resize_lot(self, lot: Lot):
        """

        :param lot: lot Object Data
        :return: resizing 한 lot list
        """
        process = self.curr_to_next_route_dict[lot.curr_loc_id][1]
        check, min_lot_size, max_lot_size = process.check_need_to_resize_lot(lot=lot)

        if check is False:
            return [lot]

        else:
            quotient = int(lot.qty // max_lot_size)
            remainder = lot.qty % max_lot_size
            resized_lot_list = []

            for i in range(quotient):
                temp_lot = copy.copy(lot)
                temp_lot.id = lot.id + "_" + str(i+1)
                temp_lot.qty = max_lot_size
                resized_lot_list.append(temp_lot)

            # 나머지 lot 추가 처리
            if remainder > 0:
                temp_lot = copy.copy(lot)
                if remainder < min_lot_size:
                    temp_lot.id = lot.id + "_" + str(quotient + 1)
                    temp_lot.qty = min_lot_size
                    resized_lot_list.append(temp_lot)
                else:
                    temp_lot.id = lot.id + "_" + str(quotient + 1)
                    resized_lot_list.append(temp_lot)

        return resized_lot_list

    def transfer(self):
        # 다음 단계로 갈 수 있는 이동 가능 항목을 찾는다(우선순위가 달린 이동 가능 항목)
        # check next location available 결과가 리스트
        # 생산 우선순위를 결정
        # fetch item
        # put item (Inventory : stocks에 item을 추가, Process : Resource에 ProcessLot을 생성(ProcessLot안에 Lot이 존재)
        pass

    # def check_availability(self, arg):
    #     process: Process = FactoryManager.instance().get_process(process_id="...")
    #     if process is None:
    #         pass
    #     else:
    #         resource: Resource = process.get_resource(resource_id="...")

    def _get_inv_item_qty(self, inv_item_list: dict):
        curr_qty = 0
        for inv_item in inv_item_list.values():
            for item in inv_item:
                itemObj: Item = item
                curr_qty += itemObj.get_quantity()

        return round(curr_qty, 3)
