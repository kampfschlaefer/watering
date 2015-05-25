
import os
from errbot.backends.test import testbot, push_message, pop_message

# import pytest


class TestChatbot(object):
    extra_plugins_dir = '../watering'

    def test_hello(self, testbot):
        push_message('!hello')
        assert 'Hello' in pop_message()
