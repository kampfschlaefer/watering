
import pytest

from watering.statemachine import StateMachine


@pytest.fixture
def statemachine():
    return StateMachine()


@pytest.fixture
def pumpstatemachine():
    class PumpStateMachine(StateMachine):
        def __init__(self):
            super(PumpStateMachine, self).__init__()
            self.pump_state = False

        def set_pump_state(self, state):
            self.pump_state = state

    return PumpStateMachine()


class TestSimpleStates(object):

    def check_state(self, statemachine, statename):
        assert statemachine._currentstate.__class__.__name__ == statename

    def test_initial_state(self, statemachine):
        self.check_state(statemachine, 'IdleState')

    @pytest.mark.parametrize(
        'initialstate, sensor, sensor_state, targetstate',
        (
            ('IdleState', 'handle_lower_sensor', False, 'PumpAction'),
            ('IdleState', 'handle_upper_sensor', True, 'MaxState'),
            ('IdleState', 'handle_button', True, 'PumpAction'),
            ('PumpAction', 'handle_upper_sensor', True, 'MaxState'),
            ('PumpAction', 'handle_timeout', True, 'LowAlarm'),
            ('MaxState', 'handle_upper_sensor', False, 'IdleState'),
            ('LowAlarm', 'handle_button', True, 'PumpAction'),
        )
    )
    def test_single_state_changes(
        self, statemachine, initialstate, sensor, sensor_state, targetstate
    ):
        statemachine.set_new_state(initialstate)

        getattr(statemachine, sensor)(sensor_state)

        self.check_state(statemachine, targetstate)

    @pytest.mark.parametrize(
        'initialstate, sensor, sensor_state',
        (
            ('IdleState', 'handle_upper_sensor', False),
            ('MaxState', 'handle_button', True),
            ('MaxState', 'handle_button', False),
            ('PumpAction', 'handle_button', True),
            ('PumpAction', 'handle_button', False),
            ('PumpAction', 'handle_lower_sensor', True),
        )
    )
    def test_no_state_changed(
        self, statemachine, initialstate, sensor, sensor_state
    ):
        statemachine.set_new_state(initialstate)

        getattr(statemachine, sensor)(sensor_state)

        self.check_state(statemachine, initialstate)


class TestPumpStates(object):
    def test_idle_pump(self, pumpstatemachine):
        assert not pumpstatemachine.pump_state

    def test_start_pump(self, pumpstatemachine):
        pumpstatemachine.handle_lower_sensor(False)

        assert pumpstatemachine.pump_state

    def test_stop_pump(self, pumpstatemachine):
        pumpstatemachine.handle_lower_sensor(False)

        pumpstatemachine.handle_upper_sensor(True)

        assert not pumpstatemachine.pump_state
