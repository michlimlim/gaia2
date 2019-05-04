from unit.unit import TestCalculator
from src.util import EmptyQueueError
from src.receiver import Receiver
from src.updatequeue import UpdateQueue

def test_update_queue(calc):
    calc.context("test_update_queue")
    queue = UpdateQueue()
    calc.check(len(queue) == 0)

    # Testing if enqueue adds items to list and increments length
    queue.enqueue("giraffe")
    calc.check(len(queue) == 1)
    queue.enqueue("elephant")
    calc.check(len(queue) == 2)
    print("queue", queue.queue)
    print("length", queue.len)

    # Testing if dequeue removes items to list and decrements length
    queue.dequeue()
    calc.check(len(queue) == 1)
    print("queue", queue.queue)
    print("length", queue.len)

    # Testing if dequeue works when queue empty
    queue.dequeue()
    calc.check(len(queue) == 0)
    try:
        queue.dequeue()
        calc.check(False)
    except EmptyQueueError:
        calc.check(True)
    calc.check(len(queue) == 0)
    try:
        queue.dequeue()
        calc.check(False)
    except:
        calc.check(True)
    calc.check(len(queue) == 0)
    print("queue", queue.queue)
    print("length", queue.len)

def add_tests(calc):
    calc.add_test(test_update_queue)
