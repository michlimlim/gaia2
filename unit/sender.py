
from unit.unit import TestCalculator
from src.sender import Sender

def test_sender(calc):
    calc.context("sender")
    sender = Sender(20)
    sender.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    
    # Testing if enqueue adds items to correct queues
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 3)
    sender.enqueue("update")
    calc.check(sender.total_no_of_updates == 6)

    # Testing if the sender thread spawned sends all updates out
    # TODO (GS): Write a unit test for the post
    # sender.run()

    
def add_tests(calc):
    calc.add_test(test_sender)