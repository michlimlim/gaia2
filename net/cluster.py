import random

class Node(object):

    def __init__(self):
        self.ID = id(self)
        self.weight = random.randint(1, 10)
        self.cluster = []

    def addCluster(self, n):
        self.cluster.append(n)

    def show(self):
        print("ID = %s | Weight = %s | cluster = %s" % (self.ID, self.weight, self.cluster))