
import os
import cx_Oracle

from m4.dao.AbstractDataSource import AbstractDataSource


class OracleDataSource(AbstractDataSource):
    """
    Oracle Data Source 클래스
    """

     # Oracle Session Pool
    _pool: cx_Oracle.SessionPool = None

    def __init__(self):
        """
        생성자 : DbDataSource 클래스 멤버 변수들
        """

        # Oracle Database 언어 설정
        os.environ["NLS_LANG"] = ".AL32UTF8"

        # 부모 클래스의 모든 멤버 변수들을 상속
        super(__class__, self).__init__()

    # Public 메서드
    def init(self, uri_map):
        """
        Database SessionPool 초기화
        :param: uli_map - URI 정보
        """
        tns: str = cx_Oracle.makedsn(
            host=uri_map["ds.connection.host"],
            port=uri_map["ds.connection.port"],
            sid=uri_map["ds.connection.sid"]
        )

        # Oracle Session Pool 생성
        self._pool: cx_Oracle.SessionPool = cx_Oracle.SessionPool(
            user=uri_map["ds.connection.id"],
            password=uri_map["ds.connection.password"],
            dsn=tns,
            min=1, max=20, increment=1, threaded=True
        )

    def close(self):
        """
        Database SessionPool 종료
        """
        self._pool.close()

    def select_data(self, sql: str, params: tuple = ()):
        """
        DB 로부터 Query문 결과 Array를 가져오는 처리.
        뉴로코어 방식 vs resource .sql 파일 내용을 문자열로 받아다 줄 지 ??
        :param sql:
        :param params:
        :return: Array-like Object  ex: pandas.DataFrame / list<list> / ...
        """
        pass

    def execute_batch(self, sql_template: str, data_arr: list, sql_del: str = ""):
        """
        CRUD 쿼리문을 실행하는 처리
        :param sql_template:
        :param data_arr:
        :param sql_del:
        :return: void
        """
        pass

    def execute_procedure(self, process_name: str, params: tuple = ()):
        """
        DB 에 저장된 프로시져를 호출하는 처리.
        :param process_name:
        :param params:
        :return: void
        """
        pass

    # Protected 메서드
    def _get_connection(self):
        """
        Oracle Session Pool 을 통해 DB와의 실제 Connection 체결 처리
        :return: cx_Oracle.Connection
        """
        return self._pool.acquire()

    def _release_connection(self, connection: cx_Oracle.Connection):
        """
        Database Connection 이후 현재까지 수행한 작업들을 commit 한 후에
        접속을 해제하는 처리
        :return:
        """
        connection.commit()
        self._pool.release()
