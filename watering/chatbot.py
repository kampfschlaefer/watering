
from errbot import BotPlugin, botcmd


class WaterBot(BotPlugin):
    'My water bot'

    @botcmd
    def hello(self, message, args):
        'Say hello'
        return "Hello"
