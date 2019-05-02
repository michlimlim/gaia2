
from unit.unit import TestCalculator
from src.sender import Sender
from mock import patch

sender = Sender(20)

class HTTPResponse(object):
    def __init__(self, code):
        self.status_code = code

@patch.object(sender, 'send_update_to_host')
def test_sender(calc, mock_fn):
    mock_fn.return_value = HTTPResponse(200)
    calc.context("sender")
    sender.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    
    # Testing if enqueue adds items to correct queues
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 3)
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 6)

    # Testing if the sender thread spawned sends all updates out
    # sender.run()
    # calc.check(mock_fn.call_count == 3)
    
def add_tests(calc):
    calc.add_test(test_sender)