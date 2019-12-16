# Truly Endless Sky
 
Truly Endless Sky, helpers to aide in procedural generation of game content for the game "Endless Sky". Essentially this provides utilities for generating endless sky map data.

The class `trulyendlesssky.EndlessSky` can parse Endless Sky data files like maps.txt and produce a list based output. The class can also maintain state and modify the map data.

Endless Sky is an awesome game by Michael Zahniser et al. You can get it from here: https://github.com/endless-sky/endless-sky/releases/tag/v0.9.10

## Uses

* Parse endless sky data files
* Regenerate endless sky data files
* Move and manipulate star systems in Endless sky
* Aide in procedural generation of Endless sky content
* Make new maps

# Motivation

When I first got Endless Sky I thought the "Endless" part implied procedural generation. I learned later after hours of gameplay that the world was itself quite fixed and not as dynamic as I had hoped. It is very well detailed and very well crafted.

Thus I wanted to use procedural generation with Endless Sky. I wanted to make endless sky a procedural game without changing the game engine itself. The challenge was manipulating the strange data format they use where they rely on tab based hierarchical trees. After hacking a hand parser together I found it insufficient to fully parse the files so I switched to a general purpose LALR parser instead. That worked fine after I added some indent and dedent tokens.


# License

Unless otherwise specified:

GPL3 (c) 2019 Abram Hindle & Michael Zahniser & Endless Sky Developers

# Installation

```
pip3 install --user git+https://github.com/abramhindle/truly-endless-sky.git@master
```

# Requirements:

* python3.6+
* scipy
* forceatlas2
* networkx
* matplotlib
* lark-parser

* Endless Sky https://github.com/endless-sky/endless-sky/releases/tag/v0.9.10

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

# Examples

Note these will corrupt your save files. Make backups!

## pirate-ring.py -- The Pirate Ring

This uses the high-level API.

Pirate Ring is my imaginary endless sky world where the base game stays the same but the pirates have found a larger area to inhabit in the outer rim. The outer rim has very long distances and fully inhabited by the impoverished pirates.

This builds a ring of systems around the current map, with a few connections connecting back. The systems in the ring are all pirate systems. We clone existing pirate systems within the ring.

Connectivity is checked and guaranteed.

## ring.py -- The Pirate Ring improved with an alternative layout

This uses the high-level API.

This is the old pirate ring but the hops are lot shorter and more
manageable. This was mostly exploring alternative methods of layout.

## graph-map.py -- Graph Map

This uses the more lowlevel API.

Using graph layout algorithms rearrange the graph of systems into a new dangerous maps. Very unsafe for new players, but good for loading up an old save with a powerful fleet and be ready for a surprise.

This Graph Map was a lazy attempt at getting a useful map demo out of endless sky. It is vibrant and difficult and too random. Works well on existing save files.

Connectivity is guaranteed.

## gridmap.py -- Grid Map

This uses the more lowlevel API.

This was a first attempt at rewriting the maps.txt. It places everything into a random grid. It is quite random and not as fun as graph Map.

Essentially the systems are shuffled, their links are removed, and then they are placed into a grid and their links to their neighbors are replaced.


# Tests

The mains of the library will run the tests for that module.

```
python3 -m trulyendlesssky.endlesssky
python3 -m trulyendlesssky.larkendless
```

# TODOs

* Try to make sure comments are maintained ? Don't lose copyright notices.
* [X] Python docstrings https://realpython.com/documenting-python-code/
* Re-architect with objects for manipulation
