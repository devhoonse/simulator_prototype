
import datetime
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
        self.scheduleSimulator.run_time()

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

        try:
            self.scheduleSimulator.setup_object(
                start_date=start_date,
                timestep_length=timestep_length, timestep_uom=timestep_uom,
                horizon_length=horizon_length, horizon_uom=horizon_uom
            )
        except AssertionError:
            print("\ttimestep 및 horizon에 microsecond 세팅 불가 !!")

        # self.scheduleSimulator.run_time()


if __name__ == '__main__':
    tester: ScheduleSimulatorTestCase = ScheduleSimulatorTestCase()
    tester.setUp()
    tester.test_setup_with_datetime()
    tester.test_setup_with_str()
