
import gevent
from pifacedigitalio import (
    PiFaceDigital, InputEventListener, IODIR_RISING_EDGE
)

from statemachine import StateMachine


class PumpController(StateMachine):
    def __init__(self):
        super(PumpController, self).__init__()

        self.pfd = PiFaceDigital()

        self.listener = InputEventListener(chip=self.pfd)
        self.listener.register(0, IODIR_RISING_EDGE, self.input0)
        self.listener.register(1, IODIR_RISING_EDGE, self.input1)
        self.listener.register(3, IODIR_RISING_EDGE, self.input3)
        self.listener.activate()

    def stop(self):
        # self.logger('stopping listener')
        self.listener.deactivate()

    def set_pump_state(self, state):
        self.pfd.relays[0].value = state

    def input0(self, event):
        self.logger.info('Input event pin0 %s', event)
        self.handle_upper_sensor(True)

    def input1(self, event):
        self.logger.info('Input event pin1 %s', event)
        self.handle_lower_sensor(True)

    def input3(self, event):
        self.logger.info('Input event pin3 %s', event)
        self.handle_button(True)


def run():
    import logging

    logging.basicConfig(level=logging.DEBUG)

    pc = PumpController()

    try:
        while True:
            gevent.sleep(10)
    except KeyboardInterrupt:
        pass

    logging.info('ending...')
    pc.stop()
    logging.info('...finished')
