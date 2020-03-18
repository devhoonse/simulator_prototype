from abstract.util.AbstractConfig import AbstractConfig


class Config(AbstractConfig):

    def __init__(self):
        super().__init__()
        self.parser.read(AbstractConfig.configPropertiesFile)

    def doSomething(self):
        print("doSomething")
        super().doSomething()
        print("doSomething2")

    def doMyThang(self):
        print("doMyThang")
        super().doMyThang()
        print("doMyThang2")
