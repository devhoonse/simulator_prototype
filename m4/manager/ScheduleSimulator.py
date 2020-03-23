
import math

from m4.manager.Calendar import Calendar


class ScheduleSimulator(object):

    # Static

    # Constants

    def __init__(self):
        """
        생성자 :
        """

        # 2-1. Public

        # 2-2. Private
        self._startDate: object = None          # Simulator 엔진 시작 시점: datetime or str
        self._timestepLength: int = 0           # 매 시간 구간 간격 길이: int
        self._timestepUom: str = ""             # 매 시간 구간 간격 단위: str
        self._horizonLength: int = 0            # 전체 시간 구간 간격 길이: int
        self._horizonUom: str = ""              # 전체 시간 구간 간격 단위: str
        self._calendar: Calendar = Calendar()   # Simulator 전체 시간 범위 Calendar 객체
        self._calendar_len: int = 0             # Simulator 전체 시간 리스트 객체 / Will be Deprecated
        self._runTime: dict = {}                # Simulator 의 현재 runTime 위치 (int)

    def setup_object(self, start_date: object,
                     timestep_length: int, timestep_uom: str,
                     horizon_length: int, horizon_uom: str):
        """
        ScheduleSimulator 인스턴스에 실제 속성을 세팅하는 처리
        :param start_date: object{datetime|str} = 시뮬레이션 시작 일자 정보
        :param timestep_length: int = Timestep 시간 길이
        :param timestep_uom: str = Timestep 시간 길이 단위, 가능 단위는 Calendar._TIME_UNIT_TYPES 참조
        :param horizon_length: int = Horizon 시간 길이
        :param horizon_uom: str = Horizon 시간 길이 단위, 가능 단위는 Calendar._TIME_UNIT_TYPES 참조
        :return: void
        """

        # ScheduleSimulator 객체 속성 값 설정
        self._set_start_date(start_date=start_date)                  # Simulator 엔진 시작 시점: datetime or str
        self._set_timestep_length(timestep_length=timestep_length)   # 매 시간 구간 간격 길이: int
        self._set_timestep_uom(timestep_uom=timestep_uom)            # 매 시간 구간 간격 단위: str
        self._set_horizon_length(horizon_length=horizon_length)      # 전체 시간 구간 간격 길이: int
        self._set_horizon_uom(horizon_uom=horizon_uom)               # 전체 시간 구간 간격 단위: str

        # Calendar 객체 setup
        self._calendar.setup_calendar(
            start_date=self._startDate,
            timestep_length=self._timestepLength, timestep_uom=self._timestepUom,
            horizon_length=self._horizonLength, horizon_uom=self._horizonUom
        )

        # Calendar 객체에 세팅된 runTime 수 파악
        self._calendar_len = self._calendar.get_full_calendar_length()

    def run_time(self, print_flag: bool = True):
        """
        self._calendar._fullCalendar 에 세팅된 각 캘린더 항목 별로 Loop 를 도는 메서드
        :param print_flag: bool = 각 calendar 항목들의 콘솔 출력 여부 / default True
        :return: void
        """

        # number_of_digits = 콘솔 출력용 자릿수 값
        # 예를 들어 calendar 갯수가 86400 개라고 하면,
        # number_of_digits 값은 5 가 됨.
        # 콘솔에 출력 시 00000 ~ 86400 으로 캘린더 번호의 자릿수를 맞추기 위한 변수
        number_of_digits: int = math.floor(math.log(self._calendar_len, 10)) + 1

        # 시뮬레이션 시작에 앞서, self._runTime 값을 self._calendar 의 가장 첫 시작 값으로 설정
        self._runTime: dict = self._calendar.get_first_time()

        # 시뮬레이션 종료 여부를 판단하기 위해, 다음 runTime 이 있는 지 확인을 위한 bool 변수 선언
        has_next: bool = True

        # 다음 시간 정보가 있는 한 계속 시간을 앞으로 보내도록 설계
        while has_next:
            if print_flag:                      # print_flag 가 설정되어 있을 경우, 콘솔에 출력
                idx_string: str = '%0{}d'.format(number_of_digits) % \
                                  self._calendar.get_index(run_time=self._runTime)  # 현재 캘린더의 위치 index
                print(f"\t{idx_string}"                     # 각 Calendar 번호: int
                      f"\t{self._runTime['DATE']}"          # 각 Calendar 의 날짜 정보: datetime
                      f"\t{self._runTime['WORK_YN']}")      # 각 Calendar 의 업무 가능 여부: bool

            # 다음 runTime 이 있는 지 확인,
            # 있으면 True 반환 및 self._runTime을 다음 runTime 값으로 업데이트
            # 없으면 False 반환 및 self._runTime 유지
            has_next = self.tick_one_time()

        # # Calendar 들을 순서대로 하나씩 꺼내며 Loop
        # for obj in self._calendar_full:
        #     cal: dict = obj                     # 현재 캘린더
        #     if print_flag:                      # print_flag 가 설정되어 있을 경우, 콘솔에 출력
        #         print(f"\t{'%0{}d'.format(number_of_digits) % self._calendar_full.index(obj)}"  # 각 Calendar 번호: int
        #               f"\t{cal['DATE']}"        # 각 Calendar 의 날짜 정보: datetime
        #               f"\t{cal['WORK_YN']}")    # 각 Calendar 의 업무 가능 여부: bool

    def tick_one_time(self):
        """
        현재 self._runTime 값을 업데이트,
        self._calendar 에 정의된
        추후 이 메서드에 정의된 tick 메서드에 의해
        Factory 내 각 Entity 들의 Time tick 또한 연동되도록 설계 필요
        :return: bool = 다음 runtime 이 없다면 False, 있다면 True / run_time 메서드에서 참조될 Flag 성 정보
        """
        next_runtime: dict = self._calendar.get_next_time(run_time=self._runTime)   # 현재 self._runTime 다음 runtime get
        has_next_runtime: bool = next_runtime != {}                                 # 다음 runtime 이 비었으면 False

        # 다음 runtime 이 있을 경우에만 현재 ScheduleSimulator 의 self._runTime 값을 업데이트
        if has_next_runtime:
            self._runTime = next_runtime

        return has_next_runtime

    def _set_start_date(self, start_date: object):
        """
        start_date 값을 self._startDate 속성으로 할당합니다.
        :param start_date: 일반적인 object 를 상정, datetime 인지 str 인지를
                           Calendar 인스턴스가 판단하여 내부에서 처리할 것
        :return: void
        """
        self._startDate = start_date

    def _set_timestep_length(self, timestep_length: int):
        """
        timestep_length 값을 self._timestepLength 속성으로 할당합니다.
        :param timestep_length: 시간 구간 길이 (int: 길이 정수 값)
        :return: void
        """
        self._timestepLength = timestep_length

    def _set_timestep_uom(self, timestep_uom: str):
        """
        timestep_uom 값을 self._timestepUom 속성으로 할당합니다.
        :param timestep_uom: 시간 구간 단위 (str : 'seconds', 'minutes', 'hours', ...)
        :return: void
        """
        self._timestepUom = timestep_uom

    def _set_horizon_length(self, horizon_length: int):
        """
        horizon_length 값을 self._horizonLength 속성으로 할당합니다.
        :param horizon_length: 시간 구간 길이 (int: 길이 정수 값)
        :return: void
        """
        self._horizonLength = horizon_length

    def _set_horizon_uom(self, horizon_uom: str):
        """
        horizon_uom 값을 self._horizonUom 속성으로 할당합니다.
        :param horizon_uom: 시간 구간 단위 (str : 'seconds', 'minutes', 'hours', ...)
        :return: void
        """
        self._horizonUom = horizon_uom
