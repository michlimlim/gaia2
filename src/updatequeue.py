#!/usr/bin/python3
from src.util import EmptyQueueError


class UpdateQueue(object):
    # UpdateQueue encapsulates a queue of model updates.
    # This class is not thread safe.

    def __init__(self):
        # :brief Create a new UpdateQueue instance.
        self.queue = []
        self.len = 0

    def enqueue(self, data):
        # :brief Enqueue some data.
        # :param data [Object] some object to add to the queue
        self.queue.append(data)
        self.len += 1

    def dequeue(self):
        # :brief Dequeue an element of the queue.
        # :return [Object] the oldest element of the queue.
        # :warning raises an EmptyQueueError if the queue is empty
        if self.len < 1:
            raise EmptyQueueError("could not pop from empty queue")
        ret = self.queue[-1:]
        self.queue = self.queue[1:]
        self.len -= 1
        return ret
    
    def clear(self):
        del self.queue[:]

    def peek(self):
        # :brief Get the next element in the queue without dequeing it.
        # :return [Object] the oldest element of the queue 
        # :warning raises an EmptyQueueError if the queue is empty
        if self.len < 1:
            raise EmptyQueueError("could not peek on empty queue")
        ret = self.queue[-1:]
        self.queue = self.queue[1:]
        return ret

    def __len__(self):
        # :brief Get the length of the queue.
        # :return [int] the length of the queue
        return self.len