from m4.common.SingletonInstance import SingletonInstance
from m4.dao.AbstractDAO import AbstractDAO
from m4.dao.AbstractSession import AbstractSession


class RouteDAO(AbstractDAO, SingletonInstance):
    """
    Route Data Access Object
    """

    def select_one(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로부터 1개 데이터를 조회
        :param session: AbstractSession 인스턴스
        :param params: sql 파라미터 데이터
        :return: {"columns" : columns, "data" : list}
        """
        pass

    def select(self, session: AbstractSession, **params):
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
             WHERE SIM_ID = :simulation_id
            """, params)

    def select_route_node(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로부터 리스트 데이터를 조회
        :param session: AbstractSession 인스턴스
        :param params: sql 파라미터 데이터
        :return: {"columns" : columns, "data" : list}
        """
        return session.select(
            """
            SELECT CURR_LOC_ID, MAX(CURR_LOC_TYP) AS CURR_LOC_TYP
              FROM  
               (SELECT CURR_LOC_ID, CURR_LOC_TYP
                  FROM FS_ROUTE
                 WHERE SIM_ID = :simulation_id
                 UNION ALL
                SELECT NEXT_LOC_ID AS CURR_LOC_ID, NEXT_LOC_TYP AS CURR_LOC_TYP
                  FROM FS_ROUTE
                 WHERE SIM_ID = :simulation_id AND ROUTE_CONN_CD = 'PDINV'
               )
             GROUP BY CURR_LOC_ID
            """, params)

    def select_connect_node(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로부터 리스트 데이터를 조회
        :param session: AbstractSession 인스턴스
        :param params: sql 파라미터 데이터
        :return: {"columns" : columns, "data" : list}
        """
        return session.select(
            """
            SELECT CURR_LOC_ID, MAX(CURR_LOC_TYP) AS CURR_LOC_TYP, NEXT_LOC_ID, MAX(NEXT_LOC_TYP) AS NEXT_LOC_TYP
              FROM FS_ROUTE
             WHERE SIM_ID = :simulation_id
             GROUP BY CURR_LOC_ID, NEXT_LOC_ID
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
