#!/usr/bin/env bash
set -e

# Ensure script is executable
if [ ! -x "$0" ]; then
    chmod +x "$0"
fi

echo "Starting Neo4j Loader Service"
echo "================================"

# Wait for ontology mapping to complete
echo "Waiting for ontology mapping to complete..."
while [ ! -f "/app/shared_data/mapping_complete.marker" ]; do
    echo "   Waiting for mapping marker..."
    sleep 5
done
echo "Ontology mapping completed, proceeding with Neo4j loading"

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
until curl -sf "http://neo4j:7474" >/dev/null; do
    echo "   Waiting for Neo4j HTTP endpoint..."
    sleep 5
done
echo "Neo4j is ready!"

# Check if RDF data exists
if [ ! -f "/app/shared_data/concordia_ontology_output.ttl" ]; then
    echo "Error: RDF data file not found at /app/shared_data/concordia_ontology_output.ttl"
    echo "Please ensure the ontology mapper service completed successfully"
    exit 1
fi

echo "RDF data file found: concordia_ontology_output.ttl"

# Run the Neo4j loader
echo "Loading RDF data into Neo4j..."
cd /app
python3 -c "
import sys
import os
import json
from dotenv import load_dotenv
from rdflib import Graph
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()

# Get Neo4j credentials
neo4j_auth = os.getenv('NEO4J_AUTH', 'neo4j/cerciot')
username, password = neo4j_auth.split('/')
neo4j_uri = 'bolt://neo4j:7687'

print(f'🔗 Connecting to Neo4j at {neo4j_uri}')

try:
    # Load the RDF graph
    graph = Graph()
    graph.parse('/app/shared_data/concordia_ontology_output.ttl', format='turtle')
    
    print(f'Loaded RDF graph with {len(graph)} triples')
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
    
    with driver.session() as session:
        # Serialize to Turtle format
        turtle_data = graph.serialize(format='turtle')
        
        # Save to file for debugging
        with open('/app/shared_data/concordia_neo4j_output.ttl', 'w') as f:
            f.write(turtle_data)
        
        print(f'Turtle data saved to concordia_neo4j_output.ttl ({len(turtle_data)} characters)')
        
        # Load into Neo4j using n10s plugin
        load_query = \"CALL n10s.rdf.import.inline(\$turtle_data, 'Turtle')\"
        result = session.run(load_query, turtle_data=turtle_data)
        
        print('RDF data loaded into Neo4j successfully!')
        
        # Print summary
        print(f'Summary:')
        print(f'   - RDF triples: {len(graph)}')
        print(f'   - Turtle file: concordia_neo4j_output.ttl')
        print(f'   - Neo4j URI: {neo4j_uri}')
        print(f'   - Check Neo4j browser at http://localhost:7474')
        
except Exception as e:
    print(f'Error loading RDF data into Neo4j: {e}')
    raise
finally:
    if 'driver' in locals():
        driver.close()
"

echo "Neo4j loading completed!"
echo "Turtle data saved to: /app/shared_data/concordia_neo4j_output.ttl"

# Create a completion marker file
echo "Neo4j loading completed at $(date)" > /app/shared_data/neo4j_loading_complete.marker

echo "Neo4j Loader Service finished successfully!"
echo "You can now access Neo4j browser at http://localhost:7474" 