# Ontology Mapping Framework

A general, extensible framework for mapping sensor and building data to ontologies using RDF and semantic web standards.

## Overview

This framework provides a structured approach to transform sensor data into hierarchical ontology structures and then map them to RDF graphs. It's designed to be:

- **Extensible**: Users can implement their own data structures and mapping logic
- **Configurable**: Dataset-specific settings are managed through configuration files
- **Reusable**: Common functionality is abstracted into base classes
- **Validatable**: Built-in validation and error handling

## Architecture

The framework consists of three main components:

1. **Configuration Management** (`OntologyMappingConfig`)
2. **Data Transformation** (`BaseDataTransformer`)
3. **Ontology Mapping** (`BaseOntologyMapper`)

### Abstract Base Classes

- `BaseDataTransformer`: Abstract class for transforming raw sensor data into hierarchical structures
- `BaseOntologyMapper`: Abstract class for mapping hierarchical data to RDF ontology

### Concrete Implementations

- `ConcordiaDataTransformer`: Implementation for Concordia sensor dataset
- `ConcordiaOntologyMapper`: Implementation for Concordia ontology mapping

## Quick Start

### 1. Create Configuration

Create a JSON configuration file for your dataset:

```json
{
  "base_namespace": "http://your-organization.com",
  "input_data_path": "path/to/your/sensor_data.json",
  "output_transformed_path": "transformed_data.json",
  "output_rdf_path": "ontology_output.ttl",
  "output_debug_path": "debug_output.ttl",
  
  "sensor_id_field": "sensorUID",
  "building_field": "building",
  "floor_field": "floor",
  "room_field": "room",
  "zone_field": "zone",
  "gateway_field": "gatewayUID",
  "sensor_type_field": "sensorType",
  "time_interval_field": "timeInterval",
  
  "sensor_fields": {
    "sensorId": "sensorId",
    "vendorName": "vendorName",
    "installationDate": "installationDate"
  },
  
  "desk_fields": {
    "deskID": "deskID",
    "deskDescription": "deskDescription"
  },
  
  "measurement_fields": {
    "unit": "unit"
  },
  
  "spatial_fields": {
    "mainRoom": "mainRoom"
  },
  
  "address_fields": {
    "street_name": "street_name",
    "street_number": "street_number",
    "postal_code": "postal_code"
  },
  
  "ignore_null_values": true,
  "ignore_missing_fields": true,
  "strict_validation": false,
  
  "enable_debug": true,
  "validate_data": true,
  "create_time_intervals": true,
  "create_gateway_relationships": true
}
```

### 2. Implement Your Transformer

Extend `BaseDataTransformer` and implement the abstract methods:

```python
from ontology_mapping import BaseDataTransformer, OntologyMappingConfig

class MyDataTransformer(BaseDataTransformer):
    def extract_building_info(self, record):
        # Extract building information from your data
        pass
    
    def extract_address_info(self, record):
        # Extract address information from your data
        pass
    
    def extract_spatial_hierarchy(self, record):
        # Extract spatial hierarchy (floor, room, zone)
        pass
    
    def extract_sensor_info(self, record):
        # Extract sensor information
        pass
    
    def extract_measurement_info(self, record):
        # Extract measurement information
        pass
    
    def create_hierarchical_structure(self, data):
        # Create the final hierarchical structure
        pass
```

### 3. Implement Your Mapper

Extend `BaseOntologyMapper` and implement the abstract methods:

```python
from ontology_mapping import BaseOntologyMapper
from rdflib import Graph, URIRef

class MyOntologyMapper(BaseOntologyMapper):
    def create_building_objects(self, data):
        # Create building objects from hierarchical data
        pass
    
    def create_address_objects(self, data):
        # Create address objects
        pass
    
    def create_spatial_objects(self, data):
        # Create spatial objects (floors, rooms, zones)
        pass
    
    def create_sensor_objects(self, data):
        # Create sensor objects
        pass
    
    def create_measurement_objects(self, data):
        # Create measurement objects
        pass
    
    def create_gateway_objects(self, data):
        # Create gateway objects
        pass
    
    def setup_namespaces(self, graph):
        # Set up ontology namespaces
        pass
    
    def get_required_ontology_types(self):
        # Return list of required RDF types
        pass
```

