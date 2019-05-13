from threading import RLock, Event, Condition, Thread
import time
import requests
import json

from src.util import EmptyQueueError, DevicePushbackError
from src.updatequeue import UpdateQueue

class Sender(object):
    def __init__(self, k):
        # :brief Create a new Sender instance.
        self.lock = RLock()
        self.my_host = None
        self.other_hosts = None
        self.other_leaders = None
        self.wait_times = {}
        self.last_sent_times = {}
        self.num_devices = -1
        self.last_sent_times = {}
        self.wait_times = {}
        self.host_locks = {}
        # Includes both the queues for other_hosts and other_leaders
        self.queues = {}
        self.total_no_of_updates = 0 
        self.min_queue_len = None
        self.k = k
        self.condition = Condition()

    def setup(self, my_host, other_hosts, other_leaders):
        # :brief Set up a queue for each host.
        # :param my_host [str] an id for this server
        # :param other_hosts [array<str>] the id of the other hosts
        self.my_host = my_host
        self.other_hosts = other_hosts
        self.other_leaders = other_leaders
        self.num_devices = 1 + len(other_hosts) + len(other_leaders)
        self.write()
        self.wait_times[my_host] = .1
        self.last_sent_times[my_host] = 0
        self.host_locks[my_host] = RLock()
        for host in other_hosts + other_leaders:
            self.queues[host] = UpdateQueue()
            self.wait_times[host] = .1
            self.last_sent_times[host] = 0
            self.host_locks[host] = RLock()
        self.release()
    
    def dequeue_every_queue(self):
        # :brief Clear every host's queue
        # :return nothing
        self.write()
        for queue in self.queues:
            self.total_no_of_updates -= len(self.queues[queue])
            self.queues[queue].clear()
        self.release()
        return

    def enqueue(self, update, other_leaders = False):
        # :brief Add an update to hosts in same cluster if False.
        # Add the update to other_leaders if flag is set as True.
        # :param update [Object] a model update that needs to be processed
        # :param host [str] the id for the host that generated the update
        queues = self.other_leaders if other_leaders else self.other_hosts 
        
        for host in queues:
           #  print("SEND TO", host)
            self.write_host(host)
            queue = self.queues[host]
            if self.min_queue_len != None:
                if queue.len > self.k * self.min_queue_len:
                    self.release_host(host)
                    raise DevicePushbackError("could not enqueue new update")
            queue.enqueue(update)
            self.total_no_of_updates += 1
            self._update_min_and_max()
            self.release_host(host)
        # Enqueuing notifies the sender thread
        with self.condition:
            self.condition.notify()
            # print("ML THREAD WOKE UP SENDER THREAD")
    
    def run(self):
        # :brief Spawn a new thread and begin sending update requests to other devices
        t = Thread(target=self._actually_run)
        t.start()

    def _actually_run(self):
        # :brief Send updates to peers when possible.
        while True:
            if self.total_no_of_updates > 0:
                for host in self.queues:
                    self._update_host(host)
            else:
                with self.condition:
                    # print("SENDER THREAD SLEEPING")
                    self.condition.wait()
                # print("SENDER THREAD WOKE UP FROM ML THREAD")
    
    # TODO (GS): To update min_queue_len after each enqueue and dequeue
    def _update_min_and_max(self):
        pass

    def _update_host(self, host):
        # :brief Try to update peer if possible.
        # If the update succeeds, then the update will be
        # popped from that hosts queue.
        if time.time() < self.last_sent_times[host] + self.wait_times[host]:
            return
        self.read_host(host)
        queue = self.queues[host]
        update = None
        try:
            update = queue.dequeue()
            self.total_no_of_updates -= 1
        except EmptyQueueError:
            self.release_host(host)
            return
        if 'CLEAR' in update:
            res = requests.post("http://" + host + "/clear_all_queues", json={"sender": self.my_host, "epoch": update['epoch']})
        elif 'CLOSE' in update:
                        res = requests.post("http://" + host + "/close", json={"sender": self.my_host})
        else:
            res = requests.post("http://" + host + "/send_update", json={"sender": self.my_host, "update": update})
        if res.status_code >= 400 and res.status_code < 500:
            self.wait_times[host] *= 2
            self.release_host(host)
            return
        self.last_sent_times[host] = time.time()
        self.wait_times[host] = max(0.1, self.wait_times[host] - .1)
        self._update_min_and_max()
        self.release_host(host)     
    # Call `read` before reading, and `release` after reading.
    # Call `write` before writing, and `release` after writing.

    def read_host(self, host):
        # :brief Read lock a host queue
        # print("READ HOST FOR HOST:", host)
        self.host_locks[host].acquire(blocking=0)

    def write_host(self, host):
        # :brief Write lock a host queue.
        self.host_locks[host].acquire(blocking=1)

    def release_host(self, host):
        # :breif Release a lock on the host queue.
        # print("RELEASE HOST FOR HOST", host)
        self.host_locks[host].release()

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
