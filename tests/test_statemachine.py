
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

    @pytest.mark.parametrize(
        'initialstate, sensor, sensor_state, targetstate',
        (
            ('Idle', 'handle_lower_sensor', True, 'PumpAction'),
            ('PumpAction', 'handle_upper_sensor', True, 'IdleState'),
            ('PumpAction', 'handle_timeout', True, 'LowAlarm'),
            ('LowAlarm', 'handle_button', True, 'PumpAction'),
            ('Idle', 'handle_button', True, 'PumpAction'),
        )
    )
    def test_single_state_changes(
        self, statemachine, initialstate, sensor, sensor_state, targetstate
    ):
        statemachine.set_new_state(initialstate)

        getattr(statemachine, sensor)(sensor_state)

        self.check_state(statemachine, targetstate)
