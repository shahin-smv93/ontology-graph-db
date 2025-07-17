#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rdflib import Graph
from ontology_classes import Sensor, Gateway, BuildingSpace

def test_sensor_gateway():
    # Create a test graph
    g = Graph()
    
    # Bind namespaces for readable output
    from ontology_classes.namespaces import saref, ssn, dcterms, schema, s4bldg
    g.bind("saref", saref)
    g.bind("ssn", ssn)
    g.bind("dcterms", dcterms)
    g.bind("schema", schema)
    g.bind("s4bldg", s4bldg)
    
    # Create a test zone (BuildingSpace)
    zone = BuildingSpace(
        uri="http://concordia.ca/zone/test-zone",
        label="Test Zone"
    )
    
    # Create a test gateway
    gateway = Gateway(
        uri="http://concordia.ca/gateway/test-gateway",
        gatewayUID="BS231700182",
        label="Test Gateway"
    )
    
    # Create a test sensor
    sensor = Sensor(
        uri="http://concordia.ca/sensor/test-sensor",
        sensorUID="80930253DC1CA30139",
        sensorId="12489",
        vendorName="SchneiderElectric",
        installationDate="2025-01-01T00:00:00Z",
        gateway_connection=gateway,
        contained_in=zone
    )
    
    # Add everything to the graph
    zone.add_to_graph(g)
    gateway.add_to_graph(g)
    sensor.add_to_graph(g)
    
    # Print the Turtle output
    print("=== Test Sensor and Gateway RDF Output ===")
    print(g.serialize(format='turtle'))
    
    # Print summary
    print(f"\n=== Summary ===")
    print(f"Total triples: {len(g)}")
    print(f"Zone URI: {zone.uri}")
    print(f"Gateway URI: {gateway.uri}")
    print(f"Sensor URI: {sensor.uri}")

if __name__ == "__main__":
    test_sensor_gateway() 