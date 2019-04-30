class EmptyQueueError(Exception):
    # EmptyQueueError is raised when a dequeue is run
    # on empty queues.
    pass

class DevicePushbackError(Exception):
    # DevicePushbackError is raised when a device cannot
    # enqueue another update.
    pass

class ExtraFatal(Exception):
    # ExtraFatal error is designed to kill the server
    # when it is in a state that should not be possible.
    # ExtraFatal exceptions should never be caught except
    # in tests.
    pass
