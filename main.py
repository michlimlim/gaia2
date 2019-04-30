from flask import Flask   
from src.pendingwork import PendingWork                                                      
import threading

app = Flask(__name__)

pending_work_queues = PendingWork(100)
pending_work_queues.setup("localhost:5000", ["localhost:5001","localhost:5002"])

def main():
  # Some kind of loop that will call Aggregator periodicially
  print("app is running")
  

@app.route("/")
def hello():
  # Example of flask app thread accessing PendingWork
  print("queues created", pending_work_queues.ret_queues())
  return ''

if __name__ == "__main__":
    main()
    threading.Thread(target=app.run).start()
