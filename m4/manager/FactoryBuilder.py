from typing import List, Dict
from collections import defaultdict

from m4.dao.AbstractSession import AbstractSession
from m4.dao.FactoryDAO import FactoryDAO
from m4.dao.FactoryScheduleDAO import FactoryScheduleDAO
from m4.dao.BomDAO import BomDAO
from ..ApplicationConfiguration import ApplicationConfiguration
from ..dao.InventoryDAO import InventoryDAO
from ..dao.ResourceDAO import ResourceDAO
from ..dao.ProcessDAO import ProcessDAO
from m4.operator.AbstractNode import AbstractNode
from ..dao.RouteNodeDAO import RouteDAO
from m4.operator.RouteAttribute import RouteAttribute
from ..constraint.ScheduleConstraint import ScheduleConstraint
from m4.operator.Route import Route
from ..operator.Inventory import Inventory
from ..operator.Resource import Resource
from ..operator.Process import Process
from m4.operator.Factory import Factory
from m4.process.Item import Item
from ..operator.RouteException import RouteException
from ..util.DateTimeUtility import DateTimeUtility
from ..manager.FactoryManager import FactoryManager

from m4.dao.DemandDAO import DemandDAO


class FactoryBuilder:
    # Demand
    _demand_list: list = []

    # Route 관련
    _routes: list = []  # OK
    _work_order_item_list: list = []    # OK
    _curr_to_next_route_dict: dict = {}   # OK
    _item_to_finished_item_dict: dict = {}     # OK     ****
    _start_location: str = ''
    _end_location: str = ''

    @classmethod
    def build(cls, plan_version_dict: dict, simulation_dict: dict, config: ApplicationConfiguration, session: AbstractSession):

        # config 객체로부터 설정 정보 받아오기
        use_backward_size: bool = bool(config.find('Backward', 'backward.res.size'))

        instance: Factory = Factory()

        factory_info, bom, work_order_master = cls._get_dao_data(session)

        schedule_constraint = cls._init_schedule_constraint(simulation_dict, session)

        inventories = cls._init_inventories(plan_version_dict, simulation_dict, session)

        cls._init_inv_start_end_location(simulation_dict, session)    # 임시

        resources = cls._init_resources(simulation_dict, session)

        processes = cls._init_processes(resources, simulation_dict, use_backward_size, session)

        routes = cls._init_routes(inventories, processes, work_order_master, simulation_dict, use_backward_size, session)

        # 공장 내 Route 객체들을 초기화
        # _next_to_curr_item_dict = cls._create_next_to_curr_item_dict(route_master=route_master)
        # _item_to_final_item_dict = cls._create_route_group(route_master=route_master)
        # routes = cls._init_routes(route_master=route_master,
        #                           inventories=inventories,
        #                           processes=processes)

        # Backward Tick 을 위한 Backward 방향 Route Sequence
        # _next_to_curr_item_dict = cls._create_next_to_curr_item_dict(route_master=route_master)
        # route_sequence = cls._get_route_sequence(routers=routes)

        # cls._init_routes(route_master=route_master)
        # work_order_master: list = cls._init_work_orders(work_order_master=work_order_master)

        instance.init(info=factory_info,
                      schedule_constraint=schedule_constraint,
                      inventories=inventories,
                      processes=processes,
                      work_order_master=work_order_master,
                      routes=routes)

        return instance

    @classmethod
    def _init_schedule_constraint(cls, simulation_dict, session: AbstractSession):
        """
        :param simulation_dict: simulation_dict 정보
        :param session: Abstract Session
        :return: ScheduleConstraint
        """

        # DAO 기준 정보 취득
        dao = FactoryScheduleDAO.instance()
        factory_schedule_id = simulation_dict['FACTRY_SCHDL_ID']
        max_priority = dao.select_max_priority(session, factory_schedule_id=factory_schedule_id)['data'][0][0]
        factory_schedule_data = dao.map(dao.select_constraint(session, factory_schedule_id=factory_schedule_id))

        # Schedule Constraint 초기화
        schedule_constraint: ScheduleConstraint = ScheduleConstraint()
        schedule_constraint.init(factory_schedule_data, max_priority)

        return schedule_constraint

    @classmethod
    def _init_inventories(cls, plan_version_dict: dict, simulation_dict: dict, session: AbstractSession):
        """
        :param simulation_dict: simulation_dict 정보
        :param session: Abstract Session
        :return: dict
        """
        # InventoryDAO로 부터 기준 정보 받아오기
        simulation_id = simulation_dict['SIM_ID']
        plan_start_date = DateTimeUtility.convert_str_to_date(plan_version_dict['START_DT_HMS'])
        dao: InventoryDAO = InventoryDAO.instance()
        inventory_data = dao.map(dao.select_route_inventory(session=session, simulation_id=simulation_id))
        item_dict: dict = dao.hash_map(dao.select_route_item(session, simulation_id=simulation_id), "INV_ID")
        item_constraint_dict: dict = dao.hash_map(dao.select_route_item_constraint(session, simulation_id=simulation_id), "INV_ID")

        inventories: dict = {}
        for inv in inventory_data:
            inventory = Inventory()
            item_constraint_data: list = item_constraint_dict.get(inv['INV_ID'], [])
            # if item_constraint_data is None:
            #     item_constraint_data = []
            inventory.init(inv, item_constraint_data)
            items: list = item_dict.get(inv['INV_ID'], [])
            for info in items:
                item: Item = Item()
                item.init(work_order_id=info.get('WORK_ORDER_ID', ''),
                          order_item_id=info.get('ORDER_ITEM_ID', ''),
                          item_id=info.get('ITEM_ID', ''),
                          location_id=info.get('LOC_ID', ''),
                          quantity=info.get('QTY', ''),
                          due_date=None)
                inventory.put(time_index=0, date=plan_start_date, item=item, move_time=0, target_id=inventory.id)

            inventories[inv['INV_ID']] = inventory
        return inventories

    @classmethod
    def _init_inv_start_end_location(cls, simulation_dict, session: AbstractSession):
        """
        :param simulation_dict: simulation_dict 정보
        :param session: Abstract Session
        :return: dict
        """
        simulation_id = simulation_dict['SIM_ID']
        dao: InventoryDAO = InventoryDAO.instance()
        inventory_data = dao.map(dao.select(session))

        for inv in inventory_data:
            if inv['INV_TYP'] == 'PDINV':
                FactoryBuilder._end_location = inv['INV_ID']
            elif inv['INV_TYP'] == 'RMINV':
                FactoryBuilder._start_location = inv['INV_ID']

    @classmethod
    def _init_resources(cls, simulation_dict, session: AbstractSession):
        """
        :param simulation_dict: simulation_dict 정보
        :param session: Abstract Session
        :return: dict
        """

        # ResourceDAO로 부터 기준 정보 받아오기
        simulation_id = simulation_dict['SIM_ID']
        dao: ResourceDAO = ResourceDAO.instance()
        resource_data = dao.map(dao.select_route_resource(session, simulation_id=simulation_id))
        constraint_dict: dict = dao.hash_map(dao.select_route_constraint(session, simulation_id=simulation_id), "RESC_ID")
        constraint_max_priority_dict = dao.hash_map(dao.select_route_constraint_max_priority(session, simulation_id=simulation_id), "RESC_ID")

        resources: dict = {}
        for res in resource_data:
            resource: Resource = Resource()

            constraint_data: list = constraint_dict.get(res['RESC_ID'], [])
            constraint_max_priority_data = constraint_max_priority_dict.get(res['RESC_ID'])
            constraint_max_priority = 0 if constraint_max_priority_data is None else constraint_max_priority_data[0]['PRIORITY']
            resource.init(res, constraint_data, constraint_max_priority)

            resources[res['RESC_ID']] = resource

        return resources

    @classmethod
    def _init_processes(cls, resources: dict, simulation_dict, use_backward_size: bool, session: AbstractSession):
        """
        :param resources: resources 객체
        :param simulation_dict: simulation_dict 정보
        :param session: Abstract Session
        :return: dict
        """

        # ProcessDAO로 부터 기준 정보 받아오기
        simulation_id = simulation_dict['SIM_ID']
        dao: ProcessDAO = ProcessDAO.instance()
        process_data = dao.map(dao.select_route_process(session, simulation_id=simulation_id))
        bor_dict: dict = dao.hash_map(dao.select_route_bor(session, simulation_id=simulation_id), "PROC_ID")

        processes: dict = {}
        for proc in process_data:
            process: Process = Process()
            process.init(proc)
            bor_data: list = bor_dict.get(proc["PROC_ID"], [])
            for bor in bor_data:
                process.add_process_resource(bor, resources[bor["RESC_ID"]], use_backward_size)

            processes[proc["PROC_ID"]] = process

        return processes

    @classmethod
    def _find_route_node(cls, inventories: dict, processes: dict, node_list: list, id_key: str, type_key: str):
        """
            find route node
        :param inventories:
        :param processes:
        :param id_key:
        :param type_key:
        :return: dict
        """
        ret = {}
        for node in node_list:
            node_id: str = node[id_key]
            if node[type_key] == 'INV':
                ret[node_id] = inventories.get(node_id)
            elif node[type_key] == 'PROC':
                ret[node_id] = processes.get(node_id)
            else:
                raise NotImplementedError(
                    f""
                )

        return ret

    @classmethod
    def _create_item_route_dict(cls,
                                inventories: dict, processes: dict, item_list: list, end_item_dict: dict,
                                id_key: str, type_key: str):
        """
        create item route dict
        :param inventories:
        :param processes:
        :param id_key:
        :param type_key:
        :return: dict
        """
        ret: dict = defaultdict(list)
        for item in item_list:
            item_id: str = item['ITEM_ID']
            # tups: list = ret.get(item_id, [])
            # is_end_item: bool = item_id not in end_item_dict.keys() \
            #                     and len([l for l in end_item_dict.values() if item_id in l]) > 0

            node_id: str = item[id_key]
            if item[type_key] == 'INV':
                node: AbstractNode = inventories.get(node_id)
            else:
                node: AbstractNode = processes.get(node_id)

            attr: RouteAttribute = RouteAttribute(from_item_id=item["ITEM_ID"],
                                                  to_item_id=item["NEXT_ITEM_ID"],
                                                  from_location_id=item["CURR_LOC_ID"],
                                                  to_location_id=item["NEXT_LOC_ID"],
                                                  from_location_type=item["CURR_LOC_TYP"],
                                                  to_location_type=item["NEXT_LOC_TYP"],
                                                  item_mix_code=item["ITEM_MIX_CD"],
                                                  route_conn_code=item["ROUTE_CONN_CD"],
                                                  priority=item["PRIORITY"],
                                                  ratio=item["RATIO"],
                                                  move_time=item["MOVE_TM"]
                                                  )

            # end_items: set = set(end_item_dict.get(attr.to_item_id, [])).union(set(end_item_dict.get(attr.from_item_id, [])))

            end_items: list = end_item_dict.get(attr.to_item_id, [])
            for end_item_id in end_items:
                tup = (end_item_id, attr, node)
                ret[item_id].append(tup)
                # ret.update({item_id: tups + [tup]})

        return ret

    @classmethod
    def _create_end_item_dict(cls, item_route_list: list):
        """
        반제품 item id ~ final item id에 대한 Dictionary 생성
        :param item_route_list: 정상적인 item route 정보
        :return: None
        """
        item_to_end_item_dict: dict = {}

        for item_route in item_route_list:
            for item in item_route:
                end_items: list = item_to_end_item_dict.get(item, [])
                if item_route[0] in end_items:
                    continue
                end_items.append(item_route[0])
                item_to_end_item_dict.update(
                    {item: end_items}
                )
                # if item not in item_to_end_item_dict.keys():
                #     item_to_end_item_dict.update({item: item_route[0]})
        return item_to_end_item_dict

    @classmethod
    def _init_routes(cls, inventories: dict, processes: dict, work_order_master: list,
                     simulation_dict, use_backward_size: bool, session: AbstractSession) -> dict:
        """

        :param inventories:
        :param processes:
        :param work_order_master:
        :param simulation_dict:
        :param session:
        :return:
        """

        # Simulation ID
        simulation_id = simulation_dict['SIM_ID']

        # Route Data Access Object
        dao: RouteDAO = RouteDAO.instance()

        # 기준 정보 - Route 마스터
        route_data = dao.select(session=session, simulation_id=simulation_id)
        route_master = dao.map(route_data)

        # 기준정보 - Route 리스트
        route_node_list = dao.map(dao.select_route_node(session=session, simulation_id=simulation_id))

        # 기준정보 - Route 연결 정보
        route_connect_data = dao.select_connect_node(session=session, simulation_id=simulation_id)
        previous_loc_dict = dao.hash_map(route_connect_data, 'NEXT_LOC_ID')  # hash map - Key(NEXT_LOC_ID) 이전 Route 정보
        next_loc_dict = dao.hash_map(route_connect_data, 'CURR_LOC_ID')      # hash map - Key(CURR_LOC_ID) 다음 Route 정보

        # Item Route 정보
        previous_route_dict = dao.hash_map(route_data, 'NEXT_LOC_ID')   # hash map - Key(NEXT_LOC_ID) 이전 Route Item 정보
        next_route_dict = dao.hash_map(route_data, 'CURR_LOC_ID')       # hash map - Key(NEXT_LOC_ID) 다음 Route Item 정보

        # Work Order 정보 초기화
        work_order_item_list = cls._create_work_order_item_list(work_order_master=work_order_master)

        # Route Item 관련 정보들 초기화  >> Factory Manager 로 이동
        next_to_curr_item_dict = cls._create_next_to_curr_item_dict(route_master=route_master)
        item_route_list, item_route_error_list = cls._create_work_order_route(work_order_item_list=work_order_item_list,
                                                                              to_from_item_dict=next_to_curr_item_dict)
        end_item_dict = cls._create_end_item_dict(item_route_list=item_route_list)

        # Todo: 미사용 코드 - 이후 로직에서 사용될 지 검토 후 삭제
        # _next_to_curr_item_dict = cls._create_next_to_curr_item_dict(route_master=route_master)
        # _item_to_final_item_dict = cls._create_route_group(route_master=route_master)

        routes: dict = {}
        for info in route_node_list:
            route: Route = Route()
            router_id = info['CURR_LOC_ID']
            router_type = info['CURR_LOC_TYP']
            if router_type == 'INV':
                route_location: AbstractNode = inventories.get(router_id)
            elif router_type == 'PROC':
                route_location: AbstractNode = processes.get(router_id)
            else:
                raise NotImplementedError(
                    f""
                )

            previous_node_dict: dict = cls._find_route_node(inventories, processes, previous_loc_dict.get(router_id, []),
                                                            "CURR_LOC_ID", "CURR_LOC_TYP")
            next_node_dict: dict = cls._find_route_node(inventories, processes, next_loc_dict.get(router_id, []),
                                                        "NEXT_LOC_ID", "NEXT_LOC_TYP")

            previous_item_route_dict: dict = cls._create_item_route_dict(inventories, processes,
                                                                         previous_route_dict.get(router_id, []),
                                                                         end_item_dict,
                                                                         "CURR_LOC_ID", "CURR_LOC_TYP")
            next_item_route_dict: dict = cls._create_item_route_dict(inventories, processes,
                                                                     next_route_dict.get(router_id, []),
                                                                     end_item_dict,
                                                                     "NEXT_LOC_ID", "NEXT_LOC_TYP")

            route.init(route_id=router_id, route_type=router_type, route_location=route_location,
                       previous_node_dict=previous_node_dict,
                       next_node_dict=next_node_dict,
                       previous_route_dict=previous_item_route_dict,
                       next_route_dict=next_item_route_dict,
                       use_backward_size=use_backward_size)
            routes[router_id] = route

        return routes

    # @classmethod
    # def _get_node_depths(cls, dao, next_loc_dict: dict, route_connect_data: dict):
    #     route_connect_list: list = dao.map(route_connect_data)
    #     priors: List[str] = [loc['CURR_LOC_ID'] for loc in route_connect_list]
    #     nexts: List[str] = [loc['NEXT_LOC_ID'] for loc in route_connect_list]
    #     last_locations: List[str] = [loc for loc in nexts if loc not in priors]
    #
    #     location_depth: List[list] = [last_locations]
    #     # 이전 location
    #     while True:
    #         prior_locations: List[str] = [row['CURR_LOC_ID']
    #                                       for loc in location_depth[-1]
    #                                       for row in next_loc_dict.get(loc, [])]
    #         if prior_locations:
    #             location_depth.append(prior_locations)
    #             continue
    #         break
    #     location_depth.reverse()
    #
    #     return location_depth

    # ===================================================== Route =====================================================

    @classmethod
    def _create_work_order_item_list(cls, work_order_master: list) -> list:
        """

        :param work_order_master:
        :return:
        """

        work_order_item_list: list = []
        for work_order_item in work_order_master:
            if work_order_item['ORDER_ITEM_ID'] not in work_order_item_list:
                work_order_item_list.append(work_order_item['ORDER_ITEM_ID'])

        return sorted(work_order_item_list)

    ############################################################################################
    # Route 관련 Method
    ############################################################################################

    # @classmethod
    # def _create_curr_to_next_loc_dict(cls, route_master: list, inventories: dict, processes: dict):
    #     curr_to_next_loc_dict = {}
    #
    #     for route in route_master:
    #         if route['CURR_LOC_ID'] in inventories.keys():
    #             current_location = inventories[route['CURR_LOC_ID']]
    #         elif route['CURR_LOC_ID'] in processes.keys():
    #             current_location = processes[route['CURR_LOC_ID']]
    #         else:
    #             raise AssertionError(
    #                 ""
    #             )
    #
    #         if route['NEXT_LOC_ID'] in inventories.keys():
    #             next_location = inventories[route['NEXT_LOC_ID']]
    #         elif route['NEXT_LOC_ID'] in processes.keys():
    #             next_location = processes[route['NEXT_LOC_ID']]
    #         else:
    #             raise AssertionError(
    #                 ""
    #             )
    #
    #         if next_location not in curr_to_next_loc_dict.keys():
    #             curr_to_next_loc_dict.update({next_location: [current_location]})
    #         else:
    #             temp_list = curr_to_next_loc_dict[next_location]
    #             if current_location not in temp_list:
    #                 temp_list.append(current_location)
    #             curr_to_next_loc_dict.update({next_location: temp_list})
    #
    #     return curr_to_next_loc_dict

    @classmethod
    def _create_next_to_curr_item_dict(cls, route_master: list) -> dict:
        """
        각 제품의 To From 정보를 Dictionary 형태로 만드는 처리
        :param route_master: Route Master Data
        :return: None
        """
        to_from_item_dict: dict = defaultdict(list)
        for route in route_master:
            next_item_id: str = route['NEXT_ITEM_ID']
            curr_item_id: str = route['ITEM_ID']
            if next_item_id == curr_item_id:
                continue
            if curr_item_id not in to_from_item_dict[next_item_id]:
                to_from_item_dict[next_item_id].append(curr_item_id)
        return to_from_item_dict

    @classmethod
    def _create_work_order_route(cls, work_order_item_list: list, to_from_item_dict: dict):

        item_route_list: list = []
        item_route_error_list: list = []

        for work_order_item in work_order_item_list:
            tup: tuple = tuple([work_order_item])
            item_route_list.extend(FactoryBuilder.get_work_order_item_route(to_from_item_dict, tup))

        return item_route_list, item_route_error_list

        # 기존 로직
        # for work_order_item in work_order_item_list:
        #     work_order_routes: list = []
        #     starting_work_order_route = [work_order_item]
        #
        #     while "311110000000" not in starting_work_order_route[-1]: # Todo: 311110000000: RM ITEM_ID (hard coding)
        #         if starting_work_order_route[-1] in to_from_item_dict.keys():
        #             for prev in to_from_item_dict[starting_work_order_route[-1]]:
        #                 work_order_routes.append(starting_work_order_route + [prev])
        #         else:
        #             item_route_error_list.append(starting_work_order_route)
        #             break
        #     item_route_list.append(starting_work_order_route)
        #
        # return item_route_list, item_route_error_list

    @staticmethod
    def get_work_order_item_route(to_from_dict: dict, ret: tuple = ()):

        current_item: str = ret[-1]

        prevs: list = to_from_dict.get(current_item, [])
        if not prevs:
            return [ret]

        rets: list = []
        for prev in prevs:
            appended: tuple = ret + tuple([prev])
            rets.extend(FactoryBuilder.get_work_order_item_route(to_from_dict, appended))
        return rets

    # @classmethod
    # def _create_route_type_dict(cls, route_master: list):
    #     route_type_dict = {}
    #
    #     for route in route_master:
    #         if route['CURR_LOC_ID'] not in route_type_dict:
    #             route_type_dict.update({route['CURR_LOC_ID']: route['CURR_LOC_TYP']})
    #         if route['NEXT_LOC_ID'] not in route_type_dict:
    #             route_type_dict.update({route['NEXT_LOC_ID']: route['NEXT_LOC_TYP']})
    #
    #     return route_type_dict

    # @classmethod
    # def _create_route_group(cls, route_master: list):
    #     route_loc_group_dict: dict = {}
    #
    #     for route in route_master:
    #         if route['CURR_LOC_ID'] not in route_loc_group_dict.keys():
    #             route_loc_group_dict.update({route['CURR_LOC_ID']: [route]})
    #         else:
    #             temp_list = route_loc_group_dict[route['CURR_LOC_ID']]
    #             temp_list.append(route)
    #             route_loc_group_dict[route['CURR_LOC_ID']] = temp_list
    #
    #     return route_loc_group_dict

    # @classmethod
    # def _create_curr_to_next_route_dict(cls, bom_route_list: list, entity_pointers: dict):
    #     """
    #
    #     :param bom_route_list:
    #     :return:
    #     """
    #     # curr_to_next_route_dict = {}
    #     # for route in bom_route_list:
    #     #     next_entity: object = route['NEXT_LOC_ID']
    #     #     if route['NEXT_LOC_ID'] in entity_pointers.keys():
    #     #         next_entity = entity_pointers[route['NEXT_LOC_ID']]
    #     #     curr_to_next_route_dict.update({route['ITEM_ID']: (route['NEXT_ITEM_ID'], next_entity)})
    #     #
    #
    #     curr_to_next_route_dict = {}
    #     for route in bom_route_list:
    #         if route['ITEM_ID'] not in curr_to_next_route_dict.keys():
    #             value = (route['NEXT_ITEM_ID'], entity_pointers[route['NEXT_LOC_ID']])
    #             curr_to_next_route_dict.update({route['ITEM_ID']: [value]})
    #         else:
    #             temp_list = curr_to_next_route_dict[route['ITEM_ID']]
    #             value = (route['NEXT_ITEM_ID'], entity_pointers[route['NEXT_LOC_ID']])
    #             temp_list.append(value)
    #             curr_to_next_route_dict.update({route['ITEM_ID']: temp_list})
    #
    #     return curr_to_next_route_dict

    # @classmethod
    # def _create_route_loc_list(cls, route_master: list):
    #     """
    #
    #     :param route_master:
    #     :return: location_route
    #     """
    #     to_from_location_dict = {}
    #     for route in route_master:
    #         if route['NEXT_LOC_ID'] not in to_from_location_dict.keys():
    #             to_from_location_dict.update({route['NEXT_LOC_ID']: route['CURR_LOC_ID']})
    #
    #     # 마지막 Route (Hard Coding)
    #     last_locations: List[str] = [loc for loc in to_from_location_dict.keys()
    #                                  if loc not in to_from_location_dict.values()]
    #
    #     #
    #     location_route: List[list] = [last_locations]
    #
    #     # 이전 location
    #     prior_locations: List[str] = []
    #     while prior_locations:
    #         prior_locations = []
    #     # while location_route[-1] != 'RM':   # Location Start Route (Hard Coding)
    #     #     if location_route[-1] in to_from_location_dict.keys():
    #     #         location_route.append(to_from_location_dict[location_route[-1]])
    #
    #     route_naming_dict = {}
    #     idx = 0
    #     for location in location_route:
    #         route_naming_dict.update({location: 'ROUTE' + str(len(location_route) - idx)})
    #         idx += 1
    #
    #     return route_naming_dict

    # @classmethod
    # def _create_prev_next_route_dict(cls, route_master: list, route_loc_list: list, entity_pointers: dict):
    #     prev_route_dict = {}
    #     next_route_dict = {}
    #     for route_loc in route_loc_list:
    #         for route in route_master:
    #             # Check Previous Route
    #             if route_loc == route['NEXT_LOC_ID']:
    #                 if route_loc not in prev_route_dict.keys():
    #                     value = entity_pointers[route['CURR_LOC_ID']]
    #                     prev_route_dict.update({route_loc: [value]})
    #                 else:
    #                     temp_list = prev_route_dict[route_loc]
    #                     if entity_pointers[route['CURR_LOC_ID']] not in temp_list:
    #                         temp_list.append(entity_pointers[route['CURR_LOC_ID']])
    #             # Check Next Route
    #             if route_loc == route['CURR_LOC_ID']:
    #                 if route_loc not in next_route_dict.keys():
    #                     value = entity_pointers[route['NEXT_LOC_ID']]
    #                     next_route_dict.update({route_loc: [value]})
    #                 else:
    #                     temp_list = next_route_dict[route_loc]
    #                     if entity_pointers[route['NEXT_LOC_ID']] not in temp_list:
    #                         temp_list.append(entity_pointers[route['NEXT_LOC_ID']])
    #
    #     return prev_route_dict, next_route_dict

    # =================================================================================================================

    @classmethod
    def _get_dao_data(cls, session: AbstractSession):

        factory_dao: FactoryDAO = FactoryDAO.instance()
        factory_info = factory_dao.map(factory_dao.select_one(session=session))[0]

        bom_dao: BomDAO = BomDAO.instance()
        bom = bom_dao.map(bom_dao.select_bom_routing(session=session))

        # DemandDAO로 부터 정보 받아오기
        demand_dao: DemandDAO = DemandDAO.instance()
        work_order_master = demand_dao.map(demand_dao.select_master(session=session))

        return factory_info, bom, work_order_master

    # @classmethod
    # def _get_router_sequence(cls, routers: list, inventories: dict, to_from_location_dict: dict):
    #     """
    #
    #     :return:
    #     """
    #     router_sequence: dict = dict()
    #     last_operators: list = cls._get_last_operators(inventories=inventories)
    #     prior_operators: list = [
    #         prior_operator
    #         for last_operator in last_operators
    #         for prior_operator in to_from_location_dict[last_operator]
    #     ]
    #     depth: int = 0
    #     while len(prior_operators) > 0:
    #         depth += 1
    #         tmp_routers: list = [router for router in routers if router.route_location in prior_operators]
    #         router_sequence[depth] = tmp_routers
    #
    #         tmp_prior_operators: list = []
    #         for last_operator in prior_operators:
    #             if last_operator not in to_from_location_dict.keys():
    #                 continue

    #             for prior_operator in to_from_location_dict[last_operator]:
    #                 tmp_prior_operators.append(prior_operator)
    #         prior_operators = tmp_prior_operators.copy()
    #
    #     return router_sequence
