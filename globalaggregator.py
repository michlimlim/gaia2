#!/usr/bin/python3

from queue import Queue 
from threading import Event, RLock
import numpy as np

class GlobalAggregator:

    def __init__(self, cluster_size):
        ## Create a new Aggregator instance. 
        # In Bulk Synchronous Parallel version, it aggregates updates from all nodes, before waking all nodes from sleep 
        self.cluster_size = cluster_size
        self.aggregation = []
        self.event = Event()
        self.lock = RLock()
        self.global_theta = 0
        # Keeps track of number of clusters that have reported to it
        self.update_count = 0 
    
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
    
    def increment_count(self):
        self.lock.acquire(1)
        self.update_count += 1
        if self.update_count == self.cluster_size:
            if len(self.aggregation) > 0:
                self.global_theta = sum(self.aggregation)/len(self.aggregation)
            else:
                self.global_theta = np.array([None, None])
            self.wake_up_clusters()
        self.lock.release()
    
    def aggregate(self, update):
        self.lock.acquire(1)
        self.aggregation.append(update)
        self.increment_count()
        self.lock.release()

    def wake_up_clusters(self):
        self.lock.acquire()
        self.event.set()
        self.aggregation = []
        self.event = Event()
        self.update_count = 0 
        self.lock.release()