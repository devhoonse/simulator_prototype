
import os
import unittest


from scp.util.Config import Config


class ConfigBaseTest(unittest.TestCase):
    """
    Reference: https://stackoverflow.com/questions/3595363/properties-file-in-python-similar-to-java-properties
    """

    def setUp(self) -> None:

        __SECTION1: str = "DatabaseSource"
        __SECTION2: str = "FileSource"

        self.config: Config = Config()

        # for test 1
        self.databaseSourceConfig: dict = self.config.getSectionConfig(__SECTION1)
        self.__databaseName: str = self.databaseSourceConfig['database.scheme.name']
        self.__databaseIp: str = self.databaseSourceConfig['database.connection.ip']

        # for test 2
        self.fileSourceConfig: dict = self.config.getSectionConfig(__SECTION2)
        self.__fileSourceDirectory: str = self.fileSourceConfig['file.directory']
        self.__fileSourceDemand: str = self.fileSourceConfig['file.demand']
        self.__fileSourceEngineConfig: str = self.fileSourceConfig['file.engineconfig']

    def test1(self):
        print(f"\n==============================================\n"
              f"DatabaseSource\n"
              f"\t{self.__databaseName} | {self.__databaseIp}")

    def test2(self):
        print(f"\n==============================================\n"
              f"FileSource\n"
              f"\tDirectory = {self.__fileSourceDirectory}\n"
              f"\t\tDemand = {self.__fileSourceDemand}\n"
              f"\t\tEngineConfig = {self.__fileSourceEngineConfig}")


if __name__ == '__main__':

    baseTest: ConfigBaseTest = ConfigBaseTest()
    baseTest.setUp()

    baseTest.test1()
    baseTest.test2()
