from flask import Flask                                                         
import threading

data = 'foo'
app = Flask(__name__)

def main():
  print("hello")

@app.route("/")
def hello():
    return data

if __name__ == "__main__":
    main()
    threading.Thread(target=app.run).start()