import larkendless as es
import random

start_system = 'Rutilicus'

maps = es.parse_endless_sky_file("data.orig/map.txt.original")
print(len(maps))
print(maps[1])
systems = es.endless_type_grep(maps, "system")
n_systems = len(systems)
width = 16
pw = 50
ph = 50

print(len(systems))
print(len(systems[0]))
print(len(systems[0][0]))

random.shuffle(systems)

def move_system(system, x, y):
    system = es.endless_replace( system, 'pos', (x,y) )
    return system

i = 0
for system in systems:
    x = i % width
    y = int(i / width)
    xp = (x * pw + int(0.2*x*pw/width))
    yp = (y * ph + int(0.3*y*ph/width))
    system = move_system(system, xp, yp)
    es.endless_replace_entity(maps, system[0], system)
    i += 1

systems = es.endless_type_grep(maps, "system")
#for system in systems:
#    print(system[0],es.endless_first(system,'pos'))

out = es.serialize_entities(maps)
open("maps.txt.out", 'w').write(out)
# print(out)
