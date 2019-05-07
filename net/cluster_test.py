import networkx as nx
import matplotlib.pyplot as plt
from cluster import Node
from cluster import ch

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

def drawGraph(arr):
    colours = []
    for n in arr:
        if ch[n]:
            colours.append("red")
        else:
            colours.append("blue")
    nx.draw(G, node_color=colours, with_labels=False, font_weight='bold')
    plt.savefig("graph.png")

def info(arr):
    for node in arr:
        node.show()

if __name__ == "__main__":
    arr  = []
    for i in range(0, 5):
        arr.append(Node())
        G.add_node(arr[i].ID)

    for i in range(0, 5):
        for j in range(i, 5):
            if i != j:
                createEdge(arr[i], arr[j])

    for i in range(0, 4):
        breakEdge(arr[i], arr[i + 1])

    drawGraph(arr)
    info(arr)