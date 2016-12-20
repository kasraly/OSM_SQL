# -*- coding: utf-8 -*-
"""
Created on Tue Dec 06 20:59:17 2016

@author: Kasra
"""

"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "edmonton_sample.osm"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
road_num_re = re.compile(r'[0-9]+[a-zA-Z]?\.?$')
house_num_re = re.compile(r'[0-9]+[a-zA-Z]?$')

expected_type = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Point", "Way", "Wynd", "Vista", "Terrace", "Hill", "Villas", 
            "View", "Village", "Run", "Promenade", "Loop", "Link", "Landing", "Key", "Highway", "Heights",
            "Heath", "Green", "Gate", "Freeway", "Crescent", "End", "Estate", "Gardens", "Common", "Row", 
            "Park", "Parade", "Ridge", "Cove", "Close", "Circle", "Bend", "Bay"]
expected_position = ["North-west", "South-west", "North-east", "South-east", "North", "South", "East", "West"]

# UPDATE THIS VARIABLE
mapping_position = {"W": "West",
                    "SW": "South-west",
                    "Northwest": "North-west",
                    "North-West": "North-west",
                    "NW": "North-west",
                    "NE": "North-east"}
mapping_type = { "St": "Street",
            "St.": "Street",
            "ST": "Street",
            "Rd.": "Road",
            "Rd": "Road",
            "Ave": "Avenue",
            "ave": "Avenue",
            "Ave.": "Avenue",
            "Villa": "Villas",
            "street": "Street",
            "road": "Road",
            "avenue": "Avenue",
            "Pointe": "Point",
            "Dr": "Drive",
            "Dr.": "Drive",
            "Crest": "Crescent",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard"}


def audit_street_type(street_types, street_name):
    street_name, street_type, _ = update_name(street_name)
    if street_type not in expected_type:
        street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)

    
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
#                if tag.attrib['k'] == 'is_in':
#                    city, province, country = parse_isin(tag.attrib['v'])
#                    print tag.attrib['k'], tag.attrib['v']
#                    print city, province, country
#                break
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    osm_file.close()
    return street_types

postcode_re = re.compile(r'[A-Z][0-9][A-Z]\s?[0-9][A-Z][0-9]', re.IGNORECASE)
def update_postcode(code):
    if postcode_re.match(code):
        if code[3] == ' ':
            return code.upper()
        else:
            return code[:3].upper() + ' ' + code[3:6].upper()
    else:
        return code

def parse_isin(name):
    address = name.split(',')
    if len(address) == 3 and address[2] == 'Canada':
        return address[0], address[1], address[2]
    elif len(address) == 2 and address[1] == 'Alberta':
        return address[0], address[1], None
    elif len(address) >= 3 and address[1] == ' County of':
        city = address[0].split()
        if len(address) == 3:
            return city[0], address[2], None       
        elif len(address) == 4:
            return city[0], address[2], address[3]
    elif len(address) == 1 and address[0] != 'Alberta':
        return address[0], None, None      
    return None, None, None
    
def update_name(name):

    # YOUR CODE HERE
    house_num = None
    street_type = None
    m = name.split()
    if road_num_re.search(m[-1]) and len(m) >= 2: # if last word is road number and more than two words
        street_type = m[-2] #check the second last word 
        if street_type in expected_type:
            if house_num_re.search(m[0]): # if the first word is house number 
                house_num = m[0]
                m = m[1:] # remove the house number from street name
        else:
            if street_type in mapping_type: # if street type can be improved 
                m[-2] = mapping_type[street_type] #update the second last word
    elif m[-1] in expected_position or m[-1] in mapping_position: #if last word is position or from postion mapping dictionary
        if m[-1] in mapping_position: 
            m[-1] = mapping_position[m[-1]]
        street_type = m[-2] #check the second last word
        if street_type in mapping_type:
            m[-2] = mapping_type[street_type] #update the second last word
    else: # otherwise last word is street type
        street_type = m[-1]
        if street_type in mapping_type:
            m[-1] = mapping_type[street_type]
    
    return ' '.join(m), street_type, house_num


def test():
    st_types = audit(OSMFILE)
#    for entry in st_types:
#        print entry + '|' + str(len(st_types[entry]))
    pprint.pprint(dict(st_types))
    
    return
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name)
            print name, "=>", better_name
 

if __name__ == '__main__':
    test()