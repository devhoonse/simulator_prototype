
import datetime

from ..util.TimeUtility import TimeUtility


class FactoryCalendar(object):
    """
    Factory Calendar Object
    ScheduleSimulator 객체에 종속되어
    전체 시간의 흐름을 구현하기 위한 클래스,
    시뮬레이션 시간 축 정보를 처리
    """

    #  Static 변수들

    # Constants
    _CONSTANT: str = ""     # Constant

    def __init__(self):
        """
        생성자 : 멤버 변수 선언
        """

        # 2-1. Public
        self.owner: str = ""                                # 해당 Calendar 인스턴스의 소유자 정보

        # 2-2. Private
        self._startDate: datetime.datetime = None           # 시작 일자: datetime /
        self._endDate: datetime.datetime = None             # 종료 일자: datetime /
        self._horizonLen: int = 0                           # 총 캘린더 길이 값 : int
        self._timeStepLen: int = 0                          # 시간 간격 길이 값 : int
        self._timeStepDelta: datetime.timedelta = None      # 시간 간격 길이 객체: timedelta
        self._fullCalendar: list = []                       # 전체: [dict: {datetime, 가동여부}] / build_full_calendar()

    def init(self, start_date: object, end_date: object,
             time_step_length: int, time_step_uom: str):
        """
        Calendar 인스턴스에 실제 속성을 세팅하는 처리,
        여기서는 가장 기본적 속성들만 세팅하며,
        비가용 계획 구간 등록 처리는 외부에서 .register_unavailable_interval() 메서드를 통하도록 설계
        :param start_date: object{datetime|str} = 시뮬레이션 시작 일자 정보
        :param end_date: object{datetime|str} = 시뮬레이션 종료 일자 정보
        :param time_step_length: int = TimeStep 시간 길이
        :param time_step_uom: str = TimeStep 시간 길이 단위, 가능 단위는 Calendar._TIME_UNIT_TYPES 참조
        :return: void
        """

        # 시작 및 종료 일자 세팅에 앞서 타입 검사 및 문자열이라면 변환하는 단계
        start_date: datetime.datetime = TimeUtility.check_date_info(date_info=start_date)
        end_date: datetime.datetime = TimeUtility.check_date_info(date_info=end_date)

        # 시작 일자 정보 세팅
        self.set_start_date(start_date=start_date)

        # 종료 일자 정보 세팅
        self.set_end_date(end_date=end_date)

        # 시작일자와 종료일자로부터 self._horizonLen 값을 세팅
        self._build_horizon()

        # timestep 길이 세팅 : 사용자 지정 UOM 단위 ()
        self.set_timestep(timestep_length=time_step_length, uom=time_step_uom)
        self._build_timestep_delta()

        # 세팅된 정보들로부터 Full Calendar Sequence 를 작성
        self.build_full_calendar()

    def get_full_calendar(self):
        """
        self._fullCalendar 를 반환하는 메서드
        :param print_flag: bool = 각 calendar 항목들의 콘솔 출력 여부 / default True
        :return: list<dict>
        """

        return self._fullCalendar

    def get_next_time(self, run_time: dict):
        """
        전달받은 run_time 객체 바로 이후 run_time 객체를 반환해 주는 메서드
        만약 전달받은 run_time 이 마지막이고 이후 아무 캘린더 정보가 없다면 빈 dict 를 반환
        ScheduleSimulator 클래스에서 runTime tick 시에 다음 runTime 이 있는 지 확인하기 위한 용도
        :param run_time:
        :return: dict
        """
        run_time_idx: int = self.get_index(run_time)                # 전달받은 run_time dict 객체의 self._fullCalendar 리스트 내 위치
        run_time_next_idx: int = run_time_idx + 1                   # 전달받은 run_time dict 객체의 다음 위치 값 (index)
        run_time_next: dict = {}                                    # 반환될 다음 run_time dict 객체 변수 선언
        try:
            run_time_next = self._fullCalendar[run_time_next_idx]   # 있을 경우 다음 run_time dict 객체를 할당
        except IndexError:
            pass                                                    # 없을 경우 동작 없음, run_time_next 변수는 빈 dict 인 채로 유지

        return run_time_next                                        # 파악된 다음 run_time 객체를 반환

    def get_first_time(self):
        """
        self._fullCalendar 리스트 내에서 가장 시작 지점의 runTime 정보 dict 객체를 반환하는 메서드
        :return: dict = 가장 시작 지점 runTime 정보
        """
        first_calendar: dict = self._fullCalendar[0]
        return first_calendar

    def get_timestep(self):
        """
        해당 캘린더에 세팅된 _timestep(int: 시간 길이) 값을 반환합니다.
        :return: 시간 구간 길이 (int: 시간 길이)
        """
        return self._timeStepLen

    def get_index(self, run_time: dict):
        """
        전달받은 run_time 객체의 self._fullCalendar 리스트 내 index 순번을 반환하는 메서드
        :param run_time: dict = runTime 정보
        :return: int = self._fullCalendar 리스트 내 index 순번
        """
        run_time_idx: int = self._fullCalendar.index(run_time)      # 전달받은 run_time dict 객체의 self._fullCalendar 리스트 내 위치
        return run_time_idx

    def get_full_calendar_length(self):
        """
        현재 Calendar 인스턴스에 세팅된 self._fullCalendar (전체 캘린더) 갯수를 반환
        :return: int = 전체 캘린더 갯수
        """
        full_calendar_length: int = len(self._fullCalendar)
        return full_calendar_length

    def get_horizon_length(self):
        """
        현재 Calendar 인스턴스에 세팅된 self._horizonLen (초 단위 Horizon 길이) 값을 반환
        :return: int = 캘린더 시작 시점부터 종료 시점까지의 초 단위 시간 간격 길이
        """
        return self._horizonLen

    def build_full_calendar(self):
        """
        현재 Calendar에 세팅된 정보들로부터 Full Calendar Sequence 를 작성
        시작시점(self._startDate)부터 종료시점(self._startDate + self._horizonSec)까지
        self._timestep 초 만큼의 간격으로 캘린더 Sequence가 작성되어
        self._fullCalendar 리스트에 세팅됨
        :return: void
        """

        calendar_no: int = 0        # 초기 Sequence 번호

        # 0초를 기점으로 self._horizonSec 초까지 self._timestep 간격으로 더해가며 차례로 세팅
        for sec in range(0, self._horizonLen + self._timeStepLen, self._timeStepLen):
            # 각 Calendar 정보를 리스트에 순서대로 append 처리
            self._fullCalendar.append(
                {'DATE': self._startDate + calendar_no * self._timeStepDelta,   # 각 Calendar 의 날짜 정보: datetime
                 'WORK_YN': True}                                               # 각 Calendar 의 업무 가능 여부: bool
            )
            calendar_no += 1        # Sequence 번호 + 1

    def _build_horizon(self):
        """
        현재 Calendar에 세팅된 시작 및 종료 시점 정보로부터
        시작부터 종료 시점 사이의 시간 간격을 초 단위로 self._horizonLen 변수에 할당하는 처리
        :return: void
        """
        horizon: datetime.timedelta = self._endDate - self._startDate
        self._horizonLen = int(horizon.total_seconds())

    def set_start_date(self, start_date: datetime.datetime):
        """
        datetime.datetime 형식의 값을 self._startDate 속성으로 할당합니다.
        :param start_date: datetime.datetime 객체
        :return: void
        """
        self._startDate = start_date

    def set_end_date(self, end_date: datetime.datetime):
        """
        datetime.datetime 형식의 값을 self._endDate 속성으로 할당합니다.
        :param end_date: datetime.datetime 객체
        :return:
        """
        self._endDate = end_date

    def set_horizon(self, horizon_length: int, uom: str):
        """
        해당 캘린더의 _horizonSec(int: 초 단위) 값을 설정합니다.
        :param horizon_length: 시간 구간 길이 (int: 길이 정수 값)
        :param uom: 시간 구간 단위 (str : 'seconds', 'minutes', 'hours', ...)
        :return: void
        """
        is_available_uom: bool = TimeUtility.check_timestep_uom(uom=uom)
        if not is_available_uom:
            raise AssertionError(
                f"{self.__class__.__name__}.set_horizon() 의 uom 파라메터에\n"
                f"사용할 수 없는 시간 구간 단위가 설정되었습니다. uom = {uom}"
            )
        horizon_timedelta: datetime.timedelta = TimeUtility.derive_timedelta(
            time_length=horizon_length, uom=uom
        )
        self._horizonLen = int(horizon_timedelta.total_seconds())

    def set_timestep(self, timestep_length: int, uom: str):
        """
        해당 캘린더의 _timestep(int: 초 단위) 값을 설정합니다.
        :param timestep_length: 시간 구간 길이 (int: 길이 정수 값)
        :param uom: 시간 구간 단위 (str : 'seconds', 'minutes', 'hours', ...)
        :return: void
        """
        is_available_uom: bool = TimeUtility.check_timestep_uom(uom=uom)
        if not is_available_uom:
            raise AssertionError(
                f"{self.__class__.__name__}.set_timestep() 의 uom 파라메터에\n"
                f"사용할 수 없는 시간 구간 단위가 설정되었습니다. uom = {uom}"
            )
        timestep_timedelta: datetime.timedelta = TimeUtility.derive_timedelta(
            time_length=timestep_length, uom=uom
        )
        self._timeStepLen = int(timestep_timedelta.total_seconds())

    def _build_timestep_delta(self):
        """
        해당 캘린더에 세팅된 _timestep(int: 초 단위) 값으로부터
        self._timestepDelta 속성을 세팅합니다.
        :return: void
        """
        self._timeStepDelta = datetime.timedelta(seconds=self._timeStepLen)

    def _check_date_info(self, date_info: object):
        """
        넘겨 받은 시작 일자 정보의 값 형식 점검 및 datetime 변환 작업 결과를 반환합니다.
        :param date_info: 시작일자 정보 값, 일반적인 object 를 가정, datetime 인지 str 인지를 검사,
                           이 외의 처리 불가 형식의 경우 Assertion 에러 표출
        :return: datetime.datetime
        """

        if isinstance(date_info, datetime.datetime):
            # start_date 가 datetime.datetime 객체일 경우: 별도 처리 없이 통과
            pass
        elif isinstance(date_info, str):
            # start_date 가 str 객체일 경우: datetime.datetime 객체로 변환
            date_info: datetime.datetime = TimeUtility.convert_str_to_date(date_string=date_info)
        else:
            # start_date 가 datetime 혹은 str 둘 중 어느 것에도 해당되지 않을 경우
            raise AssertionError(
                f"{self.__class__.__name__}.setup_calendar() 의 파라메터 start_date 에 "
                f"{type(date_info)} 타입 값이 할당되었습니다."
            )
        return date_info
