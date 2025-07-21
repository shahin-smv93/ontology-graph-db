#!/usr/bin/env bash
# set -e

# Ensure script is executable
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi

echo "Starting Data Transformer Service"
echo "====================================="
echo "DEBUG: Script is executing"

# Check if sensor file exists
if [ ! -f "/app/sensors_file/concordia_sensors_finalized.json" ]; then
    echo "Error: Sensor file not found at /app/sensors_file/concordia_sensors_finalized.json"
    echo "Please ensure your sensor data file is placed in the sensors_file directory"
    exit 1
fi

echo "Sensor file found: concordia_sensors_finalized.json"
echo "DEBUG: About to start transformation"

# Run the data transformer
echo "Running Concordia Data Transformer..."
echo "DEBUG: About to execute Python code"
echo "Checking file path: /app/sensors_file/concordia_sensors_finalized.json"
ls -la /app/sensors_file/
echo "File content preview (first 200 chars):"
head -c 200 /app/sensors_file/concordia_sensors_finalized.json
echo ""
echo "Testing JSON parsing:"
python3 -c "import json; data = json.load(open('/app/sensors_file/concordia_sensors_finalized.json')); print('Data type:', type(data)); print('Data length:', len(data) if isinstance(data, list) else 'Not a list')"
cd /app
echo "Testing imports..."
python3 -c "import sys; import os; print('Current directory:', os.getcwd()); print('Files in ontology_mapping:', os.listdir('ontology_mapping'))"
echo "Testing configuration loading..."
python3 -c "import sys; sys.path.append('/app'); from ontology_mapping import OntologyMappingConfig; config = OntologyMappingConfig.from_file('ontology_mapping/concordia_config.json'); print('Configuration loaded successfully'); print('Input path:', config.input_data_path)"
echo "Running full transformation..."
python3 -c "
import sys
import os
sys.path.append('/app')

from ontology_mapping import OntologyMappingConfig
from ontology_mapping.concordia_transformer import ConcordiaDataTransformer

# Load configuration
config = OntologyMappingConfig.from_file('ontology_mapping/concordia_config.json')

# Update input and output paths to use correct paths for data transformer
config.input_data_path = '/app/sensors_file/concordia_sensors_finalized.json'
config.output_transformed_path = '/app/shared_data/concordia_transformed_data.json'
config.output_rdf_path = '/app/shared_data/concordia_ontology_output.ttl'
config.output_debug_path = '/app/shared_data/concordia_debug_output.ttl'

# Create transformer and run
transformer = ConcordiaDataTransformer(config)
result = transformer.transform()

print(f'Data transformation completed successfully!')
print(f'Summary: {len(result.get(\"buildings\", []))} buildings, {len(result.get(\"addresses\", []))} addresses')
print(f'Output saved to: {config.output_transformed_path}')
"

echo "Data transformation completed!"
echo "Transformed data saved to: /app/shared_data/concordia_transformed_data.json"

echo "Data transformation completed at $(date)" > /app/shared_data/transformation_complete.marker

echo "Data Transformer Service finished successfully!" 