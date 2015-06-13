
from errbot.backends.test import testbot, push_message, pop_message


class TestChatbot(object):
    extra_plugin_dir = '.'

    def test_help(self, testbot):
        push_message('!help WaterBot')
        assert 'Say hello' in pop_message()

    def test_hello(self, testbot):
        push_message('!hello')
        assert 'Hello' in pop_message()
