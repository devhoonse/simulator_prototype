from m4.ApplicationConfiguration import ApplicationConfiguration
from m4.operator.Factory import Factory


class BackwardPlanner(object):

    def __init__(self):
        self._factory: Factory = None
        self._use_backward_size: bool = True

    def init(self, factory: Factory, config: ApplicationConfiguration):

        # config 객체로부터 설정 정보 받아오기
        self._use_backward_size: bool = bool(config.find('Backward', 'backward.res.size'))

        # Build 된 Factory 인스턴스를 할당
        self._factory = factory

    def plan(self, work_orders: list):
        pass
