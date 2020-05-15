
import datetime

from m4.process.Item import Item
from m4.operator.Process import Process
from m4.operator.Resource import Resource
from m4.operator.ProcessResource import ProcessResource
from m4.util.LogHandler import LogHandler
from m4.ApplicationConfiguration import ApplicationConfiguration

# Application Configuration
ApplicationConfiguration.instance().init(properties_file='m4.properties')

# Setup Log Handler
LogHandler.instance().init(config=ApplicationConfiguration.instance())

# Data
constraint_max_priority_dict: dict = {
    'LDMD1': [
        {'RESC_ID': 'LDMD1', 'PRIORITY': 1}],
    'LDMD2': [
        {'RESC_ID': 'LDMD2', 'PRIORITY': 1}]
}
constraint_dict: dict = {
    'LDMD1': [
        {'START_DATE': datetime.datetime(2020, 4, 15, 0, 0),
         'END_DATE': datetime.datetime(2020, 4, 20, 0, 0),
         'RESC_ID': 'LDMD1', 'SCHDL_ID': 'REACTOR_SD', 'PRIORITY': 1,
         'TM_CONST_ID': 'SHUTDOWN_1', 'TM_CONST_NM': 'SHUTDOWN', 'TM_CONST_TYP': 'SHDWN', 'PRD_TYP': 'DAY',
         'LOWER_BOUND': datetime.datetime(2020, 4, 15, 0, 0), 'UPPER_BOUND': datetime.datetime(2020, 4, 20, 0, 0)}],
    'LDMD2': [
        {'START_DATE': datetime.datetime(2020, 4, 15, 0, 0),
         'END_DATE': datetime.datetime(2020, 4, 20, 0, 0),
         'RESC_ID': 'LDMD2', 'SCHDL_ID': 'REACTOR_SD', 'PRIORITY': 1,
         'TM_CONST_ID': 'SHUTDOWN_1', 'TM_CONST_NM': 'SHUTDOWN', 'TM_CONST_TYP': 'SHDWN', 'PRD_TYP': 'DAY',
         'LOWER_BOUND': datetime.datetime(2020, 4, 15, 0, 0), 'UPPER_BOUND': datetime.datetime(2020, 4, 20, 0, 0)}]
}
reesources_data: list = [
    {'RESC_ID': 'LDMD1', 'RESC_NM': 'M1', 'PLANT_ID': '1200', 'RESC_SCHDL_ID': 'REACTOR_SD', 'DESCR': None},
    {'RESC_ID': 'LDMD2', 'RESC_NM': 'M2', 'PLANT_ID': '1200', 'RESC_SCHDL_ID': 'REACTOR_SD', 'DESCR': None},
    {'RESC_ID': 'LDMDPK1', 'RESC_NM': 'PACKAGING1', 'PLANT_ID': '1200', 'RESC_SCHDL_ID': None, 'DESCR': None},
    {'RESC_ID': 'LDMDPK2', 'RESC_NM': 'PACKAGING2', 'PLANT_ID': '1200', 'RESC_SCHDL_ID': None, 'DESCR': None},
    {'RESC_ID': 'LDMDPK3', 'RESC_NM': 'PACKAGING3', 'PLANT_ID': '1200', 'RESC_SCHDL_ID': None, 'DESCR': None},
    {'RESC_ID': 'LDMDPK4', 'RESC_NM': 'PACKAGING4', 'PLANT_ID': '1200', 'RESC_SCHDL_ID': None, 'DESCR': None}]
process_info: dict = {
        'PROC_ID': 'REACTOR',
        'PROC_NM': 'REACTOR',
        'DESCR': 'REACTOR'
    }
