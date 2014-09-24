import json
from node import Node
from plotting import plot_nodes
import matplotlib.pyplot as plt
import csv
from collections import namedtuple
import math

plt.figure('Migration',figsize=(5,8))
ax=plt.subplot(111)
ax.set_aspect('equal')

def gravity(p1,p2,hr,G=1e-8):
    dist=50*hr # transform time into distance
    return G*p1*p2/dist**2

weights=[]
def plot_country(country,color):
    nodes={}
    with open('../geography/nodes.json','r') as fjson:
        j=json.loads(fjson.read())
        for n in j:
            #if country not in n['Name']:
            #    continue
            nodes[n['Name']]=Node.fromDict(n)
    plot_nodes([v for v in nodes.values() if country in v.name],color=color)

    with open('../migration/driving_times.csv') as csvfile:
        reader=csv.reader(csvfile)
        header=reader.next()
        route=namedtuple('route',header)
        for row in reader:
            r=route(*row)
            if all([country in p for p in [r.origin,r.destination]]):
                linecolor=color
            elif country in r.origin:
                linecolor='black' #cross border connections
            else:
                continue
            origin=nodes[r.origin]
            destination=nodes[r.destination]
            weight=gravity(origin.pop,destination.pop,float(r.hr))
            weights.append(weight)
            plt.plot([origin.lon,destination.lon],[origin.lat,destination.lat], 
                        linecolor, alpha=min(0.8,0.03+30*weight), lw=min(2,0.03+weight))

plot_country('Guinea', 'b')
plot_country('Sierra', 'g')
plot_country('Liberia', 'r')

weights.sort()
print(weights[:5],weights[-5:])
plt.tight_layout()
plt.show()
