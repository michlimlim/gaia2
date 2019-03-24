#!/usr/bin/python3

from queue import Queue 
from threading import Event, RLock

class GlobalAggregator:

    def __init__(self, cluster_size, delta, size_of_partition):
        ## Create a new Aggregator instance. 
        # In Bulk Synchronous Parallel version, it aggregates updates from all nodes, before waking all nodes from sleep 
        self.cluster_size = cluster_size
        self.aggregation = [[] for j in range((self.cluster_size//delta + 1)*size_of_partition)]
        self.events = [Event() for k in range((self.cluster_size//delta + 1)*size_of_partition)]
        self.lock = RLock()
    
    def get_event(self, k):
    ## Called by the Cluster, to get the Event object for that the Cluster may sleep
        self.lock.acquire()
        ret = self.events[k]
        self.lock.release()
        return ret
    
    def get_aggregated_update(self, k):
    ## Called by the Cluster, to get the aggregated update for that round on global aggregation
        self.lock.acquire()
        ret = self.aggregation[k]
        self.lock.release()
        return ret
    
    def aggregate(self, k, update):
        self.lock.acquire(1)
        self.aggregation[k].append(update)
        if (len(self.aggregation[k])) == self.cluster_size:
            self.aggregation[k] = sum(self.aggregation[k])/ self.cluster_size
            self.wake_up_clusters(k)
        self.lock.release()

    def wake_up_clusters(self, k):
        self.lock.acquire()
        self.events[k].set()
        self.lock.release()