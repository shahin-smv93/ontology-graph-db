FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ontology framework
COPY ontology_classes/ ./ontology_classes/
COPY ontology_mapping/ ./ontology_mapping/

# Copy the Neo4j loader script
COPY neo4j_loader_entrypoint.sh .
RUN chmod +x neo4j_loader_entrypoint.sh && \
    chown -R root:root /app

# Set user to root for execution
USER root

# Default command
CMD ["/app/neo4j_loader_entrypoint.sh"] 