from cluster import Node
from cluster import ch

def createEdge(a, b):
    a.newLink(b)
    b.newLink(a)

def breakEdge(a, b):
    if b in a.neighbours:
        a.linkFail(b)
        b.linkFail(a)

def nodeFail(a):
    for neighbour in a.neighbours:
        breakEdge(a, neighbour)

if __name__ == "__main__":
    arr  = []
    for i in range(0, 5):
        arr.append(Node())

    createEdge(arr[0], arr[1])

    arr[0].show()
    arr[1].show()

    breakEdge(arr[0], arr[1])

    arr[0].show()
    arr[1].show()