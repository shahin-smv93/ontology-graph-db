# 🐳 Automated Ontology Mapping Pipeline with Docker

This Docker Compose setup provides a complete automated pipeline for transforming sensor data into RDF ontology and loading it into Neo4j.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Sensor data file (JSON format)
- Neo4j credentials

### Setup Steps

1. **Place your sensor data file:**
   ```bash
   cp your_sensor_data.json sensors_file/concordia_sensors_finalized.json
   ```

2. **Create environment file:**
   ```bash
   echo "NEO4J_AUTH=neo4j/your_password" > .env
   ```

3. **Start the pipeline:**
   ```bash
   docker-compose up
   ```

## 📋 Pipeline Overview

The automated pipeline consists of 5 services that run in sequence:

### 1. **Neo4j Database** (`neo4j`)
- Starts the Neo4j database with n10s plugin
- Loads ontology extensions and Bigg ontology
- Exposes ports 7474 (browser) and 7687 (bolt)

### 2. **Neo4j Setup** (`neo4j_setup`)
- Runs after Neo4j is healthy
- Executes `neo4j_setup.py` to configure Neo4j
- Sets up constraints and indexes

### 3. **Data Transformer** (`data_transformer`)
- Runs after Neo4j setup completes
- Processes sensor data using `concordia_transformer.py`
- Creates hierarchical structure from flat sensor data
- Outputs: `concordia_transformed_data.json`

### 4. **Ontology Mapper** (`ontology_mapper`)
- Runs after data transformation completes
- Maps hierarchical data to RDF ontology using `concordia_mapper.py`
- Creates RDF triples with proper ontology classes
- Outputs: `concordia_ontology_output.ttl`

### 5. **Neo4j Loader** (`neo4j_loader`)
- Runs after ontology mapping completes
- Loads RDF data into Neo4j using n10s plugin
- Creates graph database with ontology structure

## 📁 File Structure

```
project/
├── docker-compose.yaml          # Main orchestration file
├── .env                         # Neo4j credentials (user provides)
├── sensors_file/
│   └── concordia_sensors_finalized.json  # Sensor data (user provides)
├── ontology_mapping/
│   ├── concordia_config.json    # Configuration (user provides)
│   ├── concordia_transformer.py # Data transformer (user writes)
│   ├── concordia_mapper.py      # Ontology mapper (user writes)
│   └── ...                      # Framework files
├── ontology_classes/            # Ontology class definitions
├── biggontology/               # Bigg ontology definitions
├── extensions.ttl              # Ontology extensions
└── shared_data/                # Shared volume for inter-service communication
```

## 🔧 Customization

### For Different Datasets

1. **Update Configuration:**
   - Modify `ontology_mapping/concordia_config.json`
   - Update field mappings and paths

2. **Customize Transformer:**
   - Modify `ontology_mapping/concordia_transformer.py`
   - Implement dataset-specific data extraction logic

3. **Customize Mapper:**
   - Modify `ontology_mapping/concordia_mapper.py`
   - Implement dataset-specific ontology mapping

4. **Update Sensor Data:**
   - Replace `sensors_file/concordia_sensors_finalized.json`
   - Ensure data format matches your transformer

### Environment Variables

```bash
# .env file
NEO4J_AUTH=neo4j/your_password
NEO4J_URI=bolt://localhost:7687
```

## 📊 Monitoring

### Service Status
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# View all logs
docker-compose logs -f
```

### Output Files
After successful completion, check:
- `shared_data/concordia_transformed_data.json` - Hierarchical data
- `shared_data/concordia_ontology_output.ttl` - RDF ontology
- `shared_data/concordia_debug_output.ttl` - Debug information
- `shared_data/concordia_neo4j_output.ttl` - Neo4j-loaded data

### Neo4j Browser
Access Neo4j browser at: http://localhost:7474
- Username: `neo4j`
- Password: (from your .env file)

## 🛠️ Troubleshooting

### Common Issues

1. **Service Dependencies:**
   - Services wait for completion markers
   - Check logs for dependency issues

2. **File Permissions:**
   - Ensure sensor data file is readable
   - Check shared volume permissions

3. **Neo4j Connection:**
   - Verify Neo4j credentials in .env
   - Check Neo4j health status

4. **Memory Issues:**
   - Adjust Neo4j memory settings in docker-compose.yaml
   - Monitor container resource usage

### Debug Commands

```bash
# Check service health
docker-compose ps

# View specific service logs
docker-compose logs data_transformer

# Enter running container
docker-compose exec ontology_mapper bash

# Check shared volume
docker-compose exec ontology_mapper ls -la /app/shared_data/
```

## 🔄 Restarting the Pipeline

```bash
# Stop all services
docker-compose down

# Clean up volumes (optional)
docker-compose down -v

# Restart pipeline
docker-compose up

# Restart specific service
docker-compose restart data_transformer
```

## 📈 Performance

### Optimization Tips

1. **Neo4j Memory:**
   - Adjust `NEO4J_dbms_memory_heap_max__size`
   - Monitor memory usage

2. **Data Volume:**
   - Large datasets may require more memory
   - Consider batch processing for very large files

3. **Network:**
   - Services communicate via Docker network
   - Minimal network overhead

## 🎯 Success Indicators

When the pipeline completes successfully:

1. ✅ All services show "completed successfully"
2. ✅ Neo4j browser accessible at http://localhost:7474
3. ✅ Data visible in Neo4j graph database
4. ✅ Output files present in shared_data/
5. ✅ No error messages in logs

## 📞 Support

For issues or questions:
1. Check service logs: `docker-compose logs [service_name]`
2. Verify file paths and permissions
3. Ensure all required files are present
4. Check Neo4j browser for data validation 