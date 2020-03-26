
import datetime

from m4.util.TimeUtility import TimeUtility


class Duration(object):
    """
    Duration Object
    Calendar (비가용 계획) 인스턴스가 가질
    비가용 계획 구간 정보 리스트는 Duration 인스턴스(들)로 구성
    Duration 처리 관련 속성 및 동작들이 정의됨
    """

    # Duration 클래스 공통 Static 변수들
    staticVar: object = None  # Comment

    # Duration 클래스 Static Constants
    _DURATION_CYCLE_TYPES: list = [     # Duration 의 CYCLE_TYPE 값으로 가질 수 있는 문자열 목록
        'O',                            # O: Once(1회)
        'D',                            # D: Daily(하루마다 반복)
        'W'                             # W: Weekly(일주일마다 반복)
    ]

    def __init__(self):
        """
        생성자 : Duration 클래스를 상속받는 자손 클래스들이 공통으로 가질 멤버 변수들
        """

        # 2-1. Public
        self.id: str = ""                               # Duration ID

        # 2-2. Private
        self._cycleType: str = ""                       # 반복 타입 : 1회용, 매일 반복, 주마다 반복
        self._startDate: datetime.datetime = None       # 비가용 시작 시간
        self._endDate: datetime.datetime = None         # 비가용 종료 시간

    def init(self, id: str, cycle_type: str, start_date: object, end_date: object):
        """

        :return: void
        """

        # 시작 및 종료 일자 세팅에 앞서 타입 검사 및 문자열이라면 변환하는 단계
        start_date: datetime.datetime = TimeUtility.check_date_info(date_info=start_date)
        end_date: datetime.datetime = TimeUtility.check_date_info(date_info=end_date)

        # 2-1. Public
        self.id = id

        # 2-2. Private
        self._set_cycle_type(cycle_type=cycle_type)
        self._set_start_date(start_date=start_date)
        self._set_end_date(end_date=end_date)

    def clip_duration(self,
                      clip_from_date: datetime.datetime,
                      clip_to_date: datetime.datetime):
        """

        :param clip_from_date:
        :param clip_to_date:
        :return:
        """
        pass

    def get_cycle_type(self):
        """

        :return: str
        """
        return self._cycleType

    def get_start_date(self):
        """

        :return: datetime.datetime
        """
        return self._startDate

    def get_end_date(self):
        """

        :return: datetime.datetime
        """
        return self._endDate

    def _set_cycle_type(self, cycle_type: str):
        """

        :param cycle_type:
        :return:
        """
        self._cycleType = cycle_type

    def _set_start_date(self, start_date: object):
        """

        :param start_date:
        :return:
        """
        pass

    def _set_end_date(self, end_date: object):
        """

        :param end_date:
        :return:
        """
        pass
