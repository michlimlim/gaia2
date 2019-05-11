
from unit.unit import TestCalculator
from src.data_partition import partition_dict


def test_partition_dict(calc):
    calc.context("test_partition_dict")
    three_dicts =  partition_dict(3)
    calc.check(three_dicts == [{0: 5400, 1: 5400, 2: 5400}, {3: 5400, 4: 5400, 5: 5400}, {6: 5400, 7: 5400, 8: 5400, 9: 5400}])
    ten_dicts = partition_dict(10)
    calc.check(ten_dicts == [{0: 5400}, {1: 5400}, {2: 5400}, {3: 5400}, {4: 5400}, {5: 5400}, {6: 5400}, {7: 5400}, {8: 5400}, {9: 5400}])



def add_tests(calc):
    calc.add_test(test_partition_dict)