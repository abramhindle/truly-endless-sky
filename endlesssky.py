import re

def parse_endless_sky_file( filename ):
    return parse_endless_sky( open( filename ).read() )

def parse_endless_sky( data ):
    """ parse endless sky string """
    lines = data.split('\n')
    entities = []
    while( len(lines) > 0 ):
        line = lines[0]
        if len(line) > 0 and line[0] == '#':
            """ignore"""
            lines = lines[1:]
        elif len(line) > 0 and line[0] == '\t':
            """ No don't get here """
            assert False
        elif len(line) > 0 and ord(line[0]) > 0:
            entity, remaining_lines = parse_entity(line,lines[1:],depth=0)
            entities.append(entity)
            lines = remaining_lines
        elif len(line) == 0:
            """ do nothing """
            lines = lines[1:]
        else:
            """ Uh oh """
            assert False            
    return entities

property_re = r'\t*("[^"]*"|[^"\s]*)\s("[^"]*"|`[^`]*`|[^" ]*)'

def parse_tuple(line):
    m = re.match( property_re , line )
    if not m:
        """ Couldn't parse """
        assert False
    ekey   = m.group(1)
    evalue = m.group(2)
    return (ekey, evalue)

def count_init_tabs(s):
    count = 0
    for c in s:
        if c != '\t':
            return count
        else:
            count += 1
    return count

def parse_entity(line,lines,depth=0):
    ek, ev = parse_tuple(line)
    lines = lines[1:]
    tabs = "\t"*(depth+1)
    entity = [(ek,ev)]
    while( len(lines) > 0 ):
        c = count_init_tabs(lines[0])
        if c == depth+2:
            sentity, rlines = parse_entity(line,lines,depth=depth+1)
            entity[-1] = sentity # replace the old one
            lines = rlines
            line = None
        elif c == depth+1:
            """ parse a property """
            sentity = parse_tuple(lines[0])
            entity.append(sentity)
            line = lines[0]
            lines = lines[1:]
        elif c <= depth:
            return (entity, lines)
    return (entity, lines)

def get_name(x):
    if isinstance(x,list):
        return x[0][0]
    else:
        return x[0]

def get_value(x):
    if isinstance(x,list):
        return x[0][1]
    else:
        return x[1]
def get_properties(x):
    if isinstance(x,list):
        return x[1:]
    return None

def mk_val(entity, val):
    if isinstance(entity,list):
        entity[0][1] = val
        return entity
    else:
        return (entity[0], val)
    
def endless_type_grep(entities, stype):
    return [x for x in entities if get_name(x) == stype]

def endless_name_grep(entities, name):
    return [x for x in entities if get_value(x) == name]

def endless_has(entity, entry):
    return len(endless_type_grep(entity, entry)) > 0

def endless_replace(entity, prop, val):
    """ mutates! """
    for i in range(0,len(entity)):
        if get_name(entity[i]) == prop:
            entity[i] = mk_val(entity[i], val)
            break
    return entity

def endless_first(entity, stype):
    return endless_type_grep(entity, stype)[0]

def test_driver():
    maps = parse_endless_sky_file("data.orig/map.txt")
    planets = endless_type_grep(maps, "planet")
    assert(len(planets) > 0)
    earth = endless_name_grep(planets, "Earth")[0]
    assert(endless_has(earth, "landscape"))
    assert(endless_has(earth, "description"))
    assert(endless_has(earth, "bribe"))
    assert(endless_has(earth, '"required reputation"'))
    earth = endless_replace( earth, "bribe", 0.1)
    bribe = endless_first(earth, "bribe")
    assert bribe[1] == 0.1

if __name__ == "__main__":
    test_driver()
