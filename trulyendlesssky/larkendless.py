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
"""EndlessSky parser

These are more low level routines for manipulating endless sky data.
They are very close to the data format.

"""

import sys

from lark import Lark, Transformer, v_args

endless_grammar = r"""
    COMMENT: /#[^\n]*/
    _NEWLINE: ( /\r?\n/ | COMMENT )+
    ?start: (_NEWLINE | object)*
    ?value: string
          | IDENTIFIER -> identifier
          | SIGNED_NUMBER -> number
    IDENTIFIER: /[^ "\r\n\t]+/
    _INDENT: "__INDENT__"
    _DEDENT: "__DEDENT__"
    ?name: IDENTIFIER -> identifier
         | string
    tuple  : name value* _NEWLINE 
    object : tuple _INDENT [ object | tuple | _NEWLINE ]*  _DEDENT
    string : ESCAPED_STRING | ESCAPED_STRING2
    ESCAPED_STRING2 : "`" _STRING_ESC_INNER "`"
    %import common._STRING_ESC_INNER
    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %import common.WORD
    %ignore /[\t \f]+/  // WS
    %ignore COMMENT
"""

class TreeToEndless(Transformer):
    """Helper to convert Lark output into Endless Sky list/tuples
    """
    
    def string(self, s):
        (s,) = s
        return s[1:-1]
    def number(self, n):
        (n,) = n
        sn = str(n)
        if '.' in sn or 'e' in sn or 'E' in sn:
            return float(n)
        else:
            return int(n)
    def identifier(self, s):
        (t,) = s
        return str(t)
    def tuple(self, s):
        key = s[0]
        v = None
        if len(s) > 1:
            v = s[1:]
            x = tuple(s)
        else:            
            x = (key,None)
        return x
    def object(self, o):
        return o
    def start(self, s):
        return list(s)


endless_parser = Lark(endless_grammar, parser='lalr', lexer='standard')
"""endless_parser is the parser that parses endless sky data
"""

def count_init_tabs(s):
    """count the beginning tabs
    """
    
    count = 0
    for c in s:
        if c != '\t':
            return count
        else:
            count += 1
    return count

def add_indent_dedent( text ):
    """adds indent and dedent tokens to a string
    """
    
    c = 0
    out = []
    for line in text.split("\n"):
        curr = count_init_tabs(line)
        prefix = ""
        if   curr == c + 1:
            prefix = " __INDENT__ "
        elif curr < c:
            prefix = " __DEDENT__ " * (c - curr)
        elif curr == c:
            None
        else:
            """ We shouldn't be here! """
            assert False
        c = curr
        out.append( prefix + line + "\n" )
    if c > 0:
        out.append(" __DEDENT__ " * c)        
    return "".join( out )

def parser( text ):
    """parse endless sky data text to tuple/lists
    """
    
    annotated_text = add_indent_dedent( text )
    tree = endless_parser.parse( annotated_text )
    transformed = TreeToEndless().transform( tree )
    return transformed

def get_name(x):
    """give an endless sky tuple return the name
    """
    
    if isinstance(x,list):
        return x[0][0]
    else:
        return x[0]

def get_value(x):
    """give an endless sky tuple return the value
    """

    if isinstance(x,list):
        return x[0][1]
    else:
        return x[1]
def get_properties(x):
    """give an endless sky object return the properties of it
    """

    if isinstance(x,list):
        return x[1:]
    return None

def mk_val(entity, val):
    """given an entity tuple and a value make a modify or make a new tuple

    tuples are immutable so there is some complication here
    """
    
    if isinstance(entity,list):
        entity[0][1] = val
        return entity
    else:
        if isinstance(val,tuple):
            return (entity[0], *val)
        return (entity[0], val)
    
def endless_type_grep(entities, stype):
    """given an endless sky list grep out objects of a type (like system or planet)
    """
    
    return [x for x in entities if get_name(x) == stype]

def flatten(l_o_l):
    """flatten a list of lists once
    """
    
    return [item for sublist in l_o_l for item in sublist]

def endless_recursive_type_grep(entities, stype):
    """recursive grep for endless type objects -- get sub objects too!
    """
    
    return flatten([endless_recursive_type_grep(x,stype) for x in entities if isinstance(x,list)]) + [x for x in entities if get_name(x) == stype]

def endless_name_grep(entities, name):
    """grep endless sky for named objects
    """
    
    return [x for x in entities if get_value(x) == name]

def endless_has(entity, entry):
    """does an endless sky object have a properties or entry 
    """
    
    return len(endless_type_grep(entity, entry)) > 0

def endless_replace(entity, prop, val):
    """given entity with first property prop replace its value with val! mutates! 
    """
    
    for i in range(0,len(entity)):
        if get_name(entity[i]) == prop:
            entity[i] = mk_val(entity[i], val)
            break
    return entity

