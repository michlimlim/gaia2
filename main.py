from flask import Flask, request
from src.pendingwork import PendingWork                                                      
import threading
import sys
import requests

app = Flask(__name__)

pending_work_queues = PendingWork(100)

def main():
  # Some kind of loop that will call Aggregator periodicially
  return "App is running"

@app.route("/")
def hello():
  return "App is running"

@app.route("/send_update", methods=['GET', 'POST'])
def receive_update():
  content = request.json
  sender = content['sender']
  update = content['update']
  pending_work_queues.enqueue(update, sender)
  # print(pending_work_queues)
  return "Send update is running"

if __name__ == "__main__":
  # Intialize my_host and other_hosts from command line
  other_hosts = []
  if len(sys.argv) < 4 or sys.argv[1] != "-me" or sys.argv[3] != "-them": 
    print("Usage: main.py -me <my host address> -them <other_host_1> <other_host_2> ...")
    exit(1)
  my_host = sys.argv[2]
  for i in range(4, len(sys.argv)):
    other_hosts.append(sys.argv[i])
  
  # Set up global queues with the hosts
  pending_work_queues.setup(my_host, other_hosts)

  main()
  port = my_host.split(":")[1]
  threading.Thread(target=app.run, kwargs=dict(host="localhost", port=port)).start()