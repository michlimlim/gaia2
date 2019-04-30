#!/usr/bin/python3
from threading import RLock
from updatequeue import UpdateQueue
import random
import util

# TODO(gs): Implement a better test suite.

# TODO(gs): This should be set in the initializer
# instead of a global constant.
MAX_QUEUE_LEN_RATIO = 10


class PendingWork(object):
    # PendingWork holds all the queues of model
    # updates to be processed. This is implemented
    # for one tenant only, and it does not include
    # a global model queue.
    # TODO(ml): Add a global model queue.

    def __init__(self):
        # :brief Create a new PendingWork instance.
        self.queues = {}
        self.lock = RLock()
        self.my_host = ''
        self.other_hosts = []
        self.num_devices = 0
        self.total_no_of_updates = 0
        self.min_queue_len = None
        self.k = MAX_QUEUE_LEN_RATIO

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
                raise util.DevicePushbackError("could not enqueue new update")
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
        ret = None
        r = random.randint(0, self.total_no_of_updates)
        for key in self.queues:
            queue = self.queues[key]
            if queue.len > r:
                ret = queue.dequeue()
                break
            else:
                r -= queue.len
        if ret == None:
            raise util.EmptyQueueError("could not pop from any queue")
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

    def ret_queues(self):
        """Print out elements in all queues, for debugging purposes.
           TODO(gs): Consider replacing with a __str__ method."""
        re = []
        for queue in self.queues:
            re.append(queue + ":" + str(self.queues[queue].queue))
        return re


def main():
    pending_work_queues = PendingWork()

    # Testing if setup successfully creates queues
    pending_work_queues.setup(
        "localhost:5000", ["localhost:5001", "localhost:5002"])
    print("queues created", pending_work_queues.ret_queues())

    # Testing if enqueue adds items to correct queues
    pending_work_queues.enqueue("5001 update", "localhost:5001")
    pending_work_queues.enqueue("5001 update 2", "localhost:5001")
    pending_work_queues.enqueue("5000 update", "localhost:5000")
    print("queues after 3 things are added", pending_work_queues.ret_queues())

    # Testing if dequeue works
    pending_work_queues.dequeue()
    print("queues after 1 item removed", pending_work_queues.ret_queues())
    pending_work_queues.dequeue()
    pending_work_queues.dequeue()
    print("queues after another 2 items removed",
          pending_work_queues.ret_queues())

    # Testing if dequeue works when queue empty
    try:
        item = pending_work_queues.dequeue()
        print("ERROR: should have raised exception")
    except util.EmptyQueueError:
        print("correctly raised exception")


if __name__ == "__main__":
    main()
