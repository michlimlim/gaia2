#!/usr/bin/python3
import util


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
        # :return [Object] some the oldest element of the queue.
        # :warning Raises an EmptyQueueError of the queue is empty.
        if self.len < 1:
            raise util.EmptyQueueError("could not pop from empty queue")
        ret = self.queue[-1]
        self.queue = self.queue[1:]
        self.len -= 1
        return ret

    def __len__(self):
        # :brief Get the length of the queue.
        # :return [int] the length of the queue
        return self.len


def main():
    sample_queue = UpdateQueue()

    # Testing if enqueue adds items to list and increments length
    sample_queue.enqueue("giraffe")
    sample_queue.enqueue("elephant")
    print("queue", sample_queue.queue)
    print("length", sample_queue.len)

    # Testing if dequeue removes items to list and decrements length
    sample_queue.dequeue()
    print("queue", sample_queue.queue)
    print("length", sample_queue.len)

    # Testing if dequeue works when queue empty
    sample_queue.dequeue()
    sample_queue.dequeue()
    sample_queue.dequeue()
    print("queue", sample_queue.queue)
    print("length", sample_queue.len)


if __name__ == "__main__":
    main()
