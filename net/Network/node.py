import sys
from bottle import route, run

ch = {}
class Node(object):

    def __init__(self, val):
        #self.ID = id(self)
        #self.weight = random.randint(1, 10)
        self.ID = val
        self.weight = self.ID
        self.cluster = []
        self.clusterHead = None
        self.neighbours = []
        ch[self] = False
        self.start()

    #Find a new cluster:
        #If you are not the biggest of your neighbours:
            #Join the biggest cluster head
        #Else:
            #Start a cluster
    def start(self):
        big = self.largestNeighbour()
        if big and big.weight > self.weight:
            self.join(big)
        else:
            self.callCh()

    #Print your info
    def show(self):
        print("ID = %s | Weight = %s | clusterhead = %s" %
              (self.ID, self.weight, self.clusterHead.ID))
        if ch[self]:
            print(" ".join([str(mem.ID) for mem in self.cluster]))

    #Return the weightiest neighbour
    def largestNeighbour(self):
        max = 0
        biggest = None
        for neighbour in self.neighbours:
            if ch[neighbour] and neighbour.weight > max:
                max = neighbour.weight
                biggest = neighbour
        return biggest

    #Alert your neighbours that you are moving
    #Move
    def join(self, newCh):
        self.clusterHead = newCh
        ch[self] = False
        self.cluster.clear()
        self.callJoin(newCh)

    #Alert your neighbours that you are moving
    def callJoin(self, big):
        for neighbour in self.neighbours:
            neighbour.getJoin(self, big)

    #When you receive a join notification:
        #If you are a cluster head:
            #If they are joining you:
                #Add them to your cluster
            #Else If they are in your cluster:
                #Remove them (they are joining elsewhere)
        #Else If they are your cluster head:
            #Join a new cluster
    def getJoin(self, u, z):
        if ch[self]:
            if z == self:
                self.cluster.append(u)
            elif u in self.cluster:
              self.cluster.remove(u)
        elif self.clusterHead == u:
            self.start()

    #When you become a cluster head:
        #Alert all your neighbours that you are a cluster head
    def callCh(self):
        ch[self] = True
        self.clusterHead = self
        self.cluster.append(self)
        for neighbour in self.neighbours:
            neighbour.getCh(self)

    #When you get a new cluster head notification:
        #If they are a better clusterhead than you:
            #Join them
    def getCh(self, u):
        if u.weight > self.clusterHead.weight:
            self.join(u)

    #When a new link is setup:
        #Save your new neighbour's address
        #If your neighbour is a cluster head:
            #If they outrank you:
                #Join the better cluster

    @route('/hello/<ip>')
    def newLink(self, u):
        self.neighbours.append(u)
        if ch[u] and u.weight > self.clusterHead.weight:
            self.join(u)

    #When a link fails:
        #Remove that node from your neighbours
        #If you are their cluster head:
            #Remove them from your cluster
        #Else If they are your cluster head:
            #Find a new cluster head
    def linkFail(self, u):
        self.neighbours.remove(u)
        if ch[self] and u in self.cluster:
            self.cluster.remove(u)
        elif self.clusterHead == u:
            self.start()