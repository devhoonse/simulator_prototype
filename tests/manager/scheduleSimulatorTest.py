
import datetime
import math
import unittest

from m4.manager.Calendar import Calendar
from m4.manager.ScheduleSimulator import ScheduleSimulator


class ScheduleSimulatorTestCase(unittest.TestCase):

    def setUp(self) -> None:

        # 테스트용 ScheduleSimulator 인스턴스 생성
        self.scheduleSimulator: ScheduleSimulator = ScheduleSimulator()

    def test_setup_with_datetime(self):
        """
        start_date 파라메터를 datetime 형식으로 넘겨 줄 경우에 대한 테스트
        :return: void
        """

        start_date: datetime.datetime = datetime.datetime(year=2020, month=3, day=23)
        timestep_length: int = 1
        timestep_uom: str = "days"
        horizon_length: int = 15
        horizon_uom: str = "days"

        # Test 정보 출력
        print(f"\nSimulation Start")
        print(f"\tSTART_DATE : {start_date}")
        print(f"\tTIME_STEP : {timestep_length} {timestep_uom}")
        print(f"\tHORIZON : {horizon_length} {horizon_uom}")

        self.scheduleSimulator.setup_object(
            start_date=start_date,
            timestep_length=timestep_length, timestep_uom=timestep_uom,
            horizon_length=horizon_length, horizon_uom=horizon_uom
        )

        ##############################################################################
        # 외부에서 ScheduleSimulator 인스턴스 생성하여 시뮬레이션을 하고자 하는 경우      #
        # 아래와 같이 쓰면 됩니다                                                      #
        ##############################################################################

        # number_of_digits = 콘솔 출력용 자릿수 값
        # 예를 들어 calendar 갯수가 86400 개라고 하면,
        # number_of_digits 값은 5 가 됨.
        # 콘솔에 출력 시 00000 ~ 86400 으로 캘린더 번호의 자릿수를 맞추기 위한 변수
        number_of_calendars: int = self.scheduleSimulator.get_calendar_length()
        number_of_digits: int = math.floor(math.log(number_of_calendars, 10)) + 1

        # 시뮬레이션 시작에 앞서, self._runTime 값을 self._calendar 의 가장 첫 시작 값으로 설정
        self.scheduleSimulator.stand_by()

        # 시뮬레이션 종료 여부를 판단하기 위해, 다음 runTime 이 있는 지 확인을 위한 bool 변수 선언
        has_next: bool = True

        # 다음 시간 정보가 있는 한 계속 시간을 앞으로 보내도록 설계
        while has_next:
            # 현재 진행중인 runTime 값
            current_run_time: dict = self.scheduleSimulator.get_current_run_time()
            if True:  # print_flag 가 설정되어 있을 경우, 콘솔에 출력
                # 현재 캘린더의 위치 index 를 문자열 Formatting     ex: 00000 ~ 86400
                idx_string: str = '%0{}d'.format(number_of_digits) % \
                                  self.scheduleSimulator._calendar.get_index(run_time=current_run_time)
                print(f"\t[{idx_string}]"  # 각 Calendar 번호: int
                      f"\t{current_run_time['DATE']}"  # 각 Calendar 의 날짜 정보: datetime
                      f"\t{current_run_time['WORK_YN']}")  # 각 Calendar 의 업무 가능 여부: bool

            # 다음 runTime 이 있는 지 확인,
            # 있으면 True 반환 및 self._runTime을 다음 runTime 값으로 업데이트
            # 없으면 False 반환 및 self._runTime 유지
            has_next = self.scheduleSimulator.tick_one_time()

    def test_setup_with_str(self):
        """
        start_date 파라메터를 str 형식으로 넘겨 줄 경우에 대한 테스트
        :return: void
        """

        # start_date 값이 아래와 같이 문자열로 넘어 올 경우를 상정
        # datetime 변환 시 format이 필요하므로 변환 처리를 위한 format 문자열도 함께 설정
        start_date_format: str = "%Y-%m-%d %H:%M:%S"
        Calendar.set_date_str_format(format_string=start_date_format)

        start_date: str = "2020-03-23 00:00:00"
        timestep_length: int = 1
        timestep_uom: str = "hours"
        horizon_length: int = 2
        horizon_uom: str = "days"

        # Test 정보 출력
        print(f"\nSimulation Start")
        print(f"\tSTART_DATE : {start_date}")
        print(f"\tTIME_STEP : {timestep_length} {timestep_uom}")
        print(f"\tHORIZON : {horizon_length} {horizon_uom}")
        self.scheduleSimulator.setup_object(
            start_date=start_date,
            timestep_length=timestep_length, timestep_uom=timestep_uom,
            horizon_length=horizon_length, horizon_uom=horizon_uom
        )

        # ScheduleSimulator 인스턴스 자체의 run_time 메서드를 활용해 시뮬레이션을 하고자 하는 경우
        self.scheduleSimulator.run_time()

    def test_setup_with_str_microsec_step(self):
        """
        start_date 파라메터를 str 형식으로 넘겨 줄 경우에 대한 테스트
        timestep 단위가 지원되지 않는 단위로 설정되었을 경우에 대한 테스트 : 이 테스트에서는 microseconds
        :return: void
        """

        # start_date 값이 아래와 같이 문자열로 넘어 올 경우를 상정
        # datetime 변환 시 format이 필요하므로 변환 처리를 위한 format 문자열도 함께 설정
        start_date_format: str = "%Y-%m-%d %H:%M:%S"
        Calendar.set_date_str_format(format_string=start_date_format)

        start_date: str = "2020-03-23 00:00:00"
        timestep_length: int = 1
        timestep_uom: str = "microseconds"
        horizon_length: int = 2
        horizon_uom: str = "days"

        # Test 정보 출력
        print(f"\nSimulation Start")
        print(f"\tSTART_DATE : {start_date}")
        print(f"\tTIME_STEP : {timestep_length} {timestep_uom}")
        print(f"\tHORIZON : {horizon_length} {horizon_uom}")

        # microsecond 세팅 시 setup_object 내부에서 Assertion Error
        try:
            self.scheduleSimulator.setup_object(
                start_date=start_date,
                timestep_length=timestep_length, timestep_uom=timestep_uom,
                horizon_length=horizon_length, horizon_uom=horizon_uom
            )
        except AssertionError:
            print("\ttimestep 및 horizon에 microsecond 세팅 불가 !!")

        # ScheduleSimulator 인스턴스 자체의 run_time 메서드를 활용해 시뮬레이션을 하고자 하는 경우
        # self.scheduleSimulator.run_time()


if __name__ == '__main__':
    tester: ScheduleSimulatorTestCase = ScheduleSimulatorTestCase()
    tester.setUp()
    tester.test_setup_with_datetime()
    tester.test_setup_with_str()
