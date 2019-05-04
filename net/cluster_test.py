from cluster import Node

if __name__ == "__main__":
    a = Node()
    b = Node()
    c = Node()
    a.addCluster(b)
    a.addCluster(c)
    a.show()
    a.cluster[0].show()
    a.cluster[1].show()