bor_data: list = [
    {'PROC_ID': 'REACTOR',
     'RESC_ID': 'LDMD1',
     'BOR_NM': 'M1',
     'DESCR': 'REACTOR M1',
     'PRIORITY': 1,
     'PROD_EFFCNCY': 1,
     'PROC_PRECSN': 0,
     'MIN_LOT_SIZE': 80,
     'MAX_LOT_SIZE': 500,
     'PROC_TM': 1,
     'PRE_PROC_SETUP_TM': 3,
     'MAX_QUEUE_SIZE': 10},
    {'PROC_ID': 'REACTOR',
     'RESC_ID': 'LDMD2',
     'BOR_NM': 'M2',
     'DESCR': 'REACTOR M2',
     'PRIORITY': 2,
     'PROD_EFFCNCY': 1,
     'PROC_PRECSN': 0,
     'MIN_LOT_SIZE': 80,
     'MAX_LOT_SIZE': 500,
     'PROC_TM': 1,
     'PRE_PROC_SETUP_TM': 3,
     'MAX_QUEUE_SIZE': 10}
]


if __name__ == '__main__':

    # Process Initialization
    resources: dict = {}
    for res in reesources_data:
        resource: Resource = Resource()
        constraint_data: list = constraint_dict.get(res['RESC_ID'], [])
        constraint_max_priority_data = constraint_max_priority_dict.get(res['RESC_ID'])
        constraint_max_priority = 0 if constraint_max_priority_data is None else \
            constraint_max_priority_data[0]['PRIORITY']
        resource.init(res, constraint_data, constraint_max_priority)
        resources[res['RESC_ID']] = resource
    process: Process = Process()
    process.init(info=process_info)
    for bor in bor_data:
        process.add_process_resource(bor, resources[bor["RESC_ID"]])

    # Process Workflow
    run_times = [
        {'index': (i-14)*24 + j, 'date': datetime.datetime(2020, 4, i, j, 0), 'seconds': 0, 'is_off_day': False}
        for i in range(14, 21 + 1) for j in range(24)
    ]

    dmds: dict = dict()
    finished_items: list = []
    for run_time in run_times:

        # 1. Item to Put ( Route 에서 결정)
        item: Item = Item()
        item.init(
            item_id=f'ITEM_{run_time["date"].day:02d}_{run_time["date"].hour:02d}',
            location_id=f'REACTOR',
            order_quantity=100,
            req_quantity=100,
            quantity=100,
            work_order_id=f'DMD_{run_time["date"].day:02d}{run_time["date"].hour:02d}',
            order_item_id=f'ITEM_{run_time["date"].day:02d}_{run_time["date"].hour:02d}',
            setup_time=3,
            process_time=5
        )
        dmds[item.work_order_id] = dmds.get(item.work_order_id, {})
        dmds[item.work_order_id].update(
            {item.item_id: item.get_order_quantity()}
        )

        # Move 소요 시간 (테스트용)
        move_time: int = 4

        # 2. 할당 가능한 Resource ID
        available_resource_id: str = process.check(
            date=run_time['date'], item_id=item.item_id, quantity=item.get_required_quantity(), move_time=move_time)

        # 4. Process Run
        process.run(time_index=run_time['index'], date=run_time['date'])

        # 3. Process 에 Item Put ( Route 에서 결정 후 process.put() 호출 )
        if available_resource_id is not None:
            process.put(time_index=run_time['index'], date=run_time['date'],
                        item=item, move_time=move_time, resource_id=available_resource_id)

        # 5. Process Fetch
        for dmd_id in dmds.keys():
            _finished_items: list = []
            for item_id in dmds[dmd_id].keys():
                qty: float = dmds[dmd_id][item_id]
                fetched_items: list = process.fetch(
                    time_index=run_time['index'], date=run_time['date'],
                    item_id=item_id, work_order_id=dmd_id, quantity=qty
                )
                _finished_items.append(fetched_items)
                if len(fetched_items) > 0:
                    dmds[dmd_id].pop(item_id)
                    break
            finished_items.append(_finished_items)
            if len(dmds[dmd_id]) == 0:
                dmds.pop(dmd_id)
                break

    print("DEBUG POINT")
