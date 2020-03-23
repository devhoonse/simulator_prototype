
from abc import *


class AbstractDataSource(metaclass=ABCMeta):
    """
    Data Source Object
    실제 데이터를 들고 오기 위해 데이터 소스와의 연결을 담당하는 클래스
    가져올 데이터 소스의 종류에 따라 다르게 구현
        (Database)DataSource    : Database 와의 연결을 담당
        FileDataSource  : File System (패키지가 설치된 로컬 내 파일 시스템)과의 연결을 담당
    """

    def __init__(self):
        """
        생성자 : Data Source 클래스를 상속받는 자손 클래스들이 공통으로 가질 멤버 변수들
        """

    @abstractmethod
    def _get_connection(self):
        """
        DataSource 와의 실제 접속을 체결하고 Data IO를 위한 Connection 인스턴스를 반환
        체결되는 접속 및 반환되는 Connection 인스턴스는 데이터 소스에 따라 다름
            (Database)DataSource    - cx_Oracle.SessionPool, cx_Oracle.Connection 등
            FileDataSource  - File IO 를 위한 객체 inherits _io.IOBase
        :return: Connection 인스턴스
        """
        pass

    @abstractmethod
    def _release_connection(self, connection: object):
        """
        DataSource 와의 접속을 해제
        해제되는 접속은 데이터 소스에 따라 다름
            (Database)DataSource    - cx_Oracle.SessionPool.release( cx_Oracle.Connection )
            FileDataSource  - _io._IOBase.close()
        :param connection: Connection 인스턴스  ex: cx_Oracle.SessionPool / _io._IOBase
        :return: void
        """
        pass
