
from errbot import BotPlugin, botcmd

class WaterBot(BotPlugin):
    @botcmd
    def hello(self, message, args):
        return "Hello"
