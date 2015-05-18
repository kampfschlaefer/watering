
import pytest

from watering.statemachine import StateMachine


@pytest.fixture
def statemachine():
    return StateMachine()


class TestSimpleStates(object):

    def check_state(self, statemachine, statename):
        assert statemachine._currentstate.__class__.__name__ == statename

    def test_initial_state(self, statemachine):
        self.check_state(statemachine, 'IdleState')

    def test_low_water(self, statemachine):
        statemachine.handle_lower_sensor(True)

        self.check_state(statemachine, 'PumpAction')

    def test_high_water(self, statemachine):
        statemachine.set_new_state('PumpAction')

        statemachine.handle_upper_sensor(True)

        self.check_state(statemachine, 'IdleState')
