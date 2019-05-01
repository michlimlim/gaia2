#!/usr/bin/python3
from unit.unit import TestCalculator
import unit.test_unit as test_unit
import unit.ml_thread as ml_thread
import unit.pendingwork as pendingwork
import unit.updatequeue as updatequeue

def main():
    calc = TestCalculator()
    #test_unit.add_tests(calc)
    ml_thread.add_tests(calc)
    #pendingwork.add_tests(calc)
    #updatequeue.add_tests(calc)
    calc.run()

if __name__ == "__main__":
    main()