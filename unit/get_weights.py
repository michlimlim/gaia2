from src.get_weights import get_weights

def check(az):
    s = 0.0
    for  a in az:
        s += a
    if s < .99 or s > 1.01:
        return False
    return True

def test_get_weights(calc):
    calc.context("test_get_weights")
    vs = [[1, 3], [4, 5]]
    az = get_weights(vs)
    calc.check(az)
    vs = [[1, 2, 3, 10], [1.1, 23, 4, 1], [55, 1, 2, 1000]]
    az = get_weights(vs)
    calc.check(az)

def add_tests(calc):
    calc.add_test(test_get_weights)
