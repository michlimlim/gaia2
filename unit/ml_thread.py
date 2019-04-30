
from unit.unit import TestCalculator
from src.ml_thread import initialize_current_node
from src.pendingwork import PendingWork

def test_ml_thread(calc):
    calc.context("test_ml_thread")
    pending_work_queues = PendingWork()
    pending_work_queues.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    # TODO (Weitai): to change the device id to be the raw addresses of the flask apps
    node = initialize_current_node(0, pending_work_queues, 'MNIST', './data')
    node.train_and_enqueue_local_gradients()
    node.evaluate()
    calc.check(True)

def add_tests(calc):
    calc.add_test(test_ml_thread)