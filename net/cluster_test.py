import sys
import networkx as nx
import matplotlib.pyplot as plt
from cluster import Node
from cluster import ch

DEBUG = "PARTIAL"
num = max(1, int(sys.argv[1]))
G = nx.Graph()

def createEdge(a, b):
    a.newLink(b)
    b.newLink(a)
    G.add_edge(a.ID, b.ID)

def breakEdge(a, b):
    if b in a.neighbours:
        a.linkFail(b)
        b.linkFail(a)
        G.remove_edge(a.ID, b.ID)

def nodeFail(a):
    for neighbour in a.neighbours:
        breakEdge(a, neighbour)

def drawGraph(arr, i):
    colours = []
    for n in arr:
        if ch[n]:
            colours.append("red")
        else:
            colours.append("blue")
    image = plt.figure()
    nx.draw_networkx(G, node_color=colours, with_labels=True, font_weight='bold')
    if (i != -1):
        image.savefig("graph_" + str(i) + ".png")
    else:
        image.savefig("final_graph.png")
    image.clear()
    plt.close(image)

def info(arr):
    if DEBUG == "FULL":
        for node in arr:
            node.show()
    elif DEBUG == "PARTIAL":
        for node in arr:
            if ch[node]:
                node.show()

if __name__ == "__main__":
    arr  = []
    for i in range(0, num):
        arr.append(Node(i))
        G.add_node(arr[i].ID)

    #Create an all-all graph
    #for i in range(0, num):
    #    for j in range(i, num):
    #        if i != j:
    #            createEdge(arr[i], arr[j])

    #Create a simple cyclic graph
    for i in range(0, num):
        createEdge(arr[i], arr[(i + 1) % num])
    #    drawGraph(arr, i)

    drawGraph(arr, -1)
    info(arr)