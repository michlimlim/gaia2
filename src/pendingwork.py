#!/usr/bin/python3
from threading import RLock
from src.updatequeue import UpdateQueue
import random
from src.util import DevicePushbackError
from src.util import EmptyQueueError
from src.util import ExtraFatal

class PendingWork(object):
    # PendingWork holds all the queues of model
    # updates to be processed. This is implemented
    # for one tenant only, and it does not include
    # a global model queue. This class is thread safe.
    # TODO(ml): Add a global model queue.

    def __init__(self, max_qlen_ratio):
        # :brief Create a new PendingWork instance.
        self.queues = {}
        self.lock = RLock()
        self.my_host = ''
        self.other_hosts = []
        self.num_devices = 0
        self.total_no_of_updates = 0
        self.min_queue_len = None
        self.k = max_qlen_ratio

    def setup(self, my_host, other_hosts):
        # :brief Set up a queue for each host.
        # :param my_host [str] an id for this server
        # :param other_hosts [array<str>] the id of the other hosts
        self.my_host = my_host
        self.other_hosts = other_hosts
        self.num_devices = 1 + len(other_hosts)
        self.lock.acquire(blocking=1)
        self.queues[my_host] = UpdateQueue()
        for host in other_hosts:
            self.queues[host] = UpdateQueue()
        self.release()

    def enqueue(self, update, host):
        # :brief Add an update to corresponding queue of a given host.
        # :param update [Object] a model update that needs to be processed
        # :param host [str] the id for the host that generated the update
        # TODO(wt): Decide on a representation for model updates and
        # replace the 'Object' typing above.
        self.write()
        if not host in self.queues:
            # Creates queue if none exists
            # Will never push back for creating new queue
            self.queues[host] = UpdateQueue()
            self.queues[host].enqueue(update)
            self.total_no_of_updates += 1
            self._update_min_and_max()
            self.release()
            return
        queue = self.queues[host]
        if self.min_queue_len != None:
            if len(queue) > self.k * self.min_queue_len:
                self.release()
                raise DevicePushbackError("could not enqueue new update")
        queue.enqueue(update)
        self.total_no_of_updates += 1
        self._update_min_and_max()
        self.release()

    def dequeue(self):
        # :brief Pop an update from one of the queues at random.
        # The algorithm picks out an element, by dequeueing from a random queue.
        # The queue is chosen with probability proportional to its length.
        # :return [Object] a dequeued update
        # :warning Raises an EmptyQueueError when no element could be returned.
        # TODO(wt): Ditto for this method.
        self.write()
        if self.total_no_of_updates == 0:
            self.release()
            raise EmptyQueueError("")
        ret = None
        r = random.randint(0, max(self.total_no_of_updates - 1, 0))
        for key in self.queues:
            queue = self.queues[key]
            if queue.len > r:
                ret = queue.dequeue()
                break
            else:
                r -= queue.len
        if ret == None:
            # This should not happen
            self.release()
            raise ExtraFatal("could not pop from any queue")
        self.total_no_of_updates -= 1
        self._update_min_and_max()
        self.release()
        return ret

    def _update_min_and_max(self):
        # :brief Recalculate min and max queue lengths.
        # Requires that self already be locked.
        # Should not be called from outside this class (a private method).
        # TODO(gs): There is a faster way to do this since this method scales with O(n)
        # where n is the number of queues. It would essentially be to keep a histogram of counts
        # in a vector. The worst case would be the same, but average performance *should* improve.
        # However, I think that may be harder to maintain so I will leave this here until
        # scale becomes a problem.
        lo = None
        for queue in self.queues:
            if lo == None:
                lo = len(queue)
            if len(queue) < lo and lo != 1:
                lo = len(queue)
        self.min_queue_len = lo

    # Call `read` before reading, and `release` after reading.
    # Call `write` before writing, and `release` after writing.

    def read(self):
        # :brief Read lock self.
        self.lock.acquire(blocking=0)

    def write(self):
        # :brief Write lock self.
        self.lock.acquire(blocking=1)

    def release(self):
        # :brief Release any locks.
        self.lock.release()

    def __str__(self):
        # :brief Print out elements in all queues, for debugging purposes.
        # :return [str] the PendingWork queues as a string
        self.read()
        re = "\nPendingWork:\n"
        for qid in self.queues:
            re = re + qid + ":" + str(self.queues[qid].queue) + "\n"
        self.release()
        return re
    
    def get_total_no_of_updates(self):
        # :brief Get self's total_no_of_updates
        # :return [int] the value of total_no_of_updates
        return self.total_no_of_updates
