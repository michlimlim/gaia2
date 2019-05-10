from unit.unit import TestCalculator
from src.update_metadata.device_fairness import DeviceFairnessReceiverState


def test_determine_fairness_given_internal_state(calc):
    calc.context('[Device Epoch Fairness] Determine fairness given internal state')
    state_1_d = {
        '127.0.0.1:5000': 0,
        '127.0.0.1:5001': 0,
        '127.0.0.1:5002': 0
    }
    state_2_d = {
        '127.0.0.1:5000': 2,
        '127.0.0.1:5001': 4,
        '127.0.0.1:5002': 4
    }
    state_1 = DeviceFairnessReceiverState(2, state_1_d)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == True)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5001') == True)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5002') == True)
    state_2 = DeviceFairnessReceiverState(2, state_2_d)
    calc.check(state_2.check_fairness_before_backprop('127.0.0.1:5000') == True)
    calc.check(state_2.check_fairness_before_backprop('127.0.0.1:5001') == False)
    calc.check(state_2.check_fairness_before_backprop('127.0.0.1:5002') == False)

def test_update_internal_state_after_backprop(calc):
    calc.context('[Device Epoch Fairness] Update internal state after backprop correctly')
    state_1_d = {
        '127.0.0.1:5000': 0,
        '127.0.0.1:5001': 0,
        '127.0.0.1:5002': 0
    }
    state_1 = DeviceFairnessReceiverState(2, state_1_d)
    state_1.update_internal_state_after_backprop('127.0.0.1:5000')
    calc.check(state_1.device_ip_addr_to_epoch_dict['127.0.0.1:5000'] == 1)
    calc.check(state_1.device_ip_addr_to_epoch_dict['127.0.0.1:5001'] == 0)
    calc.check(state_1.device_ip_addr_to_epoch_dict['127.0.0.1:5002'] == 0)
    state_1.update_internal_state_after_backprop('127.0.0.1:5000')
    calc.check(state_1.device_ip_addr_to_epoch_dict['127.0.0.1:5000'] == 2)
    calc.check(state_1.device_ip_addr_to_epoch_dict['127.0.0.1:5001'] == 0)
    calc.check(state_1.device_ip_addr_to_epoch_dict['127.0.0.1:5002'] == 0)

def test_update_internal_state_after_aggregation(calc):
    calc.context('[Device Epoch Fairness] Update internal state correctly')
    state_1_d = {
        '127.0.0.1:5000': 0,
        '127.0.0.1:5001': 0,
        '127.0.0.1:5002': 0
    }
    # (0, 0, 0)
    state_1 = DeviceFairnessReceiverState(2, state_1_d)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == True)
    # (1, 0, 0)
    state_1.update_internal_state_after_backprop('127.0.0.1:5000')
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == True)
    # (2, 0, 0)
    state_1.update_internal_state_after_backprop('127.0.0.1:5000')
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == False)
    # (2, 1, 0)
    state_1._update_device_epoch('127.0.0.1:5001', 1)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == False)
    calc.check(state_1.min_epoch_num == 0)
    # (2, 1, 1)
    state_1._update_device_epoch('127.0.0.1:5002', 1)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == True)
    calc.check(state_1.min_epoch_num == 1)
    # (2, 1, 2)
    state_1._update_device_epoch('127.0.0.1:5002', 2)
    calc.check(state_1.check_fairness_before_backprop('127.0.0.1:5000') == True)
    calc.check(state_1.min_epoch_num == 1)
    # (2, 2, 2)
    state_1._update_device_epoch('127.0.0.1:5001', 2)
    calc.check(state_1.min_epoch_num == 2)

def test_flatten_metadata(calc):
    state_1_d = {
        '127.0.0.1:5000': 0,
        '127.0.0.1:5001': 0,
        '127.0.0.1:5002': 0
    }
    # (0, 0, 0)
    state_1 = DeviceFairnessReceiverState(2, state_1_d)
    flattened = state_1.flatten_metadata([
    {
        '127.0.0.1:5000': 1,
        '127.0.0.1:5001': 3,
        '127.0.0.1:5002': 4,
    },
    {
        '127.0.0.1:5004': 1,
        '127.0.0.1:5002': 3,
    },
        {
        '127.0.0.1:5000': 3,
    },
    ], ['127.0.0.1:5000', '127.0.0.1:5001', '127.0.0.1:5002', '127.0.0.1:5004'])
    calc.check(flattened == [[1, 3, 4, 0], [0, 0, 3, 1], [3, 0, 0, 0]])



def add_tests(calc):
    calc.add_test(test_flatten_metadata)
    # calc.add_test(test_determine_fairness_given_internal_state)
    # calc.add_test(test_update_internal_state_after_backprop)
    # calc.add_test(test_update_internal_state_after_aggregation)