import random

ch = {}

class Node(object):

    def __init__(self):
        self.ID = id(self)
        self.weight = random.randint(1, 10)
        self.cluster = []
        self.clusterHead = None
        self.neighbours = []
        ch[self] = False
        self.start()

    def start(self):
        big = self.largestNeighbour()
        if big and big.weight > self.weight:
            self.callJoin(big)
            self.clusterHead = big
        else:
            self.callCh()
            ch[self] = True
            self.clusterHead = self
            if self not in self.cluster:
                self.cluster.append(self)

    def show(self):
        print("ID = %s | Weight = %s | clusterhead = %s" %
              (self.ID, self.weight, self.clusterHead.ID))
        print(" ".join([str(mem.ID) for mem in self.cluster]))

    def largestNeighbour(self):
        max = 0
        biggest = None
        for neighbour in self.neighbours:
            if neighbour.weight > max and ch(neighbour):
                max = neighbour.weight
                biggest = neighbour
        return biggest

    def callJoin(self, big):
        for neighbour in self.neighbours:
            neighbour.getJoin(self, big)

    def getJoin(self, u, z):
        if ch[self]:
            if z == self:
                self.cluster.append(u)
            elif u in self.cluster:
              self.cluster.remove(u)
        elif self.clusterHead == u:
            self.start()

    def callCh(self):
        for neighbour in self.neighbours:
            neighbour.getCh(self)

    def getCh(self, u):
        if not self.clusterHead or u.weight > self.clusterHead.weight:
            self.callJoin(u)
            ch[self] = False

    def newLink(self, u):
        self.neighbours.append(u)
        if ch[u]:
            if self.clusterHead and u.weight > self.clusterHead.weight:
                self.callJoin(u)
                self.clusterHead = u
                ch[self] = False

    def linkFail(self, u):
        self.neighbours.remove(u)
        if ch[self] and u in self.cluster:
            self.cluster.remove(u)
        elif self.clusterHead == u:
            self.start()
