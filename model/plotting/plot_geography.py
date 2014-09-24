import json
from node import Node
from plotting import plot_nodes
import matplotlib.pyplot as plt

plt.figure('Geography',figsize=(5,8))
ax=plt.subplot(111)
ax.set_aspect('equal')

def plot_country(country,color):
    nodes=[]
    with open('../geography/nodes.json','r') as fjson:
        j=json.loads(fjson.read())
        for n in j:
            if country not in n['Name']:
                continue
            nodes.append(Node.fromDict(n))
    plot_nodes(nodes,color=color)

plot_country('Guinea', 'b')
plot_country('Sierra', 'g')
plot_country('Liberia', 'r')

plt.show()
