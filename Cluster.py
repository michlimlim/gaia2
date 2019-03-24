#!/usr/bin/python3
import numpy as np
from sgd import compute_local_theta
import time 
from math import sqrt

class Cluster:
    MAX_ID = 0

    def __init__(self, machine_speed, aggregator, delta):
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
        self.aggregator = aggregator
        self.delta = delta
        Cluster.MAX_ID += 1
    
    def get_id(self):
        ## Get the ID for this cluster.
        # return [int] the ID
        return self.id

    def set_data_set(self, X, y):
        ## Set the data set on which this cluster will train.
        # :param data_set [array<array<int>>] rowws of a dataset where the first element of each,
        #  row indicates the class of the row.
        self.X = np.c_[np.ones((len(X),1)),X]
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
    
    def global_aggregate(self, theta):
        sleep = self.aggregator.get_event()
        # SIMULATES LATENCY! 
        time.sleep(3)
        self.aggregator.aggregate(theta)
        sleep.wait()
        theta = self.aggregator.get_aggregated_update()
        return theta
    
    def send_skip(self):
        self.aggregator.increment_count()

    def significance_fn(self, theta, global_theta):
        significance = abs((global_theta-theta)/theta)
        significance = significance.sum(axis=0)[0]
        return significance

    def significance_threshold(self, iter):
        return 1/sqrt(iter)

    def go(self):
        # If I want to send a message to another cluster: 
        # time.sleep(self.latency_table[j])
        # self.cluster_table[j].some_func()
        '''
        X    = Matrix of X with added bias units
        y    = Vector of Y
        theta=Vector of thetas np.random.randn(j,1)
        learning_rate 
        iterations = no of iterations
        
        Returns the final theta vector and array of cost history over no of iterations
        '''
        iterations = 5
        theta = np.random.randn(2,1)

        m = len(self.y)
        cost_history = np.zeros(iterations)

        global_theta = theta
        iter = 0
        for it in range(iterations):
            cost = 0.0
            for i in range(m):
                ## Compute update
                print("[cluster: {:2d}] iter = {:d}".format(self.get_id(), iter))
                theta, cost = compute_local_theta(m, self.X, self.y, theta, cost, self.machine_speed/10.0)
                ## Global aggregation
                if iter > 0 and (iter % self.delta) == 0:
                    significance = self.significance_fn(theta, global_theta)
                    
                    if significance > self.significance_threshold(iter):
                        print("[cluster: {:2d}] global update step  = {:d} sig= {:02f} PAST THRESHOLD!".format(self.get_id(), iter//self.delta, significance))
                        agg = self.global_aggregate(theta)
                        if agg.any() != global_theta.any():
                            theta = agg
                            global_theta = theta
                    else: 
                        print("[cluster: {:2d}] global update step  = {:d} sig= {:02f} Skip Aggregation".format(self.get_id(), iter//self.delta, significance))
                        self.send_skip()
                iter += 1
        cost_history[it]  = cost
        # print('Theta0:          {:0.3f},\nTheta1:          {:0.3f}\nFinal cost/MSE:  {:0.3f}\n'.format(theta[0][0],theta[1][0],cost_history[-1]))
        return theta, cost_history[-1]
        