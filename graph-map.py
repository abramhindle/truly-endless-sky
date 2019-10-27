import larkendless as es
import random
import math

start_system = 'Rutilicus'

maps = es.parse_endless_sky_file("data.orig/map.txt.original")
print(len(maps))
systems = es.endless_type_grep(maps, "system")
n_systems = len(systems)


import math
import matplotlib.pyplot as plt
import networkx as nx
import networkx
import random

nodes = n_systems

import forceatlas2

def remove_extra_neighbors(G,rounds=2000):
    for i in range(rounds):
        edges = list(G.edges())
        edge = random.choice(edges)
        # choose random node
        neighbors = list(nx.common_neighbors(G, edge[0], edge[1]))
        if len(neighbors) >= 1:
            neighbor = random.choice(neighbors)
            source = random.choice([edge[0],edge[1]])
            G.remove_edge(source, neighbor)

G = nx.thresholded_random_geometric_graph(nodes, 0.075, 0.4)
remove_extra_neighbors(G,4000)

pos = nx.get_node_attributes(G, 'pos')
pos = forceatlas2.forceatlas2_networkx_layout(G, pos=pos,
    edgeWeightInfluence=1.0,
    jitterTolerance=1.0, 
    scalingRatio=2.0,
    strongGravityMode=True,
    gravity=1.0)
nx.set_node_attributes(G, pos, 'pos')

def graphit(G):
    pos = nx.get_node_attributes(G, 'pos')
    # find node near center (0.5,0.5)
    dmin = 1
    ncenter = 0
    for n in pos:
        x, y = pos[n]
        d = (x - 0.5)**2 + (y - 0.5)**2
        if d < dmin:
            ncenter = n
            dmin = d

    # color by path length from node near center
    p = dict(nx.single_source_shortest_path_length(G, ncenter))
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_nodes(G, pos,
                        node_size=80,
                        cmap=plt.cm.Reds_r)
    plt.axis('off')
    plt.show()

    
minx = -1000
maxx = 1000
width = maxx - minx
miny = -1000
maxy = 1000
height = maxy - miny

random.shuffle(systems)
nodes = list(G.nodes())
random.shuffle(nodes)

node_to_system = dict(zip(nodes,systems))

def move_system(system, x, y):
    system = es.endless_replace( system, 'pos', (x,y) )
    return system

def remove_links(system):
    return es.endless_delete_type(system, 'link')

i = 0
pos = nx.get_node_attributes(G, 'pos')

for i in range(len(systems)):
    system = systems[i]
    node = nodes[i]
    x = pos[node][0]
    y = pos[node][1]
    xp = x/60 * width - minx
    yp = y/60 * width - miny
    system = move_system(system, xp, yp)
    system = remove_links( system )
    for neighbor in G.neighbors(node):
        es.endless_add_property(system,('link', node_to_system[neighbor][0][1]))
    i += 1
    node_to_system[node] = system
    
for k in node_to_system:
    system = node_to_system[k]
    es.endless_replace_entity(maps, system[0], system)

out = es.serialize_entities(maps)
open("maps.txt.out", 'w').write(out)

graphit(G)
