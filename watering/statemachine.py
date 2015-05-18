
import logging


class AbstractState(object):
    def __init__(self, statemachine):
        self._statemachine = statemachine
        self.logger = logging.getLogger(self.__class__.__name__)

    def handle_lower_sensor(self, state):
        self.logger.debug('Unhandled lower sensor')

    def handle_upper_sensor(self, state):
        self.logger.debug('Unhandled upper sensor')


class IdleState(AbstractState):
    def handle_lower_sensor(self, state):
        if state:
            self.logger.info('Lower sensor True, should start pumping')
            self._statemachine.set_new_state('PumpAction')


class PumpAction(AbstractState):
    def handle_upper_sensor(self, state):
        if state:
            self.logger.info('Upper sensor True, should stop pumping')
            self._statemachine.set_new_state('Idle')


class LowAlarm(AbstractState):
    pass


class StateMachine(object):
    def __init__(self):
        self._states = {
            'Idle': IdleState(self),
            'PumpAction': PumpAction(self),
            'LowAlarm': LowAlarm(self),
        }
        self.set_new_state('Idle')

    def set_new_state(self, statename):
        self._currentstate = self._states[statename]

    def __getattr__(self, attr):
        if hasattr(self._currentstate, attr):
            return getattr(self._currentstate, attr)
        else:
            return super(StateMachine, self).__getattr__(attr)
