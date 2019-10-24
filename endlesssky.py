def parse_endless_sky( filename ):
    return parse_endless_sky( file( filename ).read() )

def parse_endless_sky( data ):
    """ parse endless sky string """
    return None

if __name__ == "__main__":
    maps = parse_endless_sky_file("data.org/map.txt")
    planets = endless_type_grep(maps, "planet")
    earth = endless_name_grep(planets, "Earth")
    assert(endless_has(earth, "landscape"))
    assert(endless_has(earth, "description"))
    assert(endless_has(earth, "bribe"))
    assert(endless_has(earth, "required reputation"))
    earth = endless_replace( earth, "bribe", 0.1)
    bribe = endless_first(earth, "bribe")
    assert bribe == 0.1
