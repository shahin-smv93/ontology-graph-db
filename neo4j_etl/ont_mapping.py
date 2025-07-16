import json
import os
from rdflib import Graph
from ontology_classes import Building, Address, BuildingSpace, PhysicalObject
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def build_physical_object(obj_dict, parent=None):
    obj = PhysicalObject(
        uri=obj_dict["uri"],
        label=obj_dict.get("label"),
        contained_in=parent
    )
    # Attach deskDescription if present
    if "deskDescription" in obj_dict:
        obj.deskDescription = obj_dict["deskDescription"]
    # If you have nested objects in the future, handle here
    return obj

def build_building_space(space_dict, parent=None, building=None):
    # Only set .building for top-level spaces (floors)
    is_top_level = parent is None and building is not None
    space = BuildingSpace(
        uri=space_dict["uri"],
        label=space_dict.get("label"),
        parent_space=parent,
        building=building if is_top_level else None,
        spaces=[],
        building_object=[]
    )
    # Recursively add child spaces
    for child_space_dict in space_dict.get("spaces", []):
        child_space = build_building_space(child_space_dict, parent=space, building=building)
        space.spaces.append(child_space)
    # Add building objects (desks)
    for obj_dict in space_dict.get("building_object", []):
        obj = build_physical_object(obj_dict, parent=space)
        space.building_object.append(obj)
    return space

def build_address_lookup(addresses_list):
    lookup = {}
    for a in addresses_list:
        lookup[a["uri"]] = Address(
            uri=a["uri"],
            street_name=a.get("street_name"),
            street_number=a.get("street_number"),
            postal_code=a.get("postal_code")
        )
    return lookup

def build_building(building_dict, address_lookup):
    building = Building(
        uri=building_dict["uri"],
        label=building_dict.get("label"),
        address=address_lookup.get(building_dict.get("address_uri")),
        spaces=[]
    )
    for floor_dict in building_dict.get("spaces", []):
        floor = build_building_space(floor_dict, building=building)
        building.spaces.append(floor)
    return building

def create_rdf_graph_from_hierarchy(transformed_data):
    g = Graph()
    # Bind ontology prefixes for readable Turtle output
    from ontology_classes.namespaces import s4bldg, vcard
    from rdflib.namespace import RDFS
    g.bind("s4bldg", s4bldg)
    g.bind("vcard", vcard)
    g.bind("rdfs", RDFS)
    address_lookup = build_address_lookup(transformed_data["addresses"])
    buildings = []
    for building_dict in transformed_data["buildings"]:
        building = build_building(building_dict, address_lookup)
        buildings.append(building)
    for building in buildings:
        building.add_to_graph(g)
    return g

def load_rdf_to_neo4j(rdf_graph, neo4j_uri, username, password):
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        with driver.session() as session:
            # Write Turtle to file for debugging
            turtle_data = rdf_graph.serialize(format='turtle')
            with open("debug_output.ttl", "w") as f:
                f.write(turtle_data)
        #    print(f"Turtle RDF written to debug_output.ttl ({len(turtle_data)} characters)")
            
            # Print a sample of the Turtle data (first 500 chars)
        #    print("\n===== Sample of Turtle RDF (first 500 chars) =====\n")
        #    print(turtle_data[:500] + "..." if len(turtle_data) > 500 else turtle_data)
        #    print("\n===================================================\n")
            
            load_query = "CALL n10s.rdf.import.inline($turtle_data, 'Turtle')"
            result = session.run(load_query, turtle_data=turtle_data)
        #    logging.info("RDF data loaded into Neo4j successfully")
    except Exception as e:
        #logging.error(f"Error loading RDF data into Neo4j: {e}")
        raise
    finally:
        driver.close()

def ont_mapping():
    env_neo4j = os.getenv('NEO4J_AUTH')
    if not env_neo4j:
        raise ValueError("NEO4J_AUTH is not defined in the env file")
    username, password = env_neo4j.split('/')
    neo4j_uri = 'bolt://localhost:7687'
    try:
        # Load the hierarchical transformed data
        #print("Loading transformed_data.json...")
        with open("transformed_data.json", "r") as f:
            transformed_data = json.load(f)
        
        if not transformed_data['buildings'] and not transformed_data['addresses']:
            #logging.warning("No data to process")
            return
        
        #print(f"Loaded {len(transformed_data['buildings'])} buildings and {len(transformed_data['addresses'])} addresses")
        
        logging.info("Creating RDF graph from hierarchy...")
        rdf_graph = create_rdf_graph_from_hierarchy(transformed_data)
        
        if len(rdf_graph) == 0:
            #print("WARNING: RDF graph is empty! Check your ontology classes and data structure.")
            return
        
       # logging.info("Loading RDF data into Neo4j...")
        load_rdf_to_neo4j(rdf_graph, neo4j_uri, username, password)
      #  logging.info("Ontology mapping completed successfully!")
        
        # Print summary for verification
        #print(f"\nSummary:")
        #print(f"- RDF graph contains {len(rdf_graph)} triples")
        #print(f"- Turtle file saved as debug_output.ttl")
        #print(f"- Check Neo4j browser for imported data")
        
    except Exception as e:
        #logging.error(f"Error in ontology mapping: {e}")
        raise

if __name__ == "__main__":
    ont_mapping() 