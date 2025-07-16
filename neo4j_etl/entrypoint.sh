#!/usr/bin/env sh
set -e

# wait for Neo4j HTTP to be ready
echo "Waiting for Neo4j to be ready at ${NEO4J_HOST:-neo4j}:${NEO4J_HTTP_PORT:-7474}..."
until curl -sf "http://${NEO4J_HOST:-neo4j}:${NEO4J_HTTP_PORT:-7474}" >/dev/null; do
  sleep 3
done
echo "Neo4j is up!"

echo "Running neo4j_setup.py"
python3 neo4j_setup.py

echo "Running ont_mapping.py"
python3 ont_mapping.py

echo "ETL complete!"