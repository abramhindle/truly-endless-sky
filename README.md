# Truly Endless Sky
 
Truly Endless Sky, helpers to aide in procedural generation of game content for the game "Endless Sky".

The class `trulyendlesssky.EndlessSky` can parse Endless Sky data files like maps.txt and produce a list based output. The class can also maintain state and modify the map data.

# Motivation

I wanted to make endless sky a procedural game without changing the game engine itself. The challenge was manipulating the strange data format they use where they rely on tab based hierarchical trees.

# License

Unless otherwise specified:

GPL3 (c) 2019 Abram Hindle & Michael Zahniser & Endless Sky Developers

# Installation

```
pip3 install --user git+https://github.com/abramhindle/truly-endless-sky.git@more-priate
```

# Requirements:

* python3.6+
* scipy
* forceatlas2
* networkx
* matplotlib
* lark-parser

# Usage

Draw a graph of the system locations in space.

```
import trulyendlesssky as endlesssky
import networkx as nx
import matplotlib.pyplot as plt

eso = endlesssky.EndlessSky()
# place the map.txt in the same folder
eso.load_object_file(filename="map.txt")
n_systems = eso.n_systems()

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


G = extract_original_graph(eso)
govts = nx.get_node_attributes(G, 'govt')
graphit(G, govt=govts)
```
