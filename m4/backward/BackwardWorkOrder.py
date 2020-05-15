import copy
import datetime
import math
from datetime import timedelta

# from m4.backward.BackwardManager import BackwardManager
from m4.backward.BackwardStepPlan import BackwardStepPlan
from m4.manager.FactoryManager import FactoryManager
from m4.operator.Process import Process
from m4.operator.AbstractNode import AbstractNode
from m4.operator.process.ProcessResource import ProcessResource


class BackwardWorkOrder(object):

    def __init__(self):
        # self.backwardManager: BackwardManager = None
        self.time_unit_type: str = ''
        self.work_order_id: str = ''
        self.finished_item_id: str = ''
        self.location_id: str = ''
        self.work_order_qty: int = 0
        self.priority: int = 1
        self.dtl_priority: int = 1
        self.due_date: datetime.datetime = None

        self.item_route_chain_dict: dict = {}
        self.required_quantity: int = 0

        # Time
        self._setup_time_dict: dict = {}
        self._proc_time_dict: dict = {}
        self._move_time_dict: dict = {}

    def init(self,
             time_unit_type: str,
             setup_time_dict: dict,
             proc_time_dict: dict,
             move_time_dict: dict,
             work_order: dict,
             item_route_chain_dict: dict,
             final_inventory_id: str):
        """

        :return:
        """
        # self.backwardManager = backward_Manager
        self.time_unit_type = time_unit_type
        self.work_order_id = work_order['WORK_ORDER_ID']
        self.finished_item_id = work_order['ORDER_ITEM_ID']
        self.location_id = final_inventory_id
        self.work_order_qty = work_order['ORDER_QTY']
        self.priority = work_order['PRIORITY']
        self.dtl_priority = work_order['DTL_PRIORITY']
        self.due_date = datetime.datetime.strptime(work_order['DUE_DT'], "%Y%m%d%H%M%S")

        self.item_route_chain_dict = item_route_chain_dict
        self._setup_time_dict = setup_time_dict
        self._proc_time_dict = proc_time_dict
        self._move_time_dict = move_time_dict

    def process(self,
                peg_available_item_dict: dict,
                backward_step_plan_by_loc: dict,
                peg_result_dict: dict,
                use_backward_size: bool):
        """

        :return:
        """
        self.backward_step_plan_list = self._create_backward_step_plan(peg_available_item_dict=peg_available_item_dict,
                                                                       backward_step_plan_by_loc=backward_step_plan_by_loc,
                                                                       peg_result_dict=peg_result_dict,
                                                                       use_backward_size=use_backward_size)

        return self.backward_step_plan_list

    def _create_backward_step_plan(self,
                                   peg_available_item_dict: dict,
                                   backward_step_plan_by_loc: dict,
                                   peg_result_dict: dict,
                                   use_backward_size: bool):
        """

        :param peg_available_item_dict:
        :param backward_step_plan_by_loc:
        :param peg_result_dict:
        :return:
        """

        # get FactoryManager instance 가져오기
        # - Location 인스턴스 포인터를 가져오기 위해 필요
        # - Process 로 보내는 단계의 경우 Resource 의 min/max 범위 내에서 Quantity 결정되도록
        factory_manager: FactoryManager = FactoryManager.instance()

        # Pegging 결과가 반영된 Item 목록 dict
        after_peg_item_dict = peg_available_item_dict

        # Backward Process 초기 setting
        backward_step_plan_list = []
        step = 1
        curr_loc_id = self.location_id
        curr_item_id = self.finished_item_id
        lpst = self.due_date
        self.required_quantity = self.work_order_qty

        # Set Initial Plan
        init_plan = self._get_init_plan(step=step, location_id=curr_loc_id, item_id=curr_item_id, lpst=lpst)
        peg_qty, after_peg_item_dict = self._pegging(location_id=curr_loc_id,
                                                     item_id=curr_item_id,
                                                     peg_available_item_dict=after_peg_item_dict,
                                                     peg_result_dict=peg_result_dict,
                                                     lpst=lpst)
        init_plan.peg(peg_qty=peg_qty)
        backward_step_plan_list.append(init_plan)
        self._set_backward_step_plan_by_loc(plan=init_plan, backward_step_plan_by_loc=backward_step_plan_by_loc)

        for i in range(len(self.item_route_chain_dict)):
            step += 1
            next_loc_id, next_item_id = curr_loc_id, curr_item_id
            (curr_loc_id, curr_item_id) = self.item_route_chain_dict[(curr_loc_id, curr_item_id)]

            # Time Setting
            setup_time = self._setup_time_dict.get(curr_loc_id, 0)
            proc_time = self._proc_time_dict.get(curr_loc_id, 0)
            move_time = self._move_time_dict[(curr_loc_id, next_loc_id)]

            # lpst = self._calculate_lpst(lpst=lpst, setup_time=setup_time, proc_time=proc_time, move_time=move_time)

            # Location 및 Item 정보 setting
            # Todo: curr_loc(Process) 의 각 Resource 별 투입 가능 min / max 사이즈 고려하여
            #       BackwardStepPlan 이 여러 개로 쪼개져야 함
            #       ( use_backward_size 설정이 True 일 경우에 필요,
            #         False 일 경우, 있는 그대로 계산 후 Forward 에서 실행
            next_loc = factory_manager.get_location(next_loc_id)
            # input_plans: list = [self.required_quantity]
            # if type(next_loc) is Process:
            #     precision: int = factory_manager.get_location(next_loc_id).get_precision()
            #     # quantities = self.split_qty(self.required_quantity, entire_min_capa, entire_max_capa, precision)
            #     input_plans = next_loc.plan_input_quantity(self.required_quantity)
            input_plans = next_loc.plan_input_quantity(self.required_quantity, next_item_id)

            plans: list = []
            for info in input_plans:
                lpst = self._calculate_lpst(info, lpst, setup_time, proc_time, move_time)
                plan: BackwardStepPlan = BackwardStepPlan()
                plan.init(work_order_id=self.work_order_id,
                          finished_item_id=self.finished_item_id,
                          work_order_qty=self.work_order_qty,
                          remain_production_qty=info[1],
                          step=step,
                          location_id=curr_loc_id,
                          to_location_id=info[0],
                          item_id=curr_item_id,
                          due_date=self.due_date,
                          lpst=lpst)
                plans.append(plan)

            # Pegging
            if self.required_quantity > 0:
                peg_qty, after_peg_item_dict = self._pegging(location_id=curr_loc_id,
                                                             item_id=curr_item_id,
                                                             peg_available_item_dict=after_peg_item_dict,
                                                             peg_result_dict=peg_result_dict,
                                                             lpst=lpst)

                # Update Pegging
                # Todo: peg_qty 가 Plan 에 세팅된 Quantity 보다 클 경우 ?
                plans[-1].peg(peg_qty=peg_qty)

            backward_step_plan_list.extend(plans)
            for plan in plans:
                self._set_backward_step_plan_by_loc(plan=plan, backward_step_plan_by_loc=backward_step_plan_by_loc)

            self.required_quantity = sum(p.required_quantity for p in plans)

        return backward_step_plan_list

    @staticmethod
    def split_qty(qty: float, min_capa: int, max_capa: int, precision: int):
        qtys: list = [max_capa for i in range(int(qty//max_capa))]
        if qty % max_capa > 0:
            qtys.append(round(max(min_capa, qty % max_capa), precision))
        return qtys

    def _get_init_plan(self, step: int, location_id: str, item_id: str, lpst: datetime.datetime):
        plan: BackwardStepPlan = BackwardStepPlan()
        plan.init(work_order_id=self.work_order_id,
                  finished_item_id=self.finished_item_id,
                  work_order_qty=self.work_order_qty,
                  remain_production_qty=self.required_quantity,
                  step=step,
                  location_id=location_id,
                  to_location_id='',
                  item_id=item_id,
                  due_date=self.due_date,
                  lpst=lpst)

        return plan

    def _calculate_lpst(self, info: tuple, lpst: datetime.datetime, setup_time: int, proc_time: int, move_time: int):
        process_time: float = 0
        if proc_time > 0:
            process_time = math.ceil(info[1] / proc_time)    # Todo: Ceil 필요 여부 확인 필요
        if self.time_unit_type == 'HOUR':
            lpst = lpst - timedelta(hours=setup_time) - timedelta(hours=process_time) - timedelta(hours=move_time)
        elif self.time_unit_type == 'MI':
            lpst = lpst - timedelta(minutes=setup_time) - timedelta(minutes=process_time) - timedelta(minutes=move_time)
        elif self.time_unit_type == 'SEC':
            lpst = lpst - timedelta(seconds=setup_time) - timedelta(seconds=process_time) - timedelta(seconds=move_time)
        elif self.time_unit_type == 'DAY':
            lpst = lpst - timedelta(days=setup_time) - timedelta(days=process_time) - timedelta(days=move_time)
        else:
            return lpst
        return lpst

    def _pegging(self, location_id: str, item_id: str,
                 peg_available_item_dict: dict, peg_result_dict: dict,
                 lpst: datetime.datetime):
        peg_qty = 0
        key = (location_id, item_id)
        peg_available_item_list = peg_available_item_dict.get(key, [])
        peg_result_item_list = peg_result_dict.get(key, [])

        if peg_available_item_list != []:
            for peg_available_item in peg_available_item_list:
                if peg_available_item['STOCK_QTY'] > 0:
                    peg_result_item: dict = copy.deepcopy(peg_available_item)
                    peg_result_item['WORK_ORDER_ID'] = self.work_order_id
                    peg_result_item['ORDER_ITEM_ID'] = self.finished_item_id
                    peg_result_item['ORDER_QTY'] = self.work_order_qty
                    peg_result_item['REQ_QTY'] = self.required_quantity
                    peg_result_item['PEG_QTY'] = min(self.required_quantity, peg_available_item['STOCK_QTY'])
                    peg_result_item['LPST'] = lpst

                    peg_result_dict.update(
                        {key: peg_result_item_list + [peg_result_item]}
                    )

                    if self.required_quantity >= peg_available_item['STOCK_QTY']:
                        self.required_quantity -= peg_available_item['STOCK_QTY']
                        peg_qty += peg_available_item['STOCK_QTY']
                        peg_available_item['STOCK_QTY'] = 0
                    else:
                        peg_qty += self.required_quantity
                        peg_available_item['STOCK_QTY'] = round(peg_available_item['STOCK_QTY'] - self.required_quantity, 3)  # 자리수 Hard Coding
                        self.required_quantity = 0

            # for peg_available_item, peg_result_item in zip(peg_available_item_list, peg_result_item_list):
            #     if peg_available_item['STOCK_QTY'] > 0:
            #         if self.required_quantity >= peg_available_item['STOCK_QTY']:
            #
            #             peg_result_item['WORK_ORDER_ID'] = self.work_order_id
            #             peg_result_item['ORDER_ITEM_ID'] = self.finished_item_id
            #             peg_result_item['REQ_QTY'] = self.required_quantity
            #             peg_result_item['PEG_QTY'] = peg_available_item['STOCK_QTY']
            #             peg_result_item['LPST'] = lpst
            #
            #             self.required_quantity -= peg_available_item['STOCK_QTY']
            #             peg_qty += peg_available_item['STOCK_QTY']
            #             peg_available_item['STOCK_QTY'] = 0
            #             # peg_available_item_list.remove(peg_available_item)
            #
            #         else:
            #             peg_result_item['WORK_ORDER_ID'] = self.work_order_id
            #             peg_result_item['ORDER_ITEM_ID'] = self.finished_item_id
            #             peg_result_item['REQ_QTY'] = self.required_quantity
            #             peg_result_item['PEG_QTY'] = self.required_quantity
            #             peg_result_item['LPST'] = lpst
            #
            #             peg_qty += self.required_quantity
            #             peg_available_item['STOCK_QTY'] = round(peg_available_item['STOCK_QTY'] - self.required_quantity, 3)     # 자리수 Hard Coding
            #             self.required_quantity = 0

        # else:
        #     return peg_qty, peg_available_item_dict

        return peg_qty, peg_available_item_dict

    def _set_backward_step_plan_by_loc(self, plan: BackwardStepPlan, backward_step_plan_by_loc: dict):

        if plan.location_id not in backward_step_plan_by_loc.keys():
            backward_step_plan_by_loc.update({plan.location_id: [plan]})
        else:
            temp_list = backward_step_plan_by_loc.get(plan.location_id, [])
            temp_list.append(plan)
            backward_step_plan_by_loc.update({plan.location_id: temp_list})

    def _get_end_location(self):
        end_location = ''

        return end_location
