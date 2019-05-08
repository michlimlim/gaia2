
from unit.unit import TestCalculator
from src.sender import Sender

sender = Sender(20)

class HTTPResponse(object):
    def __init__(self, code):
        self.status_code = code

def test_sender(calc):
    calc.context("sender")
    sender.setup("localhost:5000", ["localhost:5001","localhost:5002"], ["localhost:5003"])
    
    # Testing if enqueue adds items to intracluster hosts
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 2)
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 4)
    # sender.run()

    # Testing if dequeue removes every queue
    sender.dequeue_every_queue()
    calc.check(sender.total_no_of_updates == 0)
        
    # Testing if one can insert a clear signal
    # sender.enqueue({"CLEAR" : True, "epoch": 6})
    # calc.check(sender.total_no_of_updates == 2)
    # sender.run()

    # Send to other leaders only
    sender.enqueue("update", True)
    calc.check(sender.total_no_of_updates == 1)

    # Check if sender sends out the update in other_leaders
    # sender.run()
    # print(sender)

    
def add_tests(calc):
    calc.add_test(test_sender)