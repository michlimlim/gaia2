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
    # update is a [json_str]
    # print(sender)
    # print(json.loads(update[0])['updates'])
    pending_work_queues.enqueue(ModelUpdate(**json.loads(update)), sender)
    # print(pending_work_queues)
    return "Send update is running"

if __name__ == "__main__":
    # Intialize my_host and other_hosts from command line
    # Example:
    # Open a terminal for each of the following commands and run them!
    # python main.py -me localhost:5000 -them localhost:5001 localhost:5002
    # python main.py -me localhost:5001 -them localhost:5000 localhost:5002
    # python main.py -me localhost:5002 -them localhost:5000 localhost:5001
    other_hosts = []
    if len(sys.argv) < 4 or sys.argv[1] != "-me" or sys.argv[3] != "-them": 
        print("Usage: main.py -me <my host address> -them <other_host_1> <other_host_2> ...")
        exit(1)
    my_host = sys.argv[2]
    for i in range(4, len(sys.argv)):
        other_hosts.append(sys.argv[i])

    # Set up global queues with the hosts
    pending_work_queues.setup(my_host, other_hosts)
    node = initialize_current_node(pending_work_queues, 'MNIST', './data')
    pending_work_queues.setup_connection_to_node(node)

    port = my_host.split(":")[1]
    ml_thread = MlThread(node)
    threading.Thread(target=app.run, kwargs=dict(host="localhost", port=port)).start()
    ml_thread.run()


