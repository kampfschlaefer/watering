
import asyncio
from pifacedigitalio import (
    PiFaceDigital,
    IODIR_RISING_EDGE,
    IODIR_BOTH,
    InputEventListener
)

from .statemachine import StateMachine


class PumpController(StateMachine):
    def __init__(self, loop):
        super(PumpController, self).__init__(loop)

        self.pfd = PiFaceDigital()

        self.listener = InputEventListener(chip=self.pfd)
        self.listener.register(0, IODIR_BOTH, self.in_upper)
        self.listener.register(1, IODIR_RISING_EDGE, self.in_lower)
        self.listener.register(3, IODIR_RISING_EDGE, self.in_button)
        self.listener.activate()

    def stop(self):
        self.pfd.output_port.all_off()
        self.listener.deactivate()

    def set_pump_state(self, state):
        self.pfd.relays[0].value = state

    def in_upper(self, event):
        self.logger.info('Input event pin0 (upper)')
        self.loop.call_soon_threadsafe(
            self.handle_upper_sensor,
            event.direction != 1
        )

    def in_lower(self, event):
        self.logger.info('Input event pin1 (lower)')
        self.loop.call_soon_threadsafe(self.handle_lower_sensor, False)

    def in_button(self, event):
        self.logger.info('Input event pin3 (button)')
        self.loop.call_soon_threadsafe(self.handle_button, True)


def run():
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logging.info('starting main thread')

    loop = asyncio.get_event_loop()

    pc = PumpController(loop)

    loop.run_forever()

    logging.info('ending...')
    pc.stop()
    loop.close()
    logging.info('...finished')
