from m4.ApplicationConfiguration import ApplicationConfiguration
from m4.dao.OracleDataSource import OracleDataSource

"""
최상위 어플리케이션 실행 파일
    FactorySimulator 클래스 인스턴스를 생성
    Simulator를 실행
"""

if __name__ == '__main__':

    config: ApplicationConfiguration = ApplicationConfiguration()
    config.init('m4.properties')

    ds: OracleDataSource = OracleDataSource()
    ds.init(dict(config.find_section("DatabaseSource")))
