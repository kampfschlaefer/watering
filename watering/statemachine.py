
import logging


class AbstractState(object):
    def __init__(self, statemachine):
        self._statemachine = statemachine
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        pass

    def stop(self):
        pass

    def handle_lower_sensor(self, state):
        self.logger.debug('Unhandled lower sensor')

    def handle_upper_sensor(self, state):
        self.logger.debug('Unhandled upper sensor')

    def handle_button(self, state):
        self.logger.debug('Unhandled button event')

    def handle_timeout(self, state=None):
        self.logger.debug('%s: Unhandled timeout', self.__class__.__name__)


class MaxState(AbstractState):
    def handle_upper_sensor(self, state):
        if not state:
            self.logger.info('Upper sensor False, going to idle state')
            self._statemachine.set_new_state('IdleState')


class IdleState(AbstractState):
    def handle_upper_sensor(self, state):
        if state:
            self.logger.info('Upper sensor True, going to max state')
            self._statemachine.set_new_state('MaxState')

    def handle_lower_sensor(self, state):
        if not state:
            self.logger.info('Lower sensor False, should start pumping')
            self._statemachine.set_new_state('PumpAction')

    def handle_button(self, state):
        self.logger.info('Button triggered pump action')
        self._statemachine.set_new_state('PumpAction')


class PumpAction(AbstractState):
    def start(self):
        self._statemachine.set_pump_state(True)

    def stop(self):
        self.logger.info('delete PumpAction')
        self._statemachine.set_pump_state(False)
        self.logger.info('PumpAction gone')

    def handle_upper_sensor(self, state):
        if state:
            self.logger.info('Upper sensor True, should stop pumping')
            self._statemachine.set_new_state('MaxState')

    def handle_timeout(self, state=None):
        self.logger.warning(
            'Timeout occured while the pump was running. '
            'Probably the tank is empty!'
        )
        self._statemachine.set_new_state('LowAlarm')


class LowAlarm(AbstractState):
    def handle_button(self, state):
        self.logger.info('Button triggered pump action')
        self._statemachine.set_new_state('PumpAction')


class StateMachine(object):
    def __init__(self, loop, state_timeout=30):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._states = {
            'IdleState': IdleState,
            'PumpAction': PumpAction,
            'LowAlarm': LowAlarm,
            'MaxState': MaxState,
        }
        self.loop = loop
        self._timeout_handle = None
        self._currentstate = None
        self._state_timeout = state_timeout
        self.set_new_state('IdleState')

    def set_new_state(self, statename):
        oldstate = self._currentstate
        if oldstate:
            self.logger.debug(
                'Switching state from %s to %s',
                oldstate.__class__.__name__,
                statename
            )
        else:
            self.logger.debug(
                'Switching to state %s', statename
            )
        if self._timeout_handle:
            self._timeout_handle.cancel()
            self.logger.debug('killed a timer')
        self._currentstate = self._states[statename](self)
        self._currentstate.start()
        self.logger.debug('new timer with timeout %g', self._state_timeout)
        self._timeout_handle = self.loop.call_later(
            self._state_timeout,
            self.handle_timeout
        )
        self.logger.debug('stopping old state %s', oldstate.__class__.__name__)
        if oldstate:
            oldstate.stop()

    def set_pump_state(self, state):
        self.logger.warning('This is not a real pump controller...')

    def __getattr__(self, attr):
        if hasattr(self._currentstate, attr):
            return getattr(self._currentstate, attr)
        else:
            return getattr(super(StateMachine, self), attr)
