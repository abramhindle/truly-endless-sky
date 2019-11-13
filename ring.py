import larkendless as es
import random
import math
import math
import matplotlib.pyplot as plt
import networkx as nx
import networkx
import random
import forceatlas2
import numpy
import copy
import endlesssky
import scipy.spatial.distance

eso = endlesssky.EndlessSky()
eso.load_object_file()
n_systems = eso.n_systems()

minx = -1000
maxx = 1000
width = maxx - minx
miny = -1000
maxy = 1000
height = maxy - miny

def unit(p):
    v = math.sqrt(p[0]*p[0] + p[1]*p[1])
    return (p[0] / v, p[1] / v)

def vec_scalar_mul(p,s):
    return (p[0]*s, p[1]*s)

def vec_add(p1,p2):
    return (p1[0] + p2[0], p1[1] + p2[1])

def vec_sub(p1,p2):
    return (p1[0] - p2[0], p1[1] - p2[1])


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


def generate_inital_graph(n_systems, inner_radius=1500, outer_radius=2000, dist_push=50.0,prob=0.076,p=0.4,n_rounds=4000):
    point_n = 0
    G = nx.Graph()
    pos = {}
    def generate_point(inner_radius, outer_radius):
        pt = (outer_radius,outer_radius)
        sqr = pt[0]*pt[0] + pt[1]*pt[1]
        too_close = False
        while not ( sqr >= inner_radius**2 and sqr <= outer_radius**2 ):
            pt = [random.random() * 2 * outer_radius - outer_radius for x in [1,2]]
            sqr = pt[0]*pt[0] + pt[1]*pt[1]
        return pt
    for i in range(n_systems):
        G.add_node(point_n)
        pos[point_n] = generate_point(inner_radius, outer_radius)
        point_n += 1
    y = [pos[i] for i in range(point_n)]
    dist = scipy.spatial.distance.cdist(y,y,'euclidean')
    closest_points = numpy.argsort(dist)
    for i in range(point_n):
        for j in range(random.choice([3,4,5])):
            p = closest_points[i,j]
            if i != p:
                if  dist[i,p] < dist_push:
                    print(pos[i],pos[p],i,p)
                    posp = pos[p]
                    pos[p] = vec_add(posp, vec_scalar_mul( unit(vec_sub(posp, pos[i])), dist_push + dist_push * random.random()))
                    # pos[i] = vec_add(pos[i], vec_scalar_mul( unit(vec_sub(pos[i], posp)), dist_push + dist_push * random.random()))
                G.add_edge(i, p)
    nx.set_node_attributes(G, pos, 'pos')
    return G
            
def _generate_inital_graph(n_systems, prob=0.076,p=0.4,n_rounds=4000):
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
        govts.append( govt[n] )
    nx.set_node_attributes(G, govt, 'govt')
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
    plt.savefig('pirate.maps.txt.out.png')
    plt.show()

def distance(p1,p2):
    px = p1[0] - p2[0]
    py = p1[1] - p2[1]
    return math.sqrt(px*px + py*py)

pirate_systems = 300
# G2 = nx.thresholded_random_geometric_graph(pirate_systems, 0.07, 0.4)
# pos = nx.get_node_attributes(G2, 'pos')
# vector = None
# center = (0.5,0.5)
# def unit(p):
#     v = math.sqrt(p[0]*p[0] + p[1]*p[1])
#     return (p[0] / v, p[1] / v)
# 
# def vec_scalar_mul(p,s):
#     return (p[0]*s, p[1]*s)
# 
# def vec_add(p1,p2):
#     return (p1[0] + p2[0], p1[1] + p2[1])
# 
# def vec_sub(p1,p2):
#     return (p1[0] - p2[0], p1[1] - p2[1])
# 
# # recenter
# for n in pos:
#     p = pos[n]
#     pos[n] = vec_sub(p, center)
# 
# for n in pos:
#     p = pos[n]
#     if vector is None or distance(p,(0,0)) < distance(vector,(0,0)):
#         vector = p
# 
# #d = math.sqrt(60*60 + 60*60)
# #d2 = distance(vector,(0,0))
# ratio = 1500
# 
# 
# def project(p,expand=700):
#     u = unit(p)
#     return vec_add(vec_scalar_mul(u, ratio), vec_scalar_mul(p,expand))
# 
# pos = dict([(n,project(pos[n])) for n in pos])
# nx.set_node_attributes(G2, pos, 'pos')

G2 = generate_inital_graph(pirate_systems, inner_radius=1500, outer_radius=2000)
nx.set_node_attributes(G2, dict([(n,'Pirate') for n in G2.nodes()]), 'govt')

# we have to relabel them so we can find them
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
# connect them to each other
closest_comp_nodes = [choose_closest(G2,c,center=(0,0)) for c in G2comps]

pos = nx.get_node_attributes(G2, 'pos')
dcomp_nodes = [(distance((0,0), pos[n]), n) for n in closest_comp_nodes]
# print(dcomp_nodes)
dcomp_nodes.sort()
# dcomp_nodes.reverse()
closest_comp_nodes = [x[1] for x in dcomp_nodes]

def closest_pair(G, nodes1, nodes2):
    pos = nx.get_node_attributes(G, 'pos')
    pair = None
    for n1 in nodes1:
        for n2 in nodes2:
            if pair is None or distance(pos[n1],pos[n2]) < distance(pos[pair[0]],pos[pair[1]]):
                pair = (n1,n2)
    return pair

def argmin(l):
    m  = l[0]
    mi = 0
    for i in range(1,len(l)):
        if l[i] < m:
            mi = i
            m = l[i]
    return mi


def connect_components(G):
    comps = list(nx.connected_components(G))
    if len(comps) == 1:
        return
    comp1 = random.choice(comps)
    pos = nx.get_node_attributes(G, 'pos')
    closests = [(n,choose_closest(G,[n for n in G.nodes() if not n in comp1],center=pos[n])) for n in comp1]
    dists = [distance(pos[x[0]],pos[x[1]]) for x in closests]
    closest = closests[argmin(dists)]
    G.add_edge(closest[0],closest[1])
    return connect_components(G)


# remove edges that intersect 0,0 R = 50

def angle_between_points(p0,p1,p2):
    v0 = numpy.array(p0) - numpy.array(p1)
    v1 = numpy.array(p2) - numpy.array(p1)
    angle = numpy.math.atan2(numpy.linalg.det([v0,v1]),numpy.dot(v0,v1))
    return angle

def ortho_projection(lp0,lp1,center):
    p1 = lp1
    p0 = lp0
    p2 = center
    #lp1 to center is u
    #lp1 to lp0 is v
    # proju is (u dot v / length v^2) times v
    u = numpy.array(lp1) - numpy.array(center)
    v = numpy.array(lp1) - numpy.array(lp0)
    return u - (numpy.dot(u,v) / (numpy.linalg.norm(v))**2) * v
    
def line_intersect_circle(lp0,lp1,center,radius):
    perp_vec = ortho_projection(lp0,lp1,center)
    return numpy.linalg.norm( perp_vec ) < radius

def remove_edges_intersecting_circle(G2):
    edges = list(G2.edges())
    pos = nx.get_node_attributes(G2, 'pos')
    for edge in edges:
        a, b = edge
        lp0 = pos[a]
        lp1 = pos[b]
        center = (0,0)
        radius = 1400
        if line_intersect_circle(lp0,lp1,center,radius):
            print("Removing %s", (a,b))
            G2.remove_edge(a,b)

# clean up pirate space
# remove_extra_neighbors(G2)
connect_components(G2)
remove_edges_intersecting_circle(G2)
# make sure it is connected
connect_components(G2)
# clean it up again
remove_edges_intersecting_circle(G2)
# make sure there's no stragglers
connect_components(G2)


#graphit(G2)

govts = nx.get_node_attributes(G2, 'govt')
print(govts)

def extract_original_graph(eso):
    systems = eso.systems()
    n_systems = eso.n_systems()
    system_names = eso.system_names()
    system_names_to_system = eso.system_map()
    system_names_to_governments = eso.system_names_to_governments()
    positions = {}
    G = nx.Graph()
    for name in system_names:
        G.add_node(name)
        position = eso.get_system_position_by_name( name )
        positions[name] = position
        links = eso.get_system_links_by_name( name )
        for link in links:
            G.add_edge(name, link[1])
    nx.set_node_attributes(G, positions,'pos')
    nx.set_node_attributes(G, system_names_to_governments, 'govt')
    return G

# G3, _ = generate_inital_graph(375)

G3 = extract_original_graph(eso)
#graphit(G3)


G = nx.compose(G2,G3)


govts = nx.get_node_attributes(G, 'govt')

# connect the 2 graphs
for cnode in closest_comp_nodes[0:7]:
    pos = nx.get_node_attributes(G, 'pos')
    p = pos[cnode]
    closest = choose_closest(G3, G3.nodes(), center=p)
    G.add_edge(cnode, closest)

# # Rutilicus Debugging
# G.add_edge(random.choice(list(G2.nodes())), 'Rutilicus')
# G.add_edge(random.choice(list(G2.nodes())), 'Rutilicus')
G.add_edge(random.choice(list(G2.nodes())), 'Unagi')
G.add_edge(random.choice(list(G2.nodes())), 'Unagi')


# todo: add 1 link from pirates
    
def populate_pirate_ring(pirate_graph,whole_graph, eso):
    G2 = pirate_graph
    G = whole_graph
    system_names_to_governments = eso.system_names_to_governments()
    pirates = [x for x in system_names_to_governments.keys() if system_names_to_governments[x] == 'Pirate']
    rename = {}
    pos = nx.get_node_attributes(G2, 'pos')
    for node in G2.nodes():
        clone_system_name = random.choice(pirates)
        pirate_name = eso.duplicate_and_rename_system( clone_system_name )      
        eso.set_system_position_by_name( pirate_name, pos[node] )
        rename[node] = pirate_name
    G2 = nx.relabel_nodes(G2, rename)
    G = nx.relabel_nodes(G, rename)
    return (G2,G)
    
G2,G = populate_pirate_ring(G2, G, eso)

def sync_links(G, eso):
    """ We trust the links in G, not in eso """
    for node in G.nodes():
        # remove all the links
        # add the links from G
        print(node)
        eso.remove_links_of_system_name( node )
        for neighbor in G.neighbors(node):
            print("\t%s" % neighbor)
            eso.add_link_between_name( node , neighbor )

sync_links(G,eso)

print(G.nodes())
# print(govts)

eso.write_to_disk()
govts = nx.get_node_attributes(G, 'govt')
graphit(G,govts)
