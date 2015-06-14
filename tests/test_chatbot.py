
from errbot.backends.test import testbot, push_message, pop_message
import pytest


__extra_fixtures = testbot


@pytest.mark.usefixtures('testbot')
class TestChatbot(object):
    extra_plugin_dir = '.'

    def test_help(self):
        push_message('!help WaterBot')
        answer = pop_message()
        assert 'Say hello' in answer

    def test_hello(self):
        push_message('!hello')
        answer = pop_message()
        assert 'Hello' in answer

    @pytest.mark.xfail
    def test_get_status(self):
        push_message('!pumpstatus')
        answer = pop_message()
        assert 'Idle' in answer
