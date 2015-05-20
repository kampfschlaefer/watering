
import gevent
from pifacedigitalio import (
    PiFaceDigital,
    IODIR_RISING_EDGE,
    IODIR_BOTH,
)
from interrupts import InputEventListener

from statemachine import StateMachine


class PumpController(StateMachine):
    def __init__(self):
        super(PumpController, self).__init__()

        self.pfd = PiFaceDigital()

        self.listener = InputEventListener(chip=self.pfd)
        self.listener.register(0, IODIR_BOTH, self.in_upper)
        self.listener.register(1, IODIR_RISING_EDGE, self.in_lower)
        self.listener.register(3, IODIR_RISING_EDGE, self.in_button)
        self.listener.activate()

    def stop(self):
        self.listener.deactivate()

    def set_pump_state(self, state):
        self.pfd.relays[0].value = state

    def in_upper(self, event):
        self.logger.info('Input event pin0 (upper) %s', event)
        self.handle_upper_sensor(event.direction != 1)

    def in_lower(self, event):
        self.logger.info('Input event pin1 (lower) %s', event)
        self.handle_lower_sensor(False)

    def in_button(self, event):
        self.logger.info('Input event pin3 (button) %s', event)
        self.handle_button(True)


def run():
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.info('starting main thread')

    pc = PumpController()

    try:
        while True:
            gevent.sleep(10)
    except KeyboardInterrupt:
        pass

    logging.info('ending...')
    pc.stop()
    logging.info('...finished')
