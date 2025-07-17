#!/usr/bin/env python3

from rdflib import Graph
from ontology_classes.sensors import Sensor
from ontology_classes.measurement import Measurement, TimeInterval
from ontology_classes.sensor_type_mapping import get_feature_of_interest, validate_sensor_type
from measurement_helpers import create_measurement_from_sensor_data
from ontology_classes.namespaces import saref, bigg

def test_sensor_type_mapping():
    """Test the sensor type to FeatureOfInterest mapping"""
    
    print("=== Testing Sensor Type Mapping ===")
    
    # Test cases from your JSON file
    test_cases = [
        {"sensorUID": "SENSOR_001", "sensorType": "temperatureSensor", "unit": "degC", "timeInterval": "300.0"},
        {"sensorUID": "SENSOR_002", "sensorType": "co2Sensor", "unit": "ppm", "timeInterval": "600.0"},
        {"sensorUID": "SENSOR_003", "sensorType": "deskSensor", "unit": None, "timeInterval": None},
        {"sensorUID": "SENSOR_004", "sensorType": "pm2_5Sensor", "unit": "micgram_m3", "timeInterval": "900.0"},
        {"sensorUID": "SENSOR_005", "sensorType": "unknownSensor", "unit": "unknown", "timeInterval": "300.0"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Sensor Type: {test_case['sensorType']}")
        
        # Test the mapping
        feature_uri = get_feature_of_interest(test_case['sensorType'])
        is_valid = validate_sensor_type(test_case['sensorType'])
        
        print(f"Valid sensor type: {is_valid}")
        print(f"FeatureOfInterest URI: {feature_uri}")
        
        if feature_uri:
            # Create a measurement using the helper function
            measurement = create_measurement_from_sensor_data(test_case, f"test_{i}")
            print(f"Created measurement: {measurement}")
        else:
            print("No mapping found for this sensor type")

def test_measurement_creation():
    """Test creating measurements and connecting them to sensors"""
    
    print("\n=== Testing Measurement Creation ===")
    
    # Create a graph
    g = Graph()
    
    # Test with a temperature sensor
    sensor_data = {
        "sensorUID": "TEMP_SENSOR_001",
        "sensorType": "temperatureSensor",
        "unit": "degC",
        "timeInterval": "300.0"
    }
    
    # Create sensor
    sensor = Sensor(
        uri=f"http://example.com/sensor/{sensor_data['sensorUID']}",
        sensorUID=sensor_data['sensorUID'],
        sensorId="TEMP_001",
        vendorName="Test Corp"
    )
    
    # Create measurement using helper
    measurement = create_measurement_from_sensor_data(sensor_data, "temp_measurement")
    
    # Connect sensor to measurement
    sensor.has_measurement = measurement
    
    # Add to graph
    sensor.add_to_graph(g)
    measurement.add_to_graph(g)
    if measurement.time_interval:
        measurement.time_interval.add_to_graph(g)
    
    # Print results
    print(f"Created sensor: {sensor}")
    print(f"Created measurement: {measurement}")
    print(f"FeatureOfInterest: {measurement.measured_property}")
    
    # Check the triples
    print("\n=== Generated Triples ===")
    for triple in g:
        print(triple)
    
    # Verify the connection
    makes_measurement_triples = list(g.triples((sensor.uri, saref.makesMeasurement, measurement.uri)))
    print(f"\nSensor connected to measurement: {len(makes_measurement_triples) > 0}")
    
    # Verify FeatureOfInterest
    if measurement.measured_property:
        feature_triples = list(g.triples((measurement.uri, saref.isMeasurementOf, measurement.measured_property)))
        print(f"Measurement connected to FeatureOfInterest: {len(feature_triples) > 0}")

if __name__ == "__main__":
    test_sensor_type_mapping()
    test_measurement_creation() 