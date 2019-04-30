#!/usr/bin/python3
from unit.unit import TestCalculator

## :brief Check that 2 + 2 is 4.
# :param calc [pyunit.TestCalculator] the TestCalculator instance performing
# the computation
# :return None
def check_2_plus_2(calc):
  calc.context("2+2 test")
  calc.check("2 + 2 == 4")
  return None

## :brief Check that 2 != 3.
# :param calc [pyunit.TestCalculator] the TestCalculator instance performing
# the computation
# :return None
def check_2_neq_3(calc):
  calc.context("2 != 3 test")
  calc.check(2 != 3)
  calc.check_not(2 == 3)
  return None

def add_tests(calc):
  calc.add_test(check_2_plus_2)
  calc.add_test(check_2_neq_3)

def main():
  calc = TestCalculator()
  add_tests(calc)
  calc.run()

if __name__ == "__main__":
  main()
