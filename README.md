# Ontology Mapping Pipeline

> **Note:** This project is developed for the IoT showroom of the Next Generation Cities Institute at Concordia University. It is an evolving platform and will be expanded in the future to cover additional use cases, data sources, and ontology extensions.

## Overview

This project provides a robust, extensible pipeline for transforming raw sensor and building data into a semantically rich ontology, leveraging the [BIGG Ontology](https://github.com/BeeGroup-cimne/biggontology). The pipeline is designed to:
- **Ingest** heterogeneous sensor/building datasets
- **Transform** them into a structured, hierarchical format suitable for ontology mapping
- **Map** the structured data to ontology classes (using RDF/OWL standards)
- **Load** the resulting knowledge graph into a Neo4j database for advanced querying and analytics

The framework is general and reusable, supporting a wide range of building, sensor, and measurement data sources.

---

## About the BIGG Ontology

The BIGG Ontology is an open-source initiative that establishes a standardized schema for describing, characterizing, and analyzing buildings and urban areas. It supports urban planning, building management, and sustainable development by creating a shared vocabulary for researchers and practitioners. The ontology includes frameworks for defining measurements and key performance indicators (KPIs) to enable precise evaluation and benchmarking of building and urban area performance.

For more information, see the [BIGG Ontology GitHub repository](https://github.com/BeeGroup-cimne/biggontology).

---

## Pipeline Architecture

The pipeline consists of the following main stages:

1. **Data Ingestion**  
   Raw sensor/building data (e.g., JSON, CSV) is placed in the designated input directory.

2. **Data Transformation**  
   The data is parsed and transformed into a hierarchical, structured format. This step normalizes the data, extracts spatial and physical hierarchies (buildings, floors, rooms, zones, desks, sensors, etc.), and prepares it for ontology mapping.

3. **Ontology Mapping**  
   The structured data is mapped to ontology classes defined by the BIGG Ontology. This includes:
   - Buildings and their spatial components
   - Physical objects (e.g., desks)
   - Sensors and their types
   - Measurements, properties, and units
   - Gateways and relationships
   - Temporal entities (time intervals)

   The output is an RDF graph (in Turtle format) representing the knowledge extracted from the original data.

4. **Neo4j Loading**  
   The RDF graph is loaded into a Neo4j database using the n10s (Neosemantics) plugin, enabling semantic queries and graph analytics.

---

## Key Features

- **Generic & Reusable**: No hardcoded domain-specific URIs; all mappings are externally configurable.
- **Extensible**: Easily adapt the pipeline to new data sources or ontology extensions.
- **Configurable**: All field mappings and transformation rules are defined in a JSON configuration file.
- **Validation & Debugging**: Built-in validation and debug output for data quality assurance.
- **Error Handling**: Comprehensive error handling for configuration, transformation, and mapping steps.

---

## How It Works

1. **Prepare your data**  
   Place your raw sensor/building data file (e.g., `input_sensors.json`) in the input directory.

2. **Configure the pipeline**  
   Edit the configuration file (e.g., `ontology_mapping/config.json`) to specify:
   - Input/output file paths
   - Field mappings for your dataset
   - Optional validation and debug settings

3. **Run the pipeline**  
   The recommended way is to use Docker Compose, which orchestrates all steps:

   ```bash
   docker-compose up
   ```

   This will:
   - Start Neo4j and required plugins
   - Transform your data
   - Map it to the ontology
   - Load the resulting RDF into Neo4j

   Alternatively, you can run each step manually using the provided Python scripts.

4. **Query your knowledge graph**  
   Access the Neo4j browser at [http://localhost:7474](http://localhost:7474) to explore and query your semantic data.

---

## Configuration Example

```json
{
  "base_namespace": "http://your-organization.com",
  "input_data_path": "input_sensors.json",
  "output_transformed_path": "transformed_data.json",
  "output_rdf_path": "ontology_output.ttl",
  "output_debug_path": "debug_output.ttl",
  "field_categories": {
    "spatial": { "building": "building", "floor": "floor", "room": "room", "zone": "zone" },
    "sensor": { "sensorUID": "sensorUID", "sensorType": "sensorType", "unit": "unit" },
    "address": { "street_name": "street_name", "postal_code": "postal_code" }
  },
  "enable_debug": true,
  "validate_data": true
}
```

---

## Supported Ontology Classes

- **Building**: Physical buildings with addresses
- **BuildingSpace**: Floors, rooms, zones
- **PhysicalObject**: Desks and other objects
- **Sensor**: All sensor types
- **Gateway**: Communication gateways
- **Measurement**: Sensor measurements, properties, and units
- **TimeInterval**: Temporal entities for measurement intervals

---

## Relationships (Highlight)

- **Spatial**: Building <--> Floor <--> Room/Zone
- **Physical**: Room/Zone <--> Desk <--> Sensor / Room/Zone <--> Sensor
- **Sensor**: Sensor --> Measurement --> TimeInterval
- **Gateway**: Gateway <--> Sensor
- **Properties**: Measurement --> Property, Measurement --> Unit

---

## Extending the Pipeline

To adapt the pipeline for a new dataset:
1. Create a new configuration file with your field mappings.
2. (If needed) Extend the transformer and mapper classes for custom logic.
3. Run the pipeline with your new configuration.

---

## License

This project is open source and designed for extensibility and reuse.  
BIGG Ontology is licensed under the EUPL-1.2 license.  
See [BIGG Ontology GitHub](https://github.com/BeeGroup-cimne/biggontology) for details.