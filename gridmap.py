#    Copyright (c) 2019 Abram Hindle, Michael Zahniser, Endless Sky Developers
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""gridmap.py -- Grid Map

This uses the more lowlevel API.

This was a first attempt at rewriting the maps.txt. It places everything into a random grid. It is quite random and not as fun as graph Map.

Essentially the systems are shuffled, their links are removed, and then they are placed into a grid and their links to their neighbors are replaced.
"""

import trulyendlesssky.larkendless as es
import random
import math

start_system = 'Rutilicus'

maps = es.parse_endless_sky_file("data.orig/map.txt.original")
print(len(maps))
print(maps[1])
systems = es.endless_type_grep(maps, "system")
n_systems = len(systems)
width = 16
pw = 75
ph = 75

print(len(systems))
print(len(systems[0]))
print(len(systems[0][0]))

random.shuffle(systems)

def move_system(system, x, y):
    system = es.endless_replace( system, 'pos', (x,y) )
    return system

def remove_links(system):
    return es.endless_delete_type(system, 'link')

mapping = dict()

i = 0
for system in systems:
    x = i % width
    y = math.floor(i / width)
    xp = x * pw
    yp = y * ph + int(pw * (x / width))
    system = move_system(system, xp, yp)
    system = remove_links( system )
    mapping[(x,y)] = system
    i += 1

# add links

for k in mapping:
    (x,y) = k
    s = mapping[k]
    for dir in [(-1,0),(0,-1),(1,0),(0,1)]:
        dp = (x + dir[0], y + dir[1])
        if dp in mapping:
            es.endless_add_property(s,('link', mapping[dp][0][1]))
    
# update the map
for k in mapping:
    system = mapping[k]
    es.endless_replace_entity(maps, system[0], system)

    
systems = es.endless_type_grep(maps, "system")
#for system in systems:
#    print(system[0],es.endless_first(system,'pos'))

out = es.serialize_entities(maps)
open("maps.txt.out", 'w').write(out)
# print(out)
