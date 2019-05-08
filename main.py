from flask import Flask, request
from src.pendingwork import PendingWork     
from src.update_metadata.model_update import ModelUpdate
from src.ml_thread import initialize_current_node          
import threading
import json
import sys
import requests

app = Flask(__name__)

pending_work_queues = PendingWork(100)

class MlThread(object):
    # params: node [Solver] instance of Solver object
    def __init__(self, node):
        self.node = node
    def run(self):
        t = threading.Thread(target=self._actually_run)
        t.start()
    def _actually_run(self):
        self.node.train()
        self.node.evaluate()

@app.route("/")
def hello():
    return "App is running"

@app.route("/send_update", methods=['GET', 'POST'])
def receive_update():
    content = request.json
    sender = content['sender']
    update = content['update']
    pending_work_queues.enqueue(ModelUpdate(**json.loads(update)), sender)
    return "Send update is running"

@app.route("/clear_all_queues", methods=['GET', 'POST'])
def clear_all_queues():
    # Leader will call this to freeze all nodes until it sends its own update
    content = request.json
    sender = content['sender']
    epoch = content['epoch']
    if sender != pending_work_queues.leader:
        return "Non-leader tried to clear all queues"
    # Stop all enqueues from non-leader, and clear all queues
    pending_work_queues.clear_all()
    # TODO(wt): Set ML Thread to the new epoch no. Figure out where to set this?
    # pending_work_queues.node.curr_epoch = epoch
    return "Clear_all_queues is running"

if __name__ == "__main__":
    # Intialize my_host and other_hosts from command line
    # Example:
    # Open a terminal for each of the following commands and run them!
    # python main.py -me localhost:5000 -leader localhost:5000 -them localhost:5001 -otherleaders localhost:5002
    # python main.py -me localhost:5001 -leader localhost:5000 -them localhost:5000
    # python main.py -me localhost:5002 -leader localhost:5002 -them localhost:5003 -otherleaders localhost:5000
    # python main.py -me localhost:5003 -leader localhost:5002 -them localhost:5002
    other_hosts = []
    other_leaders = []
    if len(sys.argv) < 4 or sys.argv[1] != "-me" or sys.argv[3] != "-leader" or sys.argv[5] != "-them": 
        print("Usage: main.py -me <my host address> -leader <address_of_leader> -them <neighbor_host_1> <neighbor_host_2> ... (-otherleaders <leader_host_1> <leader_host_2> ....)")
        exit(1)
    my_host = sys.argv[2]
    leader = sys.argv[4]
    try:
        leaders_head = sys.argv.index("-otherleaders")
        for i in range(leaders_head + 1, len(sys.argv)):
            other_leaders.append(sys.argv[i])
    except ValueError:
        leaders_head = len(sys.argv)
    for i in range(6, leaders_head):
        other_hosts.append(sys.argv[i])

    # Set up global queues with the hosts and leader
    pending_work_queues.setup(my_host, other_hosts, leader, other_leaders)
    node = initialize_current_node(pending_work_queues, 'MNIST', './data')
    pending_work_queues.setup_connection_to_node(node)

    port = my_host.split(":")[1]
    ml_thread = MlThread(node)
    threading.Thread(target=app.run, kwargs=dict(host="localhost", port=port)).start()
    ml_thread.run()


