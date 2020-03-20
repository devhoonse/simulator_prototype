import os
import configparser


class ApplicationConfiguration:
    # properties file path : working directory path
    PROPERTIES_FILE_PATH: str = \
        os.path.dirname(
                os.path.dirname(__file__)
        )

    def __init__(self):
        pass

    def init(self, properties_file):
        config = configparser.ConfigParser()
        config.read(self.PROPERTIES_FILE_PATH + properties_file)
        print(config)
