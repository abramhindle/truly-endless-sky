import re
import larkendless as es
import copy

def es_name(obj):
    return obj[0][1]

def es_rename(obj,name):
    obj[0][1] = name

class EndlessSky:
    def __init__(self):
        None
    def load_object_file(self, filename="data.orig/map.txt.original"):
        self.maps = es.parse_endless_sky_file( filename )
    def load_maps( self, maps ):
        self.maps = maps
    def systems(self):
        systems = es.endless_type_grep(self.maps, "system")
        self._systems = systems
        return systems    
    def n_systems(self):
        return len(self.systems())
    def system_names(self):
        systems = self.systems()
        system_names = [system[0][1] for system in systems]
        self._system_names = system_names
        return system_names    
    def system_map(self):
        systems = self.systems()
        system_map= dict([system[0][1],system  for system in systems])
        return system_map
    def get_system_by_name(self, name):
        return self.system_map()[name]
    def is_system_name(self,name):
        return name in self.systems_names()
    def governments(self):
        systems = self.systems()
        governments = [es.endless_first(system, "government")[1] for system in systems]
        self._governments
        return governments
    def system_names_to_governments(self):
        governments = self.governments()
        system_names = self.system_names()
        system_names_to_governments = dict(zip(system_names, governments))
        self._system_names_to_governments = system_names_to_governments
        return system_names_to_governments
    def government_of_system_name(self, name):
        return self.system_names_to_governments()[name]
    def planets(self):
        planets = es.endless_type_grep(self.maps, "planet")
        return planets
    def add_system(self, system):
        self.maps.append(system)
    def _sys_name_renamer(self, name):
        """ generate a name for the system """
        for i in range(1,1000):
            name = x + " " + str(i)
            if not self.is_system_name(name)
                return name
        raise Exception( "Couldn't name system: %s" % name )
    def _planet_name_renamer(self, name):
        """ generate a name for the system """
        for i in range(1,1000):
            name = x + " " + str(i)
            if not self.is_planet_name(name)
                return name
        raise Exception( "Couldn't name system: %s" % name )
    def planets_of_system_object(self, system):                
        objects = endless_recursive_type_grep( system, "object")
        planets = [o for o in objects if not es_name(o) is None and if len(es_name(o)) > 0]
        return planets
    def add_system_with_rename(self, system, sys_name_renamer=None, planet_name_renamer=None):
        if sys_name_renamer is None:
            sys_name_renamer = self._sys_name_renamer
        if planet_name_renamer is None:
            planet_name_renamer = self.planet_name_renamer
        sys_name = sys_name_renamer(es_name(system))
        es_rename( system, sys_name )
        already_used_the_name = {}
        for planet in self.planets_of_system_object(system):
            oname = es_name(planet)
            pname = planet_name_renamer( oname )
            if pname in already_used_the_name:
                raise Exception("We already used the name %s" % pname)
            es_rename(planet, pname)
            # this changes top level planetes
            self.duplicate_and_rename_planet(fromname=oname, toname=pname)
        self.add_system( system )

    def duplicate_and_rename_system(self, system_name,sys_name_renamer=None, planet_name_renamer=None):
        system = self.get_system_by_name( system_name )
        add_system_with_rename( system, sys_name_renamer, planet_name_renamer)
        
    def planet_names(self):
        planets = self.planets()
        planet_names = [planet[0][1] for planet in planets]
        self._planet_names = planet_names
        return planet_names                
    def planet_map(self):
        planets = self.planets()
        planet_map= dict([planet[0][1],planet  for planet in planets])
        return planet_map
    def get_planet_by_name(self, name):
        return self.planet_map()[name]
    def get_planet_by_name(self, name):
        return self.planet_names()
    def duplicate_and_rename_planet(self, fromname=None, toname=None ):
        planet = self.get_planet_by_name( fromname )
        planet = copy.deepcopy( planet )
        es_rename( planet, toname )
        self.add_planet( planet )
    def add_planet( self, planet ):
        self.maps.append( planet )
    
        
    

def test_driver():
    
if __name__ == "__main__":
    test_driver()
