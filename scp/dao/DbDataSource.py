
import os
import cx_Oracle

from scp.dao.AbstractDataSource import AbstractDataSource


class DbDataSource(AbstractDataSource):
    """
    Database Data Source
    Database (Oracle) Connection 담당 클래스
    """

    # Static Variables
    staticVar2: object = None                           # Comment

    # Static Constants : 뉴로코어 소스에 있는 것들인데 불필요 한 듯
    START_VALUE = u"Unicode \u3042 3".encode('utf-8')   # Comment
    END_VALUE = u"Unicode \u3042 6".encode('utf-8')     # Comment

    def __init__(self):
        """
        생성자 : DbDataSource 클래스 멤버 변수들
        """

        # Oracle Database 언어 설정
        os.environ["NLS_LANG"] = ".AL32UTF8"

        # 부모 클래스의 모든 멤버 변수들을 상속
        super().__init__()

        # Config.properties 파일에서 DB 접속 관련 설정 값들 가져오기
        self.connectionConfig = self._get_connection_config()   # Comment

        # DbDataSource 클래스에만 있는 변수

        # 1. Public

        # 2. Private

        # Oracle TNS
        self._tns: str = cx_Oracle.makedsn(
            ip=self.connectionConfig['database.connection.ip'],
            port=self.connectionConfig['database.connection.port'],
            sid=self.connectionConfig['database.connection.sid']
        )

        # Oracle Session Pool
        self._pool: cx_Oracle.SessionPool = cx_Oracle.SessionPool(
            user=self.connectionConfig['database.scheme.user'],
            password=self.connectionConfig['database.scheme.pwd'],
            dsn=self._tns
        )

    # Public 메서드

    def get_db_data(self, sql: str, params: tuple = ()):
        """
        DB 로부터 Query문 결과 Array를 가져오는 처리.
        뉴로코어 방식 vs resource .sql 파일 내용을 문자열로 받아다 줄 지 ??
        :param sql:
        :param params:
        :return: Array-like Object  ex: pandas.DataFrame / list<list> / ...
        """
        pass

    def execute_proc(self, process_name: str, params: tuple = ()):
        """
        DB 에 저장된 프로시져를 호출하는 처리.
        :param process_name:
        :param params:
        :return: void
        """
        pass

    def batch_query(self, sql_template: str, data_arr: list, sql_del: str = ""):
        """
        CRUD 쿼리문을 실행하는 처리
        :param sql_template:
        :param data_arr:
        :param sql_del:
        :return: void
        """
        pass

    # Protected 메서드

    def _get_connection_config(self):
        """
        Config.properties 파일로부터 (DB) 관련 설정 값들 받아오는 처리
        Question 생성자에서 한 번만 호출되도록 ??
        :return: dict ?
        """
        return super()._get_connection_config()

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
