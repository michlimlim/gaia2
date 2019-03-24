# Gaia2

A simple simulation of data centers engaging in federated learning. For now, it applies Asynchronous Synchronous Parallel with Bulk Synchronous Parallel. 

## Getting Started

```
pip install requirements.txt
python main.py
```
## Overview

* `Cluster` (cluster.py) is a worker node that runs SGD, and sends an update to a global aggregator whenever its update exceeds the significance threshold (`significance_threshold)`. Once it sends out a global aggregate update, it freezes until the global aggregator wakes it up. 
* `GlobalAggregator` (globalaggregator.py) is the aggregator that collates updates during global aggregation rounds. Once it is done with aggregation for the round, it wakes up all the clusters
*  `main.py` is the driver program that sets up a basic linear regression problem. (To see more details of the sgd function, see `sgd.py`)

## How it models actual data centers

* To run like parallel data centers, I run `Cluster` on a thread. Communication between threads = Communication between "data centers"
* To model different computing speeds, I make the cluster sleep for `x` amount of time for each sgd update (`compute_local_theta`). 
* To model different latency's for now, I make the cluster sleep for `x` amount of time every time it has to update the global aggregator. 

