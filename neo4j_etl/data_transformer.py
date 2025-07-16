import json
import os
import sys
from typing import Dict, List

# Add the parent directory to the path to import ontology_classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ontology_classes import Building, Address

class DataTransformer:
    """
    Transforms sensor data into Building and Address objects for ontology mapping.
    Only considers: building, street_name, street_number, and postal_code.
    """
    
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.buildings: Dict[str, Building] = {}
        self.addresses: Dict[str, Address] = {}
        
    def load_sensor_data(self) -> List[Dict]:
        """Load sensor data from JSON file."""
        try:
            with open(self.data_file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading sensor data: {e}")
            return []
    
    def create_address_key(self, street_name: str, street_number: str, postal_code: str) -> str:
        """Create a unique key for an address."""
        return f"{street_number}_{street_name}_{postal_code}".replace(" ", "_")
    
    def create_building_key(self, building_name: str) -> str:
        """Create a unique key for a building based only on building name."""
        return building_name.strip()
    
    def transform_data(self) -> Dict[str, List]:
        """
        Transform sensor data into Building and Address objects.
        Returns a dictionary with 'buildings' and 'addresses' lists.
        """
        sensor_data = self.load_sensor_data()
        
        if not sensor_data:
            print("No sensor data loaded")
            return {'buildings': [], 'addresses': []}
        
        print(f"Processing {len(sensor_data)} sensor records...")
        
        for sensor in sensor_data:
            # Extract only the required attributes
            building_name = sensor.get('building')
            street_name = sensor.get('street_name')
            street_number = sensor.get('street_number')
            postal_code = sensor.get('postal_code')
            
            # Skip if missing required building or address information
            if not building_name or not street_name or not street_number or not postal_code:
                continue
            
            # Create address key and building key
            address_key = self.create_address_key(street_name, street_number, postal_code)
            building_key = self.create_building_key(building_name)
            
            # Create or get existing address
            if address_key not in self.addresses:
                address_uri = f"http://concordia.ca/address/{address_key}"
                self.addresses[address_key] = Address(
                    uri=address_uri,
                    street_name=street_name,
                    street_number=street_number,
                    postal_code=postal_code
                )
            
            # Create or get existing building
            if building_key not in self.buildings:
                building_uri = f"http://concordia.ca/building/{building_key}"
                self.buildings[building_key] = Building(
                    uri=building_uri,
                    label=f"{building_name} Building",
                    address=self.addresses[address_key],
                    spaces=[]  # Empty list since we're not using spaces
                )
            else:
                # If building already exists, check if it has the same address
                # If not, we might need to handle multiple addresses per building
                # For now, we'll assume one address per building
                pass
        
        print(f"Created {len(self.addresses)} unique addresses")
        print(f"Created {len(self.buildings)} unique buildings")
        
        return {
            'buildings': list(self.buildings.values()),
            'addresses': list(self.addresses.values())
        }
    
    def save_transformed_data(self, output_file: str = "transformed_data.json"):
        """Save transformed data to JSON file for inspection."""
        transformed_data = self.transform_data()
        
        # Convert objects to serializable format
        serializable_data = {
            'buildings': [
                {
                    'uri': str(building.uri),
                    'label': building.label,
                    'address_uri': str(building.address.uri) if building.address else None
                }
                for building in transformed_data['buildings']
            ],
            'addresses': [
                {
                    'uri': str(address.uri),
                    'street_name': address.street_name,
                    'street_number': address.street_number,
                    'postal_code': address.postal_code
                }
                for address in transformed_data['addresses']
            ]
        }
        
        # Save to the specified output file
        with open(output_file, 'w') as file:
            json.dump(serializable_data, file, indent=2)
        
        print(f"Transformed data saved to {output_file}")
        return transformed_data

def main():
    """Main function to run the data transformation."""
    # Get the path to the sensor data file (local path)
    data_file_path = "sensors_file/concordia_sensors_finalized.json"
    
    if not os.path.exists(data_file_path):
        print(f"Data file not found: {data_file_path}")
        return
    
    # Create transformer and process data
    transformer = DataTransformer(data_file_path)
    transformed_data = transformer.save_transformed_data()
    
    print("Data transformation completed successfully!")
    return transformed_data

if __name__ == "__main__":
    main() 