### 4. Run the Pipeline

```python
from ontology_mapping import OntologyMappingConfig

# Load configuration
config = OntologyMappingConfig.from_file("my_config.json")

# Transform data
transformer = MyDataTransformer(config)
transformed_data = transformer.transform()

# Map to ontology
mapper = MyOntologyMapper(config)
rdf_graph = mapper.map()

print(f"Created RDF graph with {len(rdf_graph)} triples")
```

## Concordia Dataset Example

For the Concordia dataset, use the provided implementations:

```bash
python ontology_mapping/run_concordia_mapping.py
```

This will:
1. Load the Concordia configuration
2. Transform the sensor data into hierarchical structure
3. Map the hierarchy to RDF ontology
4. Save the results to Turtle files

## Configuration Options

### Core Settings
- `base_namespace`: Base URI namespace for your organization
- `input_data_path`: Path to your sensor data file
- `output_transformed_path`: Path for transformed hierarchical data
- `output_rdf_path`: Path for generated RDF/Turtle file
- `output_debug_path`: Path for debug output

### Field Mappings
- `sensor_id_field`: Field name for sensor unique identifier
- `building_field`: Field name for building identifier
- `floor_field`: Field name for floor identifier
- `room_field`: Field name for room identifier
- `zone_field`: Field name for zone identifier
- `gateway_field`: Field name for gateway identifier
- `sensor_type_field`: Field name for sensor type
- `time_interval_field`: Field name for time interval

### Optional Field Categories
- `sensor_fields`: Dictionary mapping sensor-related fields (sensorId, vendorName, etc.)
- `desk_fields`: Dictionary mapping desk-related fields (deskID, deskDescription, etc.)
- `measurement_fields`: Dictionary mapping measurement-related fields (unit, etc.)
- `spatial_fields`: Dictionary mapping spatial hierarchy fields (mainRoom, wing, etc.)
- `address_fields`: Dictionary mapping address field names

### Field Handling
- `ignore_null_values`: Whether to ignore null values in optional fields
- `ignore_missing_fields`: Whether to ignore missing optional fields
- `strict_validation`: Whether to enforce strict validation rules

### Optional Settings
- `enable_debug`: Enable debug output
- `validate_data`: Enable data validation
- `create_time_intervals`: Create time interval objects
- `create_gateway_relationships`: Create gateway-sensor relationships

## Supported Ontology Classes

The framework supports the following ontology classes:

- **Building**: Physical buildings with addresses
- **BuildingSpace**: Floors, rooms, zones within buildings
- **PhysicalObject**: Desks and other physical objects
- **Sensor**: Various types of sensors (desk, IAQ, etc.)
- **Gateway**: Communication gateways
- **Measurement**: Sensor measurements with properties and units
- **TimeInterval**: Temporal entities for measurement intervals

## Relationships

The framework creates the following relationships:

- **Spatial**: Building → Floor → MainRoom → (Room + Zone)
- **Physical**: Room/Zone → Desk → Sensor
- **Sensor**: Sensor → Measurement → TimeInterval
- **Gateway**: Gateway ↔ Sensor (bidirectional)
- **Properties**: Measurement → Property, Measurement → Unit

## Error Handling

The framework includes comprehensive error handling:

- `OntologyMappingError`: Base exception for all mapping errors
- `ConfigurationError`: Configuration-related errors
- `DataTransformationError`: Data transformation errors
- `OntologyMappingValidationError`: Validation errors
- `MissingRequiredFieldError`: Missing required data fields

## Extending the Framework

To extend the framework for new datasets:

1. **Create a new configuration file** with your dataset-specific settings
2. **Extend BaseDataTransformer** and implement the abstract methods
3. **Extend BaseOntologyMapper** and implement the abstract methods
4. **Create a main script** to run your pipeline

## Dependencies

- `rdflib`: RDF graph manipulation
- `dataclasses`: Configuration management
- Standard Python libraries: `json`, `logging`, `os`, `sys`

## License

This framework is designed to be open and extensible for various sensor data mapping needs. 