from m4.common.SingletonInstance import SingletonInstance
from m4.dao.AbstractDAO import AbstractDAO
from m4.dao.AbstractSession import AbstractSession


class WorkOrderDAO(AbstractDAO, SingletonInstance):
    """
    Demand Data Access Object
    """

    def select_one(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 1개 데이터를 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        pass

    def select(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 list 데이터 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        return session.select("""
            SELECT T1.PLAN_VER_ID
                 , T1.WORK_ORDER_ID
                 , T1.ORDER_ITEM_ID
                 , T1.PRIORITY
                 , T1.DTL_PRIORITY
                 , T1.ORDER_QTY
                 , TO_DATE(T1.DUE_DT || '235959', 'yyyymmddhh24miss') AS DUE_DT
                 , R1.NEXT_LOC_ID AS LOC_ID
            FROM FS_WORK_ORDER T1
            JOIN FS_ROUTE R1
                 ON (R1.NEXT_ITEM_ID = T1.ORDER_ITEM_ID
                     AND R1.ROUTE_CONN_CD = 'PDINV'
                     AND R1.NEXT_LOC_TYP = 'INV')
            WHERE T1.ORDER_QTY <> 0
              AND T1.PLAN_VER_ID = :plan_version_id
            ORDER BY T1.PRIORITY, T1.DTL_PRIORITY, T1.DUE_DT
        """, params)

    def execute(self, session: AbstractSession, sql_template: str, data_list: list):
        """
        세션 인스턴스를 통해 Data Source에 대한 CUD를 실행
        :param session: AbstractSession 인스턴스
        :param sql_template: sql template string
        :param data_list: CUD 대상 데이터
        :return: True/False
        """
        pass