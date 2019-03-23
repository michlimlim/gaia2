#!/usr/bin/python3

from queue import Queue 
from threading import Condition

class GlobalAggregator:

    def __init__(self, cluster_size, delta):
        ## Create a new Aggregator instance. 
        # In Bulk Synchronous Parallel version, it aggregates updates from all nodes, before waking all nodes from sleep 
        self.cluster_size = cluster_size
        self.aggregation = []
        self.conditions = [Condition() for k in range(self.cluster_size//delta)]
    
    def get_condition(self, k):
    ## Called by the Cluster, to get the Condition object for that the Cluster may sleep
        return self.conditions[k]
    
    def get_aggregrated_update(self, k):
    ## Called by the Cluster, to get the aggregated update for that round on global aggregation
        return self.aggregration[k]
    
    def aggregate(self, k, update):
        self.aggregration[k].append(update)
        if (len(self.aggregation[k])) == self.cluster_size:
            self.aggregration[k] = sum(self.aggregration[k])/ self.cluster_size
            self.wake_up_clusters(k)

    def wake_up_clusters(self, k):
        self.conditions[k].notifyAll()