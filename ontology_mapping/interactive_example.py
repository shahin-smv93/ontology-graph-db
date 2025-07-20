#!/usr/bin/env python3
"""
Interactive example showing how to use config.py step by step.
"""

import sys
import os
import json

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_mapping.config import OntologyMappingConfig


def interactive_example():
    """Interactive example of using the configuration system."""
    
    print("🔧 Interactive Configuration Example")
    print("=" * 40)
    
    # Step 1: Load configuration
    print("\n📁 Step 1: Loading configuration...")
    config = OntologyMappingConfig.from_file("ontology_mapping/concordia_config.json")
    print(f"✅ Loaded config with {len(config.field_categories)} field categories")
    
    # Step 2: Show configuration details
    print("\n📋 Step 2: Configuration details...")
    print(f"   Base namespace: {config.base_namespace}")
    print(f"   Input file: {config.input_data_path}")
    print(f"   Required fields: {config.required_fields}")
    print(f"   Field categories: {list(config.field_categories.keys())}")
    
    # Step 3: Show field mappings
    print("\n🗺️  Step 3: Field mappings...")
    for category, mappings in config.field_categories.items():
        print(f"   {category}: {len(mappings)} fields")
        for logical, json_key in mappings.items():
            print(f"     {logical} → {json_key}")
    
    # Step 4: Test with sample data
    print("\n🧪 Step 4: Testing with sample data...")
    sample_record = {
        "sensorUID": "80930253DC1CA30139",
        "building": "ER",
        "floor": "ER-14",
        "mainRoom": "ER-14-1431",
        "room": "ER-14-1431-openSpace",
        "zone": "ER-14-1431-01",
        "sensorType": "deskSensor",
        "deskID": "1431-openSpace-54",
        "deskDescription": "Fixed Desk",
        "vendorName": "SchneiderElectric",
        "gatewayUID": "BS231700161",
        "timeInterval": "600.0",
        "unit": "ppm",
        "street_name": "Guy",
        "street_number": "2155",
        "postal_code": "H3H 2L9"
    }
    
    print(f"   Sample record has {len(sample_record)} fields")
    
    # Step 5: Extract data by category
    print("\n🔍 Step 5: Extracting data by category...")
    
    spatial_data = config.extract_spatial(sample_record)
    print(f"   Spatial data: {spatial_data}")
    
    sensor_data = config.extract_sensor(sample_record)
    print(f"   Sensor data: {sensor_data}")
    
    building_object_data = config.extract_building_object(sample_record)
    print(f"   Building object data: {building_object_data}")
    
    address_data = config.extract_address(sample_record)
    print(f"   Address data: {address_data}")
    
    # Step 6: Validate the record
    print("\n✅ Step 6: Validating record...")
    validation = config.validate_record(sample_record)
    print(f"   Valid: {validation['valid']}")
    if validation['missing']:
        print(f"   Missing: {validation['missing']}")
    if validation['null']:
        print(f"   Null: {validation['null']}")
    
    # Step 7: Show URI generation
    print("\n🔗 Step 7: URI generation...")
    building_uri = config.get_uri("building", spatial_data["building"])
    sensor_uri = config.get_uri("sensor", sensor_data["sensorUID"])
    print(f"   Building URI: {building_uri}")
    print(f"   Sensor URI: {sensor_uri}")
    
    print("\n🎉 Interactive example completed!")
    print("=" * 40)


def demonstrate_flexibility():
    """Demonstrate the flexibility of the configuration system."""
    
    print("\n🔄 Demonstrating Configuration Flexibility")
    print("=" * 40)
    
    # Create a different configuration for a different dataset
    print("\n📝 Creating a different configuration...")
    
    different_config = OntologyMappingConfig(
        base_namespace="http://different-university.edu",
        input_data_path="different_sensors.json",
        required_fields=["device_id", "campus", "device_type"],
        field_categories={
            "spatial": {
                "campus": "campus",
                "building": "building_name",
                "floor": "level",
                "room": "room_number"
            },
            "sensor": {
                "device_id": "device_id",
                "device_type": "device_type",
                "manufacturer": "manufacturer",
                "hub_id": "hub_id"
            },
            "building_object": {
                "workstation_id": "workstation_id",
                "equipment_type": "equipment_type"
            },
            "address": {
                "street": "street",
                "city": "city",
                "zip_code": "zip_code"
            }
        }
    )
    
    print("✅ Created different configuration")
    print(f"   Required fields: {different_config.required_fields}")
    print(f"   Field categories: {list(different_config.field_categories.keys())}")
    
    # Test with different data format
    different_record = {
        "device_id": "DEV12345",
        "campus": "Main",
        "building_name": "Science Hall",
        "level": "2",
        "room_number": "201",
        "device_type": "temperature",
        "manufacturer": "Siemens",
        "hub_id": "HUB001",
        "workstation_id": "WS001",
        "equipment_type": "Lab Equipment",
        "street": "University Ave",
        "city": "College Town",
        "zip_code": "12345"
    }
    
    print("\n🧪 Testing with different data format...")
    
    spatial_data = different_config.extract_spatial(different_record)
    sensor_data = different_config.extract_sensor(different_record)
    
    print(f"   Spatial: {spatial_data}")
    print(f"   Sensor: {sensor_data}")
    
    validation = different_config.validate_record(different_record)
    print(f"   Valid: {validation['valid']}")
    
    print("\n✅ Flexibility demonstration completed!")
    print("=" * 40)


if __name__ == "__main__":
    interactive_example()
    demonstrate_flexibility() 