def endless_delete_type(entity, prop):
    """makes a new endless sky object without all properties of type prop
    """
    
    return [x for x in entity if x[0] != prop]
    
def endless_first(entity, stype):
    """returns the first property to make type
    """
    
    return endless_type_grep(entity, stype)[0]

def endless_replace_entity(entities, entity_tuple, replacement_entity):
    """given entities replace entity_tuple with replacement_entity
    """
    
    for i in range(0, len(entities)):
        entity = entities[i]
        if isinstance(entity, list):
            if entity[0] == entity_tuple:
                entities[i] = replacement_entity
                return
    raise Exception("Could not find %s" % entity_tuple)

def endless_add_property(entity, t):
    """given an entity add a property tuple t
    """
    
    entity.append(t)
    return entity

def layout_value(val):
    """Convert an endless sky value to text
    """
    
    if val is None:
        return ''
    if isinstance(val,str):
        if '"' in val:
            return '`' + val + '`'
        elif ' ' in val:
            return '"' + val + '"'
        elif len(val) == 0:
            return '""'
        else:
            return val
    else:
        return layout_value( str(val) )
            

def layout_property(entity):
    """convert an endless sky property to text
    """
    
    if len(entity) == 1 or entity[1] is None:
        return layout_value(entity[0])
    else:
        try:
            return layout_value(entity[0])+" "+" ".join([layout_value(x) for x in entity[1:]])
        except Exception as e:
            print(entity)
            print(e)
            assert False

            
def indent(lines):
    """indent the lines by 1 tab
    """
    return ["\t" + line for line in lines]


def layout_entities(entities):
    '''given an endless sky entity list convert it to a list of strings'''
    if isinstance(entities, list):
        if len(entities) > 0 and isinstance(entities[0],list):
            assert "Inner List?"
        return [ layout_property(entities[0]) ] + indent(flatten([layout_entities(entity) for entity in entities[1:]]))
    else:
        return [ layout_property(entities) ]

def serialize_entities(entities):
    """convert a list of endless sky objects to a string
    """
    
    if (isinstance(entities, list) and len(entities) > 0 and isinstance(entities[0],list)):
        return "\n".join(["\n".join(layout_entities(entity)) for entity in entities])
    return "\n".join(layout_entities(entities))

def parse_endless_sky_file( filename ):
    """parse an endless sky file via the filename
    """
    return parser( open( filename ).read() )



rutilicus = '''
system Rutilicus
	pos -535 273
	government Republic
	habitable 625
	belt 1771
	link Arcturus
	link Cebalrai
	link Menkent
	link Holeb
	asteroids "small rock" 1 1.9188
	asteroids "medium rock" 10 1.9656
	asteroids "large rock" 1 2.0358
	asteroids "small metal" 13 1.4742
	asteroids "medium metal" 50 1.2168
	asteroids "large metal" 1 2.2932
	minables copper 7 2.11726
	minables lead 14 2.22127
	minables titanium 9 1.47159
	trade Clothing 224
	trade Electronics 838
	trade Equipment 560
	trade Food 335
	trade "Heavy Metals" 916
	trade Industrial 792
	trade "Luxury Goods" 1171
	trade Medical 590
	trade Metal 468
	trade Plastic 415
	fleet "Small Southern Merchants" 600
	fleet "Large Southern Merchants" 2000
	fleet "Small Militia" 6000
	fleet "Human Miners" 3000
	object
		sprite star/g5
		period 10
	object
		sprite planet/rock6
		distance 158.61
		period 31.9607
	object "New Boston"
		sprite planet/cloud6
		distance 513.86
		period 186.375
'''

alubs = '''
planet "Ablub's Invention"
	attributes arach factory
	landscape land/sky3
	description `This ancient and quiet world, orbiting a dim red sun, is home to the microchip foundries of House Idriss, the Arach guild that specializes in computers and advanced electronics. Outside of the cities, which are clustered around the equator, Ablub's Invention is uninhabited except by the native lifeforms, including strange, spindly-legged quadrupeds, awkward birds with leathery wings, and amphibians with webbed feet and long, whiskered snouts.`
	spaceport `The day-night cycle here is at least three times as long as any of the Coalition's species are habituated to, so the entire city enters a "false nighttime" in the middle of the day, shuttering all the windows so that the locals can rest and reset their biological clocks. And in the middle of the night, the city is brightly lit for a "false day."`
	spaceport `	The local work schedule has adapted to this unusual cycle, with the two true daytime periods serving the equivalent of the human work week, and the false daytime treated as a weekend, a time for socializing or working at home.`
	outfitter "Coalition Advanced"
	"required reputation" 25
'''

