import larkendless as es
import random
import math
import math
import matplotlib.pyplot as plt
import networkx as nx
import networkx
import random
import forceatlas2

maps = es.parse_endless_sky_file("data.orig/map.txt.original")
print(len(maps))
systems = es.endless_type_grep(maps, "system")
n_systems = len(systems)

minx = -1000
maxx = 1000
width = maxx - minx
miny = -1000
maxy = 1000
height = maxy - miny

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


def generate_inital_graph(n_systems, prob=0.076,p=0.4,n_rounds=4000):
    G = nx.thresholded_random_geometric_graph(n_systems, 0.076, 0.4)
    remove_extra_neighbors(G,n_rounds)
    pos = nx.get_node_attributes(G, 'pos')
    pos = forceatlas2.forceatlas2_networkx_layout(G, pos=pos,
                                                  edgeWeightInfluence=1.0,
                                                  jitterTolerance=1.0, 
                                                  scalingRatio=2.0,
                                                  strongGravityMode=True,
                                                  gravity=1.0)
    nx.set_node_attributes(G, pos, 'pos')
    govt = {}
    govts = []
    for n in G.nodes():
        govt[n] = random.choice(['Coalition','Korath','Hai'])
        govts += govt[n]
    nx.set_node_attributes(G, govts, 'govt')
    return G, govt


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
    govts = list(set(govt.values()))
    govts.sort()
    govt_to_color = dict(zip(govts, range(len(govts))))
    colors = [govt_to_color[govt[n]] for n in G.nodes]
    # p = dict(nx.single_source_shortest_path_length(G, ncenter))
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_nodes(G, pos,
                           node_color=colors,
                           node_size=80,
                           cmap=plt.cm.tab10_r)
    plt.axis('off')
    #plt.savefig('pirate.maps.txt.out.png')
    plt.show()

def distance(p1,p2):
    px = p1[0] - p2[0]
    py = p1[1] - p2[1]
    return math.sqrt(px*px + py*py)

pirate_systems = 300
G2 = nx.thresholded_random_geometric_graph(pirate_systems, 0.07, 0.4)
pos = nx.get_node_attributes(G2, 'pos')
vector = None
center = (0.5,0.5)
def unit(p):
    v = math.sqrt(p[0]*p[0] + p[1]*p[1])
    return (p[0] / v, p[1] / v)

def vec_scalar_mul(p,s):
    return (p[0]*s, p[1]*s)

def vec_add(p1,p2):
    return (p1[0] + p2[0], p1[1] + p2[1])

def vec_sub(p1,p2):
    return (p1[0] - p2[0], p1[1] - p2[1])

# recenter
for n in pos:
    p = pos[n]
    pos[n] = vec_sub(p, center)

for n in pos:
    p = pos[n]
    if vector is None or distance(p,(0,0)) < distance(vector,(0,0)):
        vector = p

#d = math.sqrt(60*60 + 60*60)
#d2 = distance(vector,(0,0))
ratio = 50


def project(p):
    u = unit(p)
    return vec_add(vec_scalar_mul(u, ratio), vec_scalar_mul(p,400))

pos = dict([(n,project(pos[n])) for n in pos])
nx.set_node_attributes(G2, ['Pirate' for n in G2.nodes()], 'govt')
nx.set_node_attributes(G2, pos, 'pos')

mapping = dict([(n,10000+n) for n in G2.nodes()])
G2 = nx.relabel_nodes(G2, mapping)

def choose_closest(G, node_list, center=(0,0)):
    pos = nx.get_node_attributes(G, 'pos')
    closest = None
    for node in node_list:
        if closest is None or distance(center,pos[node]) < distance(center,pos[closest]):
            closest = node
    return closest

G2comps = nx.connected_components(G2)
closest_comp_nodes = [choose_closest(G2,c,center=(0,0)) for c in G2comps]

print(G2.nodes())
graphit(G2)

G3, _ = generate_inital_graph(375)
graphit(G3)
G = nx.compose(G2,G3)
#govts = nx.get_node_attributes(G, 'govt')

# connect the 2 graphs
for cnode in closest_comp_nodes:
    pos = nx.get_node_attributes(G, 'pos')
    p = pos[cnode]
    closest = choose_closest(G3, G3.nodes(), center=p)
    G.add_edge(cnode, closest)
    
graphit(G)
