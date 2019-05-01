from threading import RLock
import time
from src.util import EmptyQueueError, DevicePushbackError
from src.updatequeue import UpdateQueue
import requests
from threading import Thread

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
        self.host_locks = {}
        self.queues = {}
        self.total_no_of_updates = 0 
        self.min_queue_len = None
        self.k = k

    def setup(self, my_host, other_hosts):
        # :brief Set up a queue for each host.
        # :param my_host [str] an id for this server
        # :param other_hosts [array<str>] the id of the other hosts
        self.my_host = my_host
        self.other_hosts = other_hosts
        self.num_devices = 1 + len(other_hosts)
        self.write()
        self.queues[my_host] = UpdateQueue()
        self.wait_times[my_host] = .1
        self.last_sent_times[my_host] = 0
        self.host_locks[my_host] = RLock()
        for host in other_hosts:
            self.queues[host] = UpdateQueue()
            self.wait_times[host] = .1
            self.last_sent_times[host] = 0
            self.host_locks[host] = RLock()
        self.release()

    def enqueue(self, update):
        # :brief Add an update to corresponding queue of a given host.
        # :param update [Object] a model update that needs to be processed
        # :param host [str] the id for the host that generated the update
        all_hosts = self.other_hosts + [self.my_host]
        for host in self.queues:
            self.write_host(host)
            queue = self.queues[host]
            if self.min_queue_len != None:
                if len(queue) > self.k * self.min_queue_len:
                    self.release_host(host)
                    raise DevicePushbackError("could not enqueue new update")
            queue.enqueue(update)
            self.total_no_of_updates += 1
            self._update_min_and_max()
            self.release_host(host)
    
    def run(self):
        # :brief Spawn a new thread and begin sending update requests to other devices
        t = Thread(target=self._actually_run)
        t.start()

    def _actually_run(self):
        # :brief Send updates to peers when possible.
        all_hosts = self.other_hosts + [self.my_host]
        while True:
            for host in all_hosts:
                self._update_host(host)
    
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
            update = queue.peek()
        except EmptyQueueError:
            self.release_host(host)
            return
        res = requests.post(host+"/send_update", json={"sender": host, "update": update})
        if res.status_code >= 400 and res.status_code < 500:
            self.wait_times[host] *= 2
            self.release_host(host)
            return
        self.last_sent_times[host] = time.time()
        self.wait_times[host] = max(0.1, self.wait_times[host] - .1)
        self.release_host(host)
        self.write_host(host)
        queue.dequeue()
        self.total_no_of_updates -= 1
        self._update_min_and_max()
        self.release_host(host)

    # Call `read` before reading, and `release` after reading.
    # Call `write` before writing, and `release` after writing.

    def read_host(self, host):
        # :brief Read lock a host queue
        self.host_locks[host].acquire(blocking=0)

    def write_host(self, host):
        # :brief Write lock a host queue.
        self.host_locks[host].acquire(blocking=1)

    def release_host(self, host):
        # :breif Release a lock on the host queue.
        self.host_locks[host].release()

    def read(self):
        # :brief Read lock on self.
        self.lock.acquire(blocking=o)

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