mission = '''
mission "Intro [0]"
	priority
	name "Passenger to <planet>"
	description "This old-timer captain offered to ride along with you to <destination>, and to give you some tips along the way."
	landing
	passengers 1
	source "New Boston"
	destination "New Greenland"
	
	on offer
		log "Finally scraped together enough money for a down payment on a starship. The interest on the mortgage is exorbitant."

'''

def test_driver():
    """This is the test suite
    """
    
    testd = "# yo how's it going\n\n" \
            "object\n__INDENT__" \
            "\tsprite star/g5\n" \
            "\tperiod 10\n" \
            "\tjustastring \"a string\"\n" \
            "\tobject\n__INDENT__" \
            "\t\tperiod 666\n__DEDENT__" \
            "\twhatever 555\n" \
            "\tobject\n__INDENT__"\
            "\t\tname \"whatever you want3\"\n" \
            "\tobject\n__INDENT__"\
            "\t\tname \"nested\"\n__DEDENT__ __DEDENT__" \
            "\tobject\n__INDENT__"\
            "\t\tname \"whatever you want\"\n__DEDENT__ " \
            "\tobject \"named object\"\n__INDENT__"\
            "\t\tname \"whatever you want\"\n__DEDENT__ " \
            "\tobject -6.66e20\n__INDENT__"\
            "\t\tname \"whatever you want\"\n__DEDENT__ " \
            " __DEDENT__ " \
            "galaxy Cirrus\n__INDENT__ " \
            "\twidth 1024\n__DEDENT__"
    tree = endless_parser.parse( testd )
    transformed = TreeToEndless().transform( tree )
    assert len(transformed) == 2
    intree = "object\n\tnested value\n\tnested value2\n"
    outtree = "object\n __INDENT__ \tnested value\n\tnested value2\n __DEDENT__ \n"
    x = add_indent_dedent( intree )
    assert x.strip() == outtree.strip()

    intree = "object\n\tnested value\n\t\tnested value2\n"
    outtree = "object\n __INDENT__ \tnested value\n __INDENT__ \t\tnested value2\n __DEDENT__  __DEDENT__ \n"
    x = add_indent_dedent( intree )
    assert x.strip() == outtree.strip()


    
    testd = "object\n" \
            "\tsprite star/g5\n" \
            "\tperiod 10\n"    
    objs = parser(testd)
    #d = objs[0]
    #assert d[0] == ('object',None)
    rut = parser( rutilicus )
    assert rut[0] == ('system', 'Rutilicus')
    robjs = endless_type_grep(rut,"object")
    assert len(robjs) == 3
    o = endless_first(rut, "object")
    assert o[0][0] == 'object'
    assert o[0][1] is None
    rpos = endless_type_grep(rut, 'pos')[0]
    assert rpos  == ('pos', -535, 273)

    maps = parse_endless_sky_file("data.orig/map.txt.original")
    planets = endless_type_grep(maps, "planet")
    assert(len(planets) > 0)
    earth = endless_name_grep(planets, "Earth")[0]
    assert(endless_has(earth, "landscape"))
    assert(endless_has(earth, "description"))
    assert(endless_has(earth, "bribe"))
    assert(endless_has(earth, 'required reputation'))
    earth = endless_replace( earth, "bribe", 0.1)
    bribe = endless_first(earth, "bribe")
    assert bribe[1] == 0.1

    rut2 = endless_name_grep(maps, "Rutilicus")[0]
    rpos2 = endless_type_grep(rut, 'pos')[0]
    assert rpos == rpos2
    
    objs = parser(testd)
    testd2 = serialize_entities(objs)
    assert testd.strip() == testd2.strip()
    # print(serialize_entities(maps))
    assert layout_property(('pos', 0, 0)) == 'pos 0 0'
    galaxy = [('galaxy', 'Milky Way'), ('pos', 0, 0), ('sprite', 'ui/galaxy')]
    oot = "galaxy \"Milky Way\"\n\tpos 0 0\n\tsprite ui/galaxy"
    assert serialize_entities(galaxy) == oot
    coolplace = [('cool place','fun town'), ('description','""""')]
    coot = '"cool place" "fun town"\n\tdescription `""""`'
    assert serialize_entities(coolplace) == coot
    assert '`' in serialize_entities(coolplace)
    alubs_parse = parser(alubs)
    sp = endless_first(alubs_parse, "spaceport")
    assert '"' in sp[1]
    x = layout_value(sp[1])
    assert '`' in x
    alubs_out = serialize_entities(alubs_parse)
    assert '`' in alubs_out
    delsys = [('system', 'Whatevs'),('link', 'coolbears'),('cool','awesome'),('link','what')]
    delsys2 = endless_delete_type( delsys, 'link')
    assert delsys2 != delsys
    assert not endless_has(delsys2, "link")
    missions = parser(mission)
    x = endless_first(missions, "source")[1]
    assert x == "New Boston"
    
if __name__ == "__main__":
    test_driver()
