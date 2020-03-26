
import datetime
from abc import *

from m4.util.TimeUtility import TimeUtility


class AbstractDuration(metaclass=ABCMeta):
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
        self.id: str = ""                           # Duration ID

        # 2-2. Private
        self._startDate: datetime.datetime = None   # Duration 시작 시간
        self._endDate: datetime.datetime = None     # Duration 종료 시간
        self._intervals: list = []                  # 비가용 계획 구간 리스트 [(시작 시간, 종료 시간)] : DailyOnce 는 하나의 튜플만 가짐

    def init(self, id: str, cycle_type: str):
        """

        :param id:
        :param cycle_type:
        :return:
        """

        # 2-1. Public
        self.id = id

        # 2-2. Private
        self._set_cycle_type(cycle_type=cycle_type)

    @abstractmethod
    def clip_duration(self,
                      clip_from_date: datetime.datetime,
                      clip_to_date: datetime.datetime):
        """

        :param clip_from_date:
        :param clip_to_date:
        :return:
        """
        pass

    @abstractmethod
    def get_current_duration(self):
        pass

    def _set_cycle_type(self, cycle_type: str):
        """

        :param cycle_type:
        :return:
        """
        self._cycleType = cycle_type
