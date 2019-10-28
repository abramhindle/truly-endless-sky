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

def graphit(G, govt=None):
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
    if govt is None:
        govt = dict([(n,1) for n in G.nodes ])
    print(govt)
    govts = list(set(govt.values()))
    govts.sort()
    govt_to_color = dict(zip(govts, range(len(govts))))
    colors = [govt_to_color[govt[n]] for n in G.nodes]
    print(govts)
    print(colors)
    # p = dict(nx.single_source_shortest_path_length(G, ncenter))
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_nodes(G, pos,
                           node_color=colors,
                           node_size=80,
                           cmap=plt.cm.tab10_r)
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

# at this point the association is complete
system_names = [system[0][1] for system in systems]
system_names_to_system = dict(zip(system_names, systems))
governments = [es.endless_first(system, "government")[1] for system in systems]
system_names_to_governments = dict(zip(system_names, governments))
node_to_system_names = dict(zip(nodes,system_names))

def swap_node(G, node1, node2):
    """ this is a lot of work """
    pos = nx.get_node_attributes(G, 'pos')
    neighbors1 = G.neighbors(node1)
    neighbors2 = G.neighbors(node2)
    # remove the edges
    for n1 in neighbors1:
        G.remove_edge(node1,n1)
    for n2 in neighbors2:
        G.remove_edge(node2,n2)
    # add the remove nodes
    for n1 in neighbors1:
        G.add_edge(node2,n1)
    for n2 in neighbors2:
        G.add_edge(node1,n2)
    # swap the pos
    pos[node1], pos[node2] = pos[node2], pos[node1]
    nx.set_node_attributes(G, 'pos', pos)

def shuffle_of(l):
    ll = list(l)
    random.shuffle(ll)
    return ll
    
def dictswap(dict1, node1,node2):
    dict1[node1], dict1[node2] = dict1[node2], dict1[node1]
    
def swap_systems(node1, node2):
    dictswap(node_to_system_names, node1, node2)

def govt_of_node(node):
    system_name = node_to_system_names[node]
    return system_names_to_governments[system_name]
    
# idea: given a node can we increase the government adjacent count of its neighbors?
def count_govt_neighbor(node):
    govt = govt_of_node(node)
    x = sum([govt_of_node(n) == govt for n in G.neighbors(node)])
    return (x, govt)

def keep_neighborhoods_similar():
    # keep the neighborhoods kinda similar
    for node in shuffle_of(nodes):
        system_name = node_to_system_names[node]
        count, govt = count_govt_neighbor( node )
        other_govts = [g for g in [(govt_of_node(n),n) for n in G.neighbors(node)] if g[0] != govt]
        for gn in other_govts:
            g,n = gn
            swap_systems( node, n )
            c2, _ = count_govt_neighbor( node )
            if (c2 < count):
                """ undo """
                swap_systems( node, n )

for i in range(100):
    keep_neighborhoods_similar()





def move_system(system, x, y):
    system = es.endless_replace( system, 'pos', (x,y) )
    return system

def remove_links(system):
    return es.endless_delete_type(system, 'link')

pos = nx.get_node_attributes(G, 'pos')
node_to_system = dict([ (n,system_names_to_system[ node_to_system_names[n] ])  for n in node_to_system_names ])

for node in node_to_system:
    system = node_to_system[node]
    x = pos[node][0]
    y = pos[node][1]
    xp = x/60 * width - minx
    yp = y/60 * width - miny
    system = move_system(system, xp, yp)
    system = remove_links( system )
    for neighbor in G.neighbors(node):
        es.endless_add_property(system,('link', node_to_system[neighbor][0][1]))
    node_to_system[node] = system
    
for k in node_to_system:
    system = node_to_system[k]
    es.endless_replace_entity(maps, system[0], system)

out = es.serialize_entities(maps)
open("maps.txt.out", 'w').write(out)

node_to_govt = dict([(n, system_names_to_governments[ node_to_system_names[ n ] ]) for n in node_to_system_names])

graphit(G, govt=node_to_govt)
