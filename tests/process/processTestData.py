
import datetime

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
     'PRE_PROC_SETUP_TM': 3},
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
     'PRE_PROC_SETUP_TM': 3}
]
