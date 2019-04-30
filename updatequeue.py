#!/usr/bin/python3
# TODO(gs): Document this class.
import util


class UpdateQueue(object):
    # :warning Not thread safe.
    def __init__(self):
        self.queue = []
        self.len = 0

    def enqueue(self, data):
        self.queue.append(data)
        self.len += 1

    def dequeue(self):
        if self.len < 1:
            raise util.EmptyQueueError("could not pop from empty queue")
        ret = self.queue[-1]
        self.queue = self.queue[1:]
        self.len -= 1
        return ret

    def __len__(self):
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
