from threading import RLock, Event, Condition, Thread
import time
import requests

from src.util import EmptyQueueError, DevicePushbackError
from src.updatequeue import UpdateQueue

class Sender(object):
    def __init__(self, k):
        # :brief Create a new Sender instance.
        self.lock = RLock()
        self.my_host = None
        self.other_hosts = None
        self.wait_times = {}
        self.last_sent_times = {}
        self.num_devices = -1
        self.last_sent_times = {}
        self.wait_times = {}
        self.queues = {}
        self.total_no_of_updates = 0 
        self.min_queue_len = 1
        self.k = k
        self.condition = Condition()

    def setup(self, my_host, other_hosts):
        # :brief Set up a queue for each host.
        # :param my_host [str] an id for this server
        # :param other_hosts [array<str>] the id of the other hosts
        self.my_host = my_host
        self.other_hosts = other_hosts
        self.num_devices = 1 + len(other_hosts)
        self.write()
        # self.queues[my_host] = UpdateQueue()
        self.wait_times[my_host] = .1
        self.last_sent_times[my_host] = 0
        for host in other_hosts:
            self.queues[host] = UpdateQueue()
            self.wait_times[host] = .1
            self.last_sent_times[host] = 0
        self.release()

    def enqueue(self, update):
        # :brief Add an update to corresponding queue of a given host.
        # :param update [Object] a model update that needs to be processed
        # :param host [str] the id for the host that generated the update
        for host in self.queues:
            print("SEND TO", host)
            self.write()
            queue = self.queues[host]
            if self.min_queue_len != None:
                if len(queue) > self.k * self.min_queue_len:
                    self.release()
                    raise DevicePushbackError("could not enqueue new update")
            queue.enqueue(update)
            self.total_no_of_updates += 1
            self._update_min_and_max()
            self.release()
        # Enqueuing notifies the sender thread
        with self.condition:
            self.condition.notify()
            print("ML THREAD WOKE UP SENDER THREAD")
    
    def run(self):
        # :brief Spawn a new thread and begin sending update requests to other devices
        t = Thread(target=self._actually_run)
        t.start()

    def _actually_run(self):
        # :brief Send updates to peers when possible.
        while True:
            if self.total_no_of_updates > 0:
                for host in self.other_hosts:
                    self._update_host(host)
            else:
                with self.condition:
                    print("SENDER THREAD SLEEPING")
                    self.condition.wait()
                print("SENDER THREAD WOKE UP FROM ML THREAD")
    
    def _update_min(self):
        # :brief Update the minimum queue length
        # :warning requires that the state already be locked.
        for host in self.queues:
            if self.min > max(len(self.queues[host]), 1):
                self.min = max(len(self.queues[host]), 1)

    def _update_host(self, host):
        # :brief Try to update peer if possible.
        # If the update succeeds, then the update will be
        # popped from that hosts queue.
        if time.time() < self.last_sent_times[host] + self.wait_times[host]:
            return
        self.read()
        queue = self.queues[host]
        update = None
        try:
            update = queue.peek()
        except EmptyQueueError:
            self.release()
            return
        res = requests.post("http://" + host + "/send_update", json={"sender": self.my_host, "update": update})
        if res.status_code >= 400 and res.status_code < 500:
            self.wait_times[host] *= 2
            self.release()
            return
        self.last_sent_times[host] = time.time()
        self.wait_times[host] = max(0.1, self.wait_times[host] - .1)
        self.release()
        self.write()
        queue.dequeue()
        self.total_no_of_updates -= 1
        self._update_min()
        self.release()
     
    # Call `read` before reading, and `release` after reading.
    # Call `write` before writing, and `release` after writing.

    def read(self):
        # :brief Read lock on self.
        self.lock.acquire(blocking=0)

    def write(self):
        # :brief Write lock on self.
        self.lock.acquire(blocking=1)

    def release(self):
        # :brief Release lock on self.
        self.lock.release()
    
    def __str__(self):
        # :brief Print out elements in all queues, for debugging purposes.
        # :return [str] the Sender queues as a string
        self.read()
        re = "\nSender:\n"
        for qid in self.queues:
            re = re + qid + ":" + str(self.queues[qid].queue) + "\n"
        self.release()
        return re