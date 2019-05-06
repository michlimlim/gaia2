
from unit.unit import TestCalculator
from src.sender import Sender

sender = Sender(20)

class HTTPResponse(object):
    def __init__(self, code):
        self.status_code = code

def test_sender(calc):
    calc.context("sender")
    sender.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    
    # Testing if enqueue adds items to correct queues
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 2)
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 4)

    # Testing if dequeue removes every queue
    sender.dequeue_every_queue()
    calc.check(sender.total_no_of_updates == 0)
    
def add_tests(calc):
    calc.add_test(test_sender)