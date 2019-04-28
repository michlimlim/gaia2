from flask import Flask   
from pendingwork import PendingWork                                                      
import threading

app = Flask(__name__)

pending_work_queues = PendingWork()
pending_work_queues.setup("localhost:5000", ["localhost:5001","localhost:5002"])

def main():
  # Example of main thread accessing PendingWork
  print("queues created", pending_work_queues.ret_queues())

@app.route("/")
def hello():
  # Example of flask app thread accessing PendingWork
  print("queues created", pending_work_queues.ret_queues())
  return ''

if __name__ == "__main__":
    main()
    threading.Thread(target=app.run).start()
