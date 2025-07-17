import json
import os
import sys
from rdflib import Graph, URIRef

# Add the parent directory to the path to import ontology_classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_classes import (
    Building, Address, BuildingSpace, PhysicalObject, 
    Sensor, Gateway, Measurement, TimeInterval,
    get_feature_of_interest
)

def build_time_interval(time_interval_str):
    """Build TimeInterval object from time interval string"""
    if not time_interval_str:
        return None
    
    # Create URI for time interval
    time_interval_uri = f"http://example.com/timeInterval/{time_interval_str}"
    return TimeInterval(
        uri=time_interval_uri,
        time_interval=float(time_interval_str) if time_interval_str else None
    )

def build_measurement(measurement_dict, sensor_uri):
    """Build Measurement object from measurement dictionary"""
    if not measurement_dict:
        return None
    
    # Create measurement URI if not provided
    measurement_uri = measurement_dict.get("uri")
    if not measurement_uri:
        measurement_uri = f"{sensor_uri}_measurement"
    
    # Get feature of interest from sensor type
    sensor_type = measurement_dict.get("sensor_type")
    measured_property = measurement_dict.get("measured_property")
    if measured_property and not isinstance(measured_property, URIRef):
        measured_property = URIRef(measured_property)
    elif not measured_property and sensor_type:
        measured_property = get_feature_of_interest(sensor_type)
        if measured_property and not isinstance(measured_property, URIRef):
            measured_property = URIRef(measured_property)
    
    # Build time interval if available
    time_interval = None
    if "time_interval" in measurement_dict:
        time_interval = build_time_interval(measurement_dict["time_interval"])
    
    return Measurement(
        uri=measurement_uri,
        time_interval=time_interval,
        measured_property=measured_property,
        unit=measurement_dict.get("unit"),
        sensor_type=sensor_type
    )

def build_sensor(sensor_dict, parent=None):
    """Build Sensor object from sensor dictionary"""
    sensor = Sensor(
        uri=sensor_dict["uri"],
        sensorUID=sensor_dict.get("sensorUID"),
        sensorId=sensor_dict.get("sensorId"),
        vendorName=sensor_dict.get("vendorName"),
        installationDate=sensor_dict.get("installationDate"),
        contained_in=parent
    )
    
    # Build measurement if present
    if "measurement" in sensor_dict:
        measurement = build_measurement(sensor_dict["measurement"], sensor_dict["uri"])
        sensor.has_measurement = measurement
    
    return sensor

def build_gateway(gateway_dict, parent=None):
    """Build Gateway object from gateway dictionary"""
    return Gateway(
        uri=gateway_dict["uri"],
        gatewayUID=gateway_dict.get("gatewayUID"),
        label=gateway_dict.get("label"),
        contained_in=parent
    )

def build_physical_object(obj_dict, parent=None):
    """Build PhysicalObject (desk) with nested sensors"""
    obj = PhysicalObject(
        uri=obj_dict["uri"],
        label=obj_dict.get("label"),
        contained_in=parent
    )
    
    # Attach deskDescription if present
    if "deskDescription" in obj_dict:
        obj.deskDescription = obj_dict["deskDescription"]
    
    # Handle nested sensors in desks
    if "contains" in obj_dict:
        for sensor_dict in obj_dict["contains"]:
            sensor = build_sensor(sensor_dict, parent=obj)
            obj.contains.append(sensor)
    
    return obj

def build_building_space(space_dict, parent=None, building=None):
    """Build BuildingSpace with support for sensors and measurements"""
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
    
    # Add building objects (desks, sensors, and gateways)
    for obj_dict in space_dict.get("building_object", []):
        # Check if it's a sensor (has sensorType)
        if "sensorType" in obj_dict:
            # It's a sensor
            sensor = build_sensor(obj_dict, parent=space)
            space.building_object.append(sensor)
        # Check if it's a gateway (has gatewayUID)
        elif "gatewayUID" in obj_dict:
            # It's a gateway
            gateway = build_gateway(obj_dict, parent=space)
            space.building_object.append(gateway)
        else:
            # It's a desk or other physical object
            obj = build_physical_object(obj_dict, parent=space)
            space.building_object.append(obj)
    
    return space

def build_address_lookup(addresses_list):
    """Build address lookup dictionary"""
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
    """Build Building with all nested spaces and objects"""
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
    """Create RDF graph from the complete hierarchical data structure"""
    g = Graph()
    
    # Bind all ontology prefixes for readable Turtle output
    from ontology_classes.namespaces import (
        s4bldg, vcard, saref, ssn, dcterms, schema, 
        time, s4watr, qudt, bigg
    )
    from rdflib.namespace import RDFS, RDF
    
    g.bind("s4bldg", s4bldg)
    g.bind("vcard", vcard)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("saref", saref)
    g.bind("ssn", ssn)
    g.bind("dcterms", dcterms)
    g.bind("schema", schema)
    g.bind("time", time)
    g.bind("s4watr", s4watr)
    g.bind("qudt", qudt)
    g.bind("bigg", bigg)
    
    address_lookup = build_address_lookup(transformed_data["addresses"])
    buildings = []
    
    for building_dict in transformed_data["buildings"]:
        building = build_building(building_dict, address_lookup)
        buildings.append(building)
    
    for building in buildings:
        building.add_to_graph(g)
    
    return g

def test_full_ont_mapping():
    """Test function for full ontology mapping with sensors and measurements"""
    try:
        # Load the enhanced hierarchical transformed data
        print("Loading enhanced_transformed_data.json...")
        with open("enhanced_transformed_data.json", "r") as f:
            transformed_data = json.load(f)
        
        if not transformed_data['buildings'] and not transformed_data['addresses']:
            print("No data to process")
            return
        
        print(f"Loaded {len(transformed_data['buildings'])} buildings and {len(transformed_data['addresses'])} addresses")
        
        print("Creating RDF graph from enhanced hierarchy...")
        rdf_graph = create_rdf_graph_from_hierarchy(transformed_data)
        
        if len(rdf_graph) == 0:
            print("WARNING: RDF graph is empty! Check your ontology classes and data structure.")
            return
        
        # Write Turtle to file for debugging
        turtle_data = rdf_graph.serialize(format='turtle')
        with open("test_full_debug_output.ttl", "w") as f:
            f.write(turtle_data)
        
        print(f"RDF graph created successfully!")
        print(f"- RDF graph contains {len(rdf_graph)} triples")
        print(f"- Turtle file saved as test_full_debug_output.ttl")
        
        # Test for time interval relationships
        print("\nTesting for time interval relationships...")
        time_interval_triples = list(rdf_graph.triples((None, None, None)))
        time_interval_count = 0
        for s, p, o in time_interval_triples:
            if "timeInterval" in str(s) or "timeInterval" in str(o):
                time_interval_count += 1
                print(f"Time interval triple: {s} {p} {o}")
        
        print(f"Found {time_interval_count} time interval related triples")
        
        # Test for measurement relationships
        print("\nTesting for measurement relationships...")
        measurement_triples = list(rdf_graph.triples((None, None, None)))
        measurement_count = 0
        for s, p, o in measurement_triples:
            if "measurement" in str(s) or "measurement" in str(o):
                measurement_count += 1
                if measurement_count <= 10:  # Show first 10
                    print(f"Measurement triple: {s} {p} {o}")
        
        print(f"Found {measurement_count} measurement related triples")
        
    except Exception as e:
        print(f"Error in test full ontology mapping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_ont_mapping() 