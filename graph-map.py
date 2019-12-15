import trulyendlesssky.larkendless as es
import random
import math
import math
import matplotlib.pyplot as plt
import networkx as nx
import networkx
import random
import forceatlas2

start_system = 'Rutilicus'

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


# this stuff is for the intro mission support. You don't actually need it
obj_to_system_name = dict()
for system in systems:
    sysname = system[0][1]
    objects = es.endless_recursive_type_grep(system, "object")
    for obj in objects:
        if len(obj[0]) > 0:
            n = obj[0][1]
            if n is not None:
                obj_to_system_name[n] = sysname
    obj_to_system_name[sysname] = sysname

assert 'Ingot' in obj_to_system_name


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
    # p = dict(nx.single_source_shortest_path_length(G, ncenter))
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_nodes(G, pos,
                           node_color=colors,
                           node_size=80,
                           cmap=plt.cm.tab10_r)
    plt.axis('off')
    plt.savefig('maps.txt.out.png')
    plt.show()

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
    """ don't modify l, copy and shuffle """
    ll = list(l)
    random.shuffle(ll)
    return ll
    
def dictswap(dict1, node1,node2):
    dict1[node1], dict1[node2] = dict1[node2], dict1[node1]

def generate_graph(n_systems, prob=0.076,p=0.4,n_rounds=4000):
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
    return G

def populate_graph(G, maps,systems):

    random.shuffle(systems)
    nodes = list(G.nodes())
    random.shuffle(nodes)    

    # at this point the association is complete
    system_names = [system[0][1] for system in systems]
    system_names_to_system = dict(zip(system_names, systems))
    governments = [es.endless_first(system, "government")[1] for system in systems]
    system_names_to_governments = dict(zip(system_names, governments))
    node_to_system_names = dict(zip(nodes,system_names))

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
                if (c2 <= count):
                    """ undo """
                    swap_systems( node, n )

    # keep neighborhoods pretty similar 
    for i in range(100):
        keep_neighborhoods_similar()

    pos = nx.get_node_attributes(G, 'pos')
    node_to_system = dict([ (n,system_names_to_system[ node_to_system_names[n] ])  for n in node_to_system_names ])
    system_name_to_node = dict([ (node_to_system_names[n],n) for n in node_to_system_names ])

    context = {
        "G":G,
        "node_to_system": node_to_system,
        "system_names_to_governments":system_names_to_governments,
        "node_to_system_names":node_to_system_names,
        "system_name_to_node":system_name_to_node,
        "system_names_to_system":system_names_to_system
    }
    
    return (G, node_to_system, context)

def get_intro_systems():
    intro = es.parse_endless_sky_file("data.orig/intro missions.txt")
    intro_missions = es.endless_type_grep(intro, "mission")
    sources = [ es.endless_first(x, "source")[1] for x in intro_missions ]
    dests   = [ es.endless_first(x, "destination")[1] for x in intro_missions ]
    intro_planets = list(set(sources + dests))
    intro_systems = [obj_to_system_name[planet] for planet in intro_planets]
    return intro_systems

def check_intro_connectivity(G, context):
    intro_systems = get_intro_systems()
    for system_i in intro_systems:
        src = context["system_name_to_node"][system_i]
        for system_j in intro_systems:
            dst = context["system_name_to_node"][system_j]
            if not nx.has_path(G, src, dst):
                print("No connectivity: %s %s" % (system_i, system_j))
                return False
    return True

def check_intro_distance(G, context, dist=15):
    intro_systems = get_intro_systems()
    for system_i in intro_systems:
        src = context["system_name_to_node"][system_i]
        for system_j in intro_systems:
            dst = context["system_name_to_node"][system_j]
            if nx.has_path(G, src, dst):
                if len(nx.shortest_path(G, source=src, target=dst)) > dist:
                    print("Path too long: %s %s" % (system_i, system_j))
                    return False
            else:
                return False
    return True

def move_system(system, x, y):
    system = es.endless_replace( system, 'pos', (x,y) )
    return system

def remove_links(system):
    return es.endless_delete_type(system, 'link')


invalid_graph = True
G = None
failures = 0
while invalid_graph:
    if G is None or failures % 10 == 0:
        print("Generating Graph!")
        G = generate_graph(n_systems)
    print("Populating Graph!")
    G, node_to_system, context = populate_graph(G, maps, systems)
    # now we want to ensure that intro missions are connected
    print("Checking graph!")
    failures += 1
    if check_intro_connectivity(G, context):
        if check_intro_distance(G, context, dist=20):
            invalid_graph = False
        else:
            print("Invalid Graph! Mission Systems too far away!")
    else:
        print("Invalid Graph! Mission Systems unreachable")
        

pos = nx.get_node_attributes(G, 'pos')
# now we make sure the systems link to who we configured
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

# now we replace the systems in the map
for k in node_to_system:
    system = node_to_system[k]
    es.endless_replace_entity(maps, system[0], system)
        
# write
out = es.serialize_entities(maps)
open("maps.txt.out", 'w').write(out)

system_names_to_governments = context["system_names_to_governments"]
node_to_system_names = context["node_to_system_names"]
# graph
node_to_govt = dict([(n, system_names_to_governments[ node_to_system_names[ n ] ]) for n in node_to_system_names])
graphit(G, govt=node_to_govt)
