FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Neo4j setup files
COPY neo4j_etl/neo4j_setup.py .
COPY neo4j_etl/entrypoint.sh .

# Make scripts executable
RUN chmod +x entrypoint.sh && \
    chown -R root:root /app

# Set user to root for execution
USER root

# Default command
CMD ["/app/entrypoint.sh"] 