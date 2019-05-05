from unit.unit import TestCalculator
from src.receiver import Receiver
from src.util import EmptyQueueError

def test_receiver(calc):
    calc.context("test_receiver")
    receiver = Receiver(100)

    # Testing if setup successfully creates queues
    receiver.setup(
        "localhost:5000", ["localhost:5001", "localhost:5002"])
    check = receiver.get_total_no_of_updates() == 0
    if not check:
        print("queues created", receiver)
        calc.check(False)
        return

    # Testing if enqueue adds items to correct queues
    receiver.enqueue("5001 update", "localhost:5001")
    calc.check(receiver.get_total_no_of_updates() == 1)
    receiver.enqueue("5001 update 2", "localhost:5001")
    calc.check(receiver.get_total_no_of_updates() == 2)
    receiver.enqueue("5000 update", "localhost:5000")
    check = receiver.get_total_no_of_updates() == 3
    if not check:
        calc.check(False)
        print("queues after 3 things are added", receiver)
        return

    # Testing if dequeue works
    receiver.dequeue()
    check = receiver.get_total_no_of_updates() == 2
    if not check:
        calc.check(False)
        print("queues after 1 item removed", receiver)
        return
    receiver.dequeue()
    check = receiver.get_total_no_of_updates() == 1
    if not check:
        calc.check(False)
        print("queues after 1 item removed", receiver)
        return
    receiver.dequeue()
    check = receiver.get_total_no_of_updates() == 0
    if not check:
        calc.check(False)
        print("queues after another 2 items removed",
            receiver)
        return

    # Testing if dequeue works when queue empty
    try:
        item = receiver.dequeue()
        calc.check(False)
    except EmptyQueueError:
        calc.check(True)

def add_tests(calc):
    calc.add_test(test_receiver)
