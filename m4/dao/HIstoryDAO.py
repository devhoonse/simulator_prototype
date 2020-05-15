from m4.common.SingletonInstance import SingletonInstance
from m4.dao.AbstractDAO import AbstractDAO
from m4.dao.AbstractSession import AbstractSession


class HistoryDAO(AbstractDAO, SingletonInstance):
    """
    Route Data Access Object
    """

    def select(self, session: AbstractSession, **params):
        pass

    def select_one(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로부터 1개 데이터를 조회
        :param session: AbstractSession 인스턴스
        :param params: sql 파라미터 데이터
        :return: {"columns" : columns, "data" : list}
        """
        pass

    def select_master(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로부터 리스트 데이터를 조회
        :param session: AbstractSession 인스턴스
        :param params: sql 파라미터 데이터
        :return: {"columns" : columns, "data" : list}
        """
        return session.select(
            """
            SELECT *
            FROM FS_ROUTE
            """, params)

    def execute(self, session: AbstractSession, data_list: list):
        """
        세션 인스턴스를 통해 Data Source에 대한 CUD를 실행
        :param session: AbstractSession 인스턴스
        :param sql_template: sql template string
        :param data_list: CUD 대상 데이터
        :return: True/False
        """

        sql_template = """
        INSERT INTO SCMV2.FS_SCHDL_RSLT_TEST(
            PLAN_VER_ID, SIM_ID, CURR_LOC_ID, CURR_RES_ID, NEXT_LOC_ID, 
            LOT_ID, WORK_ORDER_ID, ORDER_ITEM_ID, ITEM_ID, PROD_QTY, EVENT_ID, 
            START_DT_HMS, END_DT_HMS, DUR
        )values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14)"""
        # sql_template = """INSERT INTO SCMV2.FS_SCHDL_RSLT(PLAN_VER_ID, SIM_ID, CURR_LOC_ID, NEXT_LOC_ID, WORK_ORDER_ID, ORDER_ITEM_ID,
        #                                                     LOT_ID, ITEM_ID, PROD_QTY, START_DT_HMS, END_DT_HMS, DUR
        #                                                    )values(:1, :2, :3, :4, :6, :7, :5, :8, :9, :11, :12, :13)"""

        session.execute(sql_template=sql_template, data_list=list(map(tuple, data_list)))
