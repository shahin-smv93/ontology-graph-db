FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ontology classes
COPY ontology_classes/ ./ontology_classes/

# Copy the application files
COPY neo4j_etl/ .

# Make scripts executable
RUN chmod +x entrypoint.sh

# Default command (can be overridden in docker-compose)
CMD ["/app/entrypoint.sh"] 