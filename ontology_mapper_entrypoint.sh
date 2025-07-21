#!/usr/bin/env bash
set -e

# Ensure script is executable
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi

echo "Starting Ontology Mapper Service"
echo "==================================="

# Wait for data transformer to complete
echo "Waiting for data transformation to complete..."
while [ ! -f "/app/shared_data/transformation_complete.marker" ]; do
    echo "   Waiting for transformation marker..."
    sleep 5
done
echo "Data transformation completed, proceeding with ontology mapping"

# Check if transformed data exists
if [ ! -f "/app/shared_data/concordia_transformed_data.json" ]; then
    echo "Error: Transformed data file not found at /app/shared_data/concordia_transformed_data.json"
    echo "Please ensure the data transformer service completed successfully"
    exit 1
fi

echo "Transformed data file found: concordia_transformed_data.json"

# Run the ontology mapper
echo "Running Concordia Ontology Mapper..."
cd /app
python3 -c "
import sys
import os
sys.path.append('/app')

from ontology_mapping import OntologyMappingConfig
from ontology_mapping.concordia_mapper import ConcordiaOntologyMapper

# Load configuration
config = OntologyMappingConfig.from_file('ontology_mapping/concordia_config.json')

# Update output paths to use shared volume
config.output_transformed_path = '/app/shared_data/concordia_transformed_data.json'
config.output_rdf_path = '/app/shared_data/concordia_ontology_output.ttl'
config.output_debug_path = '/app/shared_data/concordia_debug_output.ttl'

# Create mapper and run
mapper = ConcordiaOntologyMapper(config)
rdf_graph = mapper.map()

print(f'Ontology mapping completed successfully!')
print(f'RDF graph contains {len(rdf_graph)} triples')
print(f'Output saved to: {config.output_rdf_path}')
print(f'Debug output saved to: {config.output_debug_path}')

# Print validation summary
required_types = mapper.get_required_ontology_types()
for rdf_type in required_types:
    triples = list(rdf_graph.triples((None, None, rdf_type)))
    print(f'   {rdf_type}: {len(triples)} instances')
"

echo "Ontology mapping completed!"
echo "RDF data saved to: /app/shared_data/concordia_ontology_output.ttl"
echo "Debug data saved to: /app/shared_data/concordia_debug_output.ttl"

# Create a completion marker file
echo "Ontology mapping completed at $(date)" > /app/shared_data/mapping_complete.marker

echo "Ontology Mapper Service finished successfully!" 