
from unit.unit import TestCalculator
from src.ml_thread import initialize_current_node
from src.receiver import Receiver

def test_ml_thread(calc):
    calc.context("test_ml_thread")
    receiver_1 = Receiver(5)
    receiver_2 = Receiver(5)
    receiver_3 = Receiver(5)
    receiver_1.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    receiver_2.setup("localhost:5001", ["localhost:5000","localhost:5002"])
    receiver_3.setup("localhost:5002", ["localhost:5000","localhost:5001"])
    node_1 = initialize_current_node(receiver_1, 'MNIST', './data')
    node_2 = initialize_current_node(receiver_2, 'MNIST', './data')
    node_3 = initialize_current_node(receiver_3, 'MNIST', './data')
    
    node_1.train()
    node_1.evaluate()
    node_2.train()
    node_2.evaluate()
    node_3.train()
    node_3.evaluate()
    calc.check(True)

def add_tests(calc):
    calc.add_test(test_ml_thread)
