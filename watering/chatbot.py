
import logging
# import asyncio
from errbot import BotPlugin, botcmd

# from watering.statemachine import StateMachine


class WaterBot(BotPlugin):
    'My water bot'

    # def __init__(self, *args, **kwargs):
    #     ret = super().__init__(*args, **kwargs)
    #     self.logger = logging.getLogger(self.__class__.__name__)
    #     self.logger.info('**\n** init **\n**')
    #     logging.info('## init2 ##')
    #     return ret

    def activate(self):
        super().activate()
        logging.info('Activating the waterbot')
        # self.loop = asyncio.new_event_loop()
        # self.sm = StateMachine(loop=self.loop)
        # self.loop.run_forever()

    def deactivate(self):
        super().deactivate()
        # self.sm.stop()
        # self.loop.stop()

    @botcmd
    def hello(self, message, args):
        'Say hello'
        return 'Hello'

    @botcmd
    def pumpstatus(self, message, args):
        'Get the status'
        return 'I don\'t know yet how to tell the status:-('
