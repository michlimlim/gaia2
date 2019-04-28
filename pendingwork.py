
from threading import RLock
from queue import Queue
import random

class PendingWork(object):

    """
    PendingWork class. 
    
    It holds all the queues of models updates to be processed. 
    For one tenant only. For now, it does not include global model queue.
    """

    def __init__(self):
        self.queues = {}
        self.lock = RLock()
        self.my_host = ''
        self.other_hosts = []
        self.total_no_of_updates = 0

    def setup(self, my_host, other_hosts):
        """Sets up a queue for each host"""
        self.my_host = my_host
        self.other_hosts = other_hosts
        self.lock.acquire(blocking=1)
        self.queues[my_host] = Queue()
        for host in other_hosts:
            self.queues[host] = Queue()
        self.release()

    def enqueue(self, update, host):
        """Adds update to corresponding queue of host"""
        # Creates queue if none exists
        self.read()
        if not host in self.queues:
            self.release()
            self.write()
            self.queues[host] = Queue()
        self.release()
        # Adds update to the host's queue
        host_queue = self.queues[host]
        self.write()
        host_queue.enqueue(update)
        self.total_no_of_updates += 1
        self.release()

    def dequeue(self):
        """Pops update from one of the queues at random
           The algorithm picks out a random element, and dequeues the queue it is found in.
           Effectively, it picks a queue proportional to its size. """
        ret = None
        self.write()
        r = random.randint(0, self.total_no_of_updates)
        for key in self.queues:
            queue = self.queues[key]
            if queue.len > r:
                ret = queue.dequeue()
                break
            else:
                r -= queue.len 
        self.total_no_of_updates -= 1
        self.release()
        return ret

    """Call `read` before reading, and `release` after reading.
       Call `write` before writing, and `release` after writing."""

    def read(self):
        self.lock.acquire(blocking=0)

    def write(self):
        self.lock.acquire(blocking=1)

    def release(self):
        self.lock.release()
    
    def print_queues(self):
        """Print out elements in all queues. For debugging purposes."""
        re = []
        for queue in self.queues:
            re.append(queue + ":" + str(self.queues[queue].queue))
        return re

def main(): 
    pending_work_queues = PendingWork()

    # Testing if setup successfully creates queues
    pending_work_queues.setup("localhost:5000", ["localhost:5001","localhost:5002"])
    print("queues created", pending_work_queues.print_queues())

    # Testing if enqueue adds items to correct queues
    pending_work_queues.enqueue("5001 update", "localhost:5001")
    pending_work_queues.enqueue("5001 update 2", "localhost:5001")
    pending_work_queues.enqueue("5000 update", "localhost:5000")
    print("queues after 3 things are added", pending_work_queues.print_queues())
    
    # Testing if dequeue works
    pending_work_queues.dequeue()
    print("queues after 1 item removed", pending_work_queues.print_queues())
    pending_work_queues.dequeue()
    pending_work_queues.dequeue()
    print("queues after another 2 items removed", pending_work_queues.print_queues())


    # Testing if dequeue works when queue empty
    item = pending_work_queues.dequeue()
    print("queue after dequeue on empty", pending_work_queues.print_queues())

if __name__ == "__main__":
    main()