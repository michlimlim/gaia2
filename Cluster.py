#!/usr/bin/python3
import time, sys
from helpers import import_data_from_file
import numpy as np
import concurrent.futures

class Cluster:
    MAX_ID = 0

    def __init__(self, machine_speed):
        ## Create a new Cluster instance.
        # :param machine_speed [float] the speed of the machine, proportional to ops / sec
        # :param data_set [array<array<int>>] rows of a dataset where the first element contains the class of the row
        # :return [Cluster] a new Cluster instance
        self.machine_speed = machine_speed
        self.X = 0
        self.y = 0 
        self.latency_table = {}
        self.cluster_table = {}
        self.id = Cluster.MAX_ID + 1
        Cluster.MAX_ID += 1
    
    def get_id(self):
        ## Get the ID for this cluster.
        # return [int] the ID
        return self.id

    def set_data_set(self, X, y):
        ## Set the data set on which this cluster will train.
        # :param data_set [array<array<int>>] rowws of a dataset where the first element of each,
        #  row indicates the class of the row.
        self.X = X
        self.y = y

    def set_latency_to(self, cluster, latency):
        ## Set the latency this cluster has when sendin messages to another cluster.
        # This latency is artificial and trggers a sleep for the amount of time specified.
        # If there is *real* latency between clusters, the artificial latency should be 
        # set to zero.
        # :param cluster [Cluster] the cluster to which the latency is set
        # :param latency [float] the latency betwween clusters in seconds
        self.latency_table[cluster.get_id()] = latency
        self.cluster_table[cluster.get_id()] = cluster

    def go(self):
        # If I want to send a message to another cluster: 
        # time.sleep(self.latency_table[j])
        # self.cluster_table[j].some_func()
        print("hello")
        return "hello"

def launch_cluster(cluster):
    return cluster.go()
        
def main():
    ## TODO: Use real data  
    # all_data = import_data_from_file(sys.argv[1])

    # Generate Data 
    X = 2 * np.random.rand(100,1)
    y = 4 +3 * X + np.random.randn(100,1)

    max_machine_speed = 3
    max_server_latency = 5
    ## TODO: Figure out a way to have clusters dies and come back.
    clusters = [Cluster(k % max_machine_speed) for k in range(100)]
    ## TODO: Refactor and design a better assignment schema.
    size_of_data_partition = len(X) // len(clusters)
    for k in range(len(clusters)):
        low = k * size_of_data_partition
        hi = (k + 1) * size_of_data_partition
        clusters[k].set_data_set(X[low:hi], y[low:hi])
    for k in range(len(clusters)):
        for j in range(len(clusters)):
            if k != j:
                clusters[k].set_latency_to(clusters[j], (k + j) % max_server_latency)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(launch_cluster, clusters)

if __name__ == "__main__":
    main()