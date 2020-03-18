
import os
import configparser

from abc import *


class AbstractConfig(metaclass=ABCMeta):

    ####################
    # Static Variables #
    ####################

    # Installation Path
    instationPath: str = \
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )

    # Abstract Class Files Directory
    abstractPath: str = os.path.join(
        instationPath, 'abstract'
    )

    # SCP Simulator Class Files Directory
    scpPath: str = os.path.join(
        instationPath, 'scp'
    )

    # Config.properties file Path
    configPropertiesFile: str = os.path.join(
        instationPath, 'Config.properties'
    )


    def __init__(self):
        self.parser: configparser.RawConfigParser = configparser.RawConfigParser()
        self.parser.read(AbstractConfig.configPropertiesFile)

    def getSectionConfig(self, sectionName: str):
        return dict(self.parser.items(section=sectionName))

    @abstractmethod
    def doSomething(self):
        pass

    @abstractmethod
    def doMyThang(self):
        pass
