#!/usr/bin/python3

import concurrent.futures
import numpy as np
from sgd import compute_local_theta, cal_cost
from cluster import Cluster
from globalaggregator import GlobalAggregator
from threading import Thread

def main():
    ## TODO: Use real data  
    # all_data = import_data_from_file(sys.argv[1])

    # Generate Data 
    X = 2 * np.random.rand(100,1)
    y = 4 +3 * X + np.random.randn(100,1)

    # Initialize variables 
    max_machine_speed = 3
    max_server_latency = 5
    cluster_size = 10
    delta = 3
    size_of_data_partition = len(X) // cluster_size

    aggregator = GlobalAggregator(cluster_size)

    ## TODO: Figure out a way to have clusters dies and come back.
    clusters = [Cluster(k % max_machine_speed, aggregator, delta) for k in range(cluster_size)]

    for k in range(len(clusters)):
        low = k * size_of_data_partition
        hi = (k + 1) * size_of_data_partition
        clusters[k].set_data_set(X[low:hi], y[low:hi])
    for k in range(len(clusters)):
        for j in range(len(clusters)):
            if k != j:
                clusters[k].set_latency_to(clusters[j], (k + j) % max_server_latency)
    #with concurrent.futures.ThreadPoolExecutor() as executor:
        #result = executor.map(launch_cluster, clusters)
    threads = []
    for cluster in clusters:
        t = Thread(target=cluster.go)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    final_theta = aggregator.get_aggregated_update()
    print('Theta0:          {:0.3f},\nTheta1:          {:0.3f}'.format(final_theta[0][0],final_theta[1][0]))

if __name__ == "__main__":
    main()