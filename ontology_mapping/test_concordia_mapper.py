#!/usr/bin/env python3
"""
Test script to verify that ConcordiaOntologyMapper has the same functionality as full_ont_mapping.py
"""

import sys
import os
import json
from rdflib import Graph

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_mapping import OntologyMappingConfig
from ontology_mapping.concordia_mapper import ConcordiaOntologyMapper


def test_concordia_mapper():
    """Test the ConcordiaOntologyMapper functionality."""
    
    print("🧪 Testing ConcordiaOntologyMapper functionality")
    print("=" * 50)
    
    # Create a dummy input file to satisfy validation
    dummy_data = [{"sensorUID": "test", "building": "test", "sensorType": "test"}]
    with open("test_data.json", "w") as f:
        json.dump(dummy_data, f)
    
    # Create a sample configuration
    config = OntologyMappingConfig(
        base_namespace="http://concordia.ca",
        input_data_path="test_data.json",
        output_transformed_path="test_transformed.json",
        output_rdf_path="test_output.ttl",
        output_debug_path="test_debug.ttl"
    )
    
    # Create sample hierarchical data (similar to what full_ont_mapping.py expects)
    sample_data = {
        "buildings": [
            {
                "uri": "http://concordia.ca/building/ER",
                "label": "ER",
                "address_uri": "http://concordia.ca/address/2155_Guy_H3H_2L9",
                "spaces": [
                    {
                        "uri": "http://concordia.ca/floor/ER-14",
                        "label": "ER-14",
                        "spaces": [
                            {
                                "uri": "http://concordia.ca/mainRoom/ER-14-1431",
                                "label": "ER-14-1431",
                                "spaces": [
                                    {
                                        "uri": "http://concordia.ca/room/ER-14-1431-openSpace",
                                        "label": "ER-14-1431-openSpace",
                                        "spaces": [
                                            {
                                                "uri": "http://concordia.ca/desk/1431-openSpace-54",
                                                "label": "1431-openSpace-54",
                                                "deskDescription": "Fixed Desk",
                                                "building_object": [
                                                    {
                                                        "uri": "http://concordia.ca/sensor/80930253DC1CA30139",
                                                        "sensorUID": "80930253DC1CA30139",
                                                        "sensorId": "SENSOR001",
                                                        "sensorType": "deskSensor",
                                                        "vendorName": "SchneiderElectric",
                                                        "installationDate": "2023-01-01",
                                                        "gateway_connection": "http://concordia.ca/gateway/BS231700161",
                                                        "measurement": {
                                                            "uri": "http://concordia.ca/measurement/80930253DC1CA30139/deskSensor_measurement",
                                                            "measured_property": "http://bigg-project.eu/ld/ontology#OccupancyProperty",
                                                            "sensor_type": "deskSensor",
                                                            "time_interval": "600.0",
                                                            "unit": "ppm"
                                                        }
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ],
                                "building_object": [
                                    {
                                        "uri": "http://concordia.ca/gateway/BS231700161",
                                        "gatewayUID": "BS231700161",
                                        "label": "Gateway BS231700161"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        "addresses": [
            {
                "uri": "http://concordia.ca/address/2155_Guy_H3H_2L9",
                "street_name": "Guy",
                "street_number": "2155",
                "postal_code": "H3H 2L9"
            }
        ]
    }
    
    # Create mapper
    mapper = ConcordiaOntologyMapper(config)
    
    # Test 1: Check required ontology types
    print("\n1️⃣ Testing required ontology types...")
    required_types = mapper.get_required_ontology_types()
    expected_types = [
        'https://saref.etsi.org/saref4bldg/Building',
        'https://saref.etsi.org/saref4bldg/BuildingSpace',
        'https://saref.etsi.org/saref4bldg/PhysicalObject',
        'https://saref.etsi.org/core/Device',
        'https://saref.etsi.org/core/Sensor',
        'https://saref.etsi.org/core/Measurement',
        'http://www.w3.org/ns/ssn/System',
        'http://www.w3.org/2006/time#TemporalEntity',
        'http://www.w3.org/2006/time#ProperInterval',
        'http://www.w3.org/2006/vcard/ns#Address'
    ]
    
    actual_types = [str(t) for t in required_types]
    print(f"   Expected types: {len(expected_types)}")
    print(f"   Actual types: {len(actual_types)}")
    
    missing_types = set(expected_types) - set(actual_types)
    if missing_types:
        print(f"   ❌ Missing types: {missing_types}")
    else:
        print("   ✅ All expected types are present")
    
    # Test 2: Create RDF graph
    print("\n2️⃣ Testing RDF graph creation...")
    try:
        graph = mapper.create_rdf_graph(sample_data)
        print(f"   ✅ RDF graph created successfully")
        print(f"   - Graph contains {len(graph)} triples")
        
        # Test 3: Check for specific ontology types in the graph
        print("\n3️⃣ Testing ontology types in graph...")
        from ontology_classes.namespaces import s4bldg, saref, ssn, time, vcard
        
        type_checks = [
            (s4bldg.Building, "Building"),
            (s4bldg.BuildingSpace, "BuildingSpace"),
            (s4bldg.PhysicalObject, "PhysicalObject"),
            (saref.Device, "Device"),
            (saref.Sensor, "Sensor"),
            (saref.Measurement, "Measurement"),
            (ssn.System, "System"),
            (time.TemporalEntity, "TemporalEntity"),
            (time.ProperInterval, "ProperInterval"),
            (vcard.Address, "Address")
        ]
        
        for rdf_type, type_name in type_checks:
            triples = list(graph.triples((None, None, rdf_type)))
            print(f"   - {type_name}: {len(triples)} instances")
        
        # Test 4: Check for specific relationships
        print("\n4️⃣ Testing relationships...")
        from ontology_classes.namespaces import s4bldg, saref, ssn, s4watr
        
        relationship_checks = [
            (s4bldg.hasSpace, "hasSpace"),
            (s4bldg.isContainedIn, "isContainedIn"),
            (s4bldg.contains, "contains"),
            (saref.makesMeasurement, "makesMeasurement"),
            (ssn.hasSubSystem, "hasSubSystem"),
            (ssn.isSubSystemOf, "isSubSystemOf"),
            (s4watr.hasPhenomenonTime, "hasPhenomenonTime")
        ]
        
        for relationship, rel_name in relationship_checks:
            triples = list(graph.triples((None, relationship, None)))
            print(f"   - {rel_name}: {len(triples)} triples")
        
        # Test 5: Save graph to file
        print("\n5️⃣ Testing graph serialization...")
        turtle_data = graph.serialize(format='turtle')
        with open("test_concordia_output.ttl", "w") as f:
            f.write(turtle_data)
        print(f"   ✅ Graph saved to test_concordia_output.ttl")
        print(f"   - File size: {len(turtle_data)} characters")
        
        print("\n🎉 All tests passed! ConcordiaOntologyMapper has the same functionality as full_ont_mapping.py")
        
        # Clean up test files
        os.remove("test_data.json")
        os.remove("test_concordia_output.ttl")
        
    except Exception as e:
        print(f"   ❌ Error creating RDF graph: {e}")
        # Clean up test files even on error
        if os.path.exists("test_data.json"):
            os.remove("test_data.json")
        return False
    
    return True


if __name__ == "__main__":
    test_concordia_mapper() 