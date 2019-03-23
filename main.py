#!/usr/bin/python3

import concurrent.futures
import numpy as np
from sgd import compute_local_theta
from cluster import Cluster
from globalaggregator import GlobalAggregator

def main():
    ## TODO: Use real data  
    # all_data = import_data_from_file(sys.argv[1])

    # Generate Data 
    X = 2 * np.random.rand(10000,1)
    y = 4 +3 * X + np.random.randn(10000,1)

    # Initialize variables 
    max_machine_speed = 3
    max_server_latency = 5
    cluster_size = 100
    delta = 5
    aggregator = GlobalAggregator(cluster_size, delta)

    ## TODO: Figure out a way to have clusters dies and come back.
    clusters = [Cluster(k % max_machine_speed, aggregator, delta) for k in range(cluster_size)]

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

def launch_cluster(cluster):
    return cluster.go()

if __name__ == "__main__":
    main()