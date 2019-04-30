class EmptyQueueError(Exception):
    # EmptyQueueError is raised when a dequeue is run
    # on empty queues.
    pass

class DevicePushbackError(Exception):
    # DevicePushbackError is raised when a device cannot
    # enqueue another update.
    pass