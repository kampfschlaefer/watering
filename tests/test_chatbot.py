
from errbot.backends.test import testbot, push_message, pop_message
import pytest


__extra_fixtures = testbot


@pytest.mark.usefixtures('testbot')
class TestChatbot(object):
    extra_plugin_dir = '.'

    def test_help(self):
        push_message('!help WaterBot')
        assert 'Say hello' in pop_message()

    def test_hello(self):
        push_message('!hello')
        assert 'Hello' in pop_message()
