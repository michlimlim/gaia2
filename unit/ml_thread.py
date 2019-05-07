
from unit.unit import TestCalculator
from src.ml_thread import initialize_current_node
from src.pendingwork import PendingWork

def test_ml_thread(calc):
    calc.context("test_ml_thread")
    pending_work_queues_1 = PendingWork(5)
    pending_work_queues_2 = PendingWork(5)
    pending_work_queues_3 = PendingWork(5)
    pending_work_queues_1.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    pending_work_queues_2.setup("localhost:5001", ["localhost:5000","localhost:5002"])
    pending_work_queues_3.setup("localhost:5002", ["localhost:5000","localhost:5001"])
    node_1 = initialize_current_node(pending_work_queues_1, 'MNIST', './data')
    node_2 = initialize_current_node(pending_work_queues_2, 'MNIST', './data')
    node_3 = initialize_current_node(pending_work_queues_3, 'MNIST', './data')

    node_1.train()
    node_1.evaluate()
    node_2.train()
    node_2.evaluate()
    node_3.train()
    node_3.evaluate()
    calc.check(True)

def add_tests(calc):
    calc.add_test(test_ml_thread)