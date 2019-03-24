#!/usr/bin/python3

from queue import Queue 
from threading import Event, RLock

class GlobalAggregator:

    def __init__(self, cluster_size):
        ## Create a new Aggregator instance. 
        # In Bulk Synchronous Parallel version, it aggregates updates from all nodes, before waking all nodes from sleep 
        self.cluster_size = cluster_size
        self.aggregation = []
        self.event = Event()
        self.lock = RLock()
        self.global_theta = 0
    
    def get_event(self):
    ## Called by the Cluster, to get the Event object for that the Cluster may sleep
        self.lock.acquire()
        ret = self.event
        self.lock.release()
        return ret
    
    def get_aggregated_update(self):
    ## Called by the Cluster, to get the aggregated update for that round on global aggregation
        self.lock.acquire()
        ret = self.global_theta
        self.lock.release()
        return ret
    
    def aggregate(self, update):
        self.lock.acquire(1)
        self.aggregation.append(update)
        if (len(self.aggregation)) == self.cluster_size:
            self.global_theta = sum(self.aggregation)/ self.cluster_size
            self.wake_up_clusters()
        self.lock.release()

    def wake_up_clusters(self):
        self.lock.acquire()
        self.event.set()
        self.aggregation = []
        self.event = Event()
        self.lock.release()