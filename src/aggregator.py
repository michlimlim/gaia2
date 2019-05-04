class Aggregator(object):
    def __init__(self):
        self.model = {}
        self.updates = UpdateQueue()

    def aggregate_updates(self):
        dequeued_update = PendingWork.dequeue()
        if dequeued_update != None:
	        self.updates = self.update + dequeued_update

    def send_aggregated_update(self): 
        while self.updates != empty:
            update = self.updates.dequeue()
            for other_host in self.other_hosts:
                self.send(other_host, update)

