
import gevent
from pyfacedigitalio import (
    PiFaceDigital, InputEventListener, IODIR_RISING_EDGE
)

from statemachine import StateMachine


class PumpController(StateMachine):
    def __init__(self):
        super(PumpController, self).__init__()

        self.pfd = PiFaceDigital()

        self.listener = InputEventListener(chip=self.pfd)
        self.listener.register(0, IODIR_RISING_EDGE, self.input0)
        self.listener.activate()

    def set_pump_state(self, state):
        self.pfd.relays[0].value = state

    def input0(self, event):
        self.logger.info('Input event %s', event)


def run():
    import logging

    logging.basicConfig()

    pc = PumpController()

    gevent.sleep(300)

    del pc
