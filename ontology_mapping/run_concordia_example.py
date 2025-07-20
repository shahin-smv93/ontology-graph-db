#!/usr/bin/env python3
"""
Example script showing how to use config.py with concordia_config.json
to transform sensor data into hierarchical structure.
"""

import sys
import os
from typing import Dict, Any

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_mapping.config import OntologyMappingConfig
from ontology_mapping.concordia_transformer import ConcordiaDataTransformer


def main():
    """Main function demonstrating the complete pipeline."""
    
    print("🚀 Starting Concordia Data Transformation Pipeline")
    print("=" * 50)
    
    # Step 1: Load configuration
    print("\n1️⃣ Loading configuration...")
    try:
        config = OntologyMappingConfig.from_file("ontology_mapping/concordia_config.json")
        print(f"✅ Configuration loaded from: ontology_mapping/concordia_config.json")
        print(f"   - Input data: {config.input_data_path}")
        print(f"   - Output: {config.output_transformed_path}")
        print(f"   - Required fields: {config.required_fields}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Step 2: Validate configuration
    print("\n2️⃣ Validating configuration...")
    try:
        config.validate()
        print("✅ Configuration is valid")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return
    
    # Step 3: Create transformer
    print("\n3️⃣ Creating transformer...")
    try:
        transformer = ConcordiaDataTransformer(config)
        print("✅ Transformer created successfully")
    except Exception as e:
        print(f"❌ Failed to create transformer: {e}")
        return
    
    # Step 4: Test field extraction (optional)
    print("\n4️⃣ Testing field extraction...")
    test_record = {
        "sensorUID": "80930253DC1CA30139",
        "building": "ER",
        "floor": "ER-14",
        "room": "ER-14-1431-openSpace",
        "sensorType": "deskSensor",
        "deskID": "1431-openSpace-54",
        "vendorName": "SchneiderElectric",
        "gatewayUID": "BS231700161",
        "street_name": "Guy",
        "street_number": "2155",
        "postal_code": "H3H 2L9"
    }
    
    # Test extraction methods
    spatial_data = config.extract_spatial(test_record)
    sensor_data = config.extract_sensor(test_record)
    building_object_data = config.extract_building_object(test_record)
    address_data = config.extract_address(test_record)
    
    print(f"   - Spatial: {spatial_data}")
    print(f"   - Sensor: {sensor_data}")
    print(f"   - Building Object: {building_object_data}")
    print(f"   - Address: {address_data}")
    
    # Step 5: Validate test record
    print("\n5️⃣ Testing record validation...")
    validation_result = config.validate_record(test_record)
    print(f"   - Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"   - Missing: {validation_result['missing']}")
        print(f"   - Null: {validation_result['null']}")
    
    # Step 6: Transform data
    print("\n6️⃣ Transforming data...")
    try:
        result = transformer.transform()
        print(f"✅ Transformation completed successfully!")
        print(f"   - Output saved to: {config.output_transformed_path}")
        
        # Show a summary of the result
        if isinstance(result, dict):
            print(f"   - Buildings: {len(result.get('buildings', []))}")
            print(f"   - Addresses: {len(result.get('addresses', []))}")
            
    except Exception as e:
        print(f"❌ Transformation failed: {e}")
        return
    
    print("\n🎉 Pipeline completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main() 