from threading import Thread
import subprocess
from queue import Queue
import re

ch = []
num_threads = 4

class Node(object):

    def __init__(self, ip, dht):
        self.ID = ip
        self.weight = 0
        self.cluster = []
        self.clusterHead = None
        self.neighbours = dht
        self.ips_q

    #We should come up with something much more cleverer
    #Calculates and assigns a weight to this node
    #Might be based on #connections or bandwidth availability
    def weigh(self):
        self.weight = self.ID

    def bestNeighbour(self):
        latency = {}
        for neighbour in self.neighbours:
            latency[neighbour] = threadPing(neighbour)
