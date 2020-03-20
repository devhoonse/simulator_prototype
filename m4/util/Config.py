
import os
import configparser


class Config(object):
    """

    """

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
        instationPath, 'm4'
    )

    # Config.properties file Path
    configPropertiesFile: str = os.path.join(
        instationPath, 'Config.properties'
    )

    def __init__(self):
        self.parser: configparser.RawConfigParser = configparser.RawConfigParser()
        self.parser.read(Config.configPropertiesFile)

    def __del__(self):
        self.parser.clear()

    def getSectionConfig(self, sectionName: str):
        return dict(self.parser.items(section=sectionName))
