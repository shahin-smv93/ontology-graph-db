#!/usr/bin/env python3
"""
Complete Concordia ontology mapping pipeline with Neo4j loading.
This script combines the Concordia mapping framework with Neo4j integration.
"""

import logging
import sys
import os
from rdflib import Graph
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_mapping import OntologyMappingConfig
from ontology_mapping.concordia_transformer import ConcordiaDataTransformer
from ontology_mapping.concordia_mapper import ConcordiaOntologyMapper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def load_rdf_to_neo4j(rdf_graph: Graph, neo4j_uri: str, username: str, password: str):
    """Load RDF graph into Neo4j using n10s plugin."""
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        with driver.session() as session:
            # Write Turtle to file for debugging
            turtle_data = rdf_graph.serialize(format='turtle')
            with open("concordia_neo4j_output.ttl", "w") as f:
                f.write(turtle_data)
            
            logger.info(f"Turtle RDF written to concordia_neo4j_output.ttl ({len(turtle_data)} characters)")
            
            # Print a sample of the Turtle data (first 1000 chars)
            print("\n===== Sample of Turtle RDF (first 1000 chars) =====\n")
            print(turtle_data[:1000] + "..." if len(turtle_data) > 1000 else turtle_data)
            print("\n===================================================\n")
            
            # Load into Neo4j using n10s plugin
            load_query = "CALL n10s.rdf.import.inline($turtle_data, 'Turtle')"
            result = session.run(load_query, turtle_data=turtle_data)
            logger.info("RDF data loaded into Neo4j successfully")
            
    except Exception as e:
        logger.error(f"Error loading RDF data into Neo4j: {e}")
        raise
    finally:
        driver.close()


def concordia_to_neo4j_pipeline():
    """Main function for complete Concordia ontology mapping with Neo4j loading."""
    
    # Check for Neo4j credentials
    env_neo4j = os.getenv('NEO4J_AUTH')
    if not env_neo4j:
        raise ValueError("NEO4J_AUTH is not defined in the env file")
    
    username, password = env_neo4j.split('/')
    neo4j_uri = 'bolt://localhost:7687'
    
    try:
        print("Starting Concordia to Neo4j Pipeline")
        print("=" * 50)
        
        # Step 1: Load configuration
        config_path = "ontology_mapping/concordia_config.json"
        logger.info(f"Loading configuration from {config_path}")
        config = OntologyMappingConfig.from_file(config_path)
        
        # Step 2: Transform data
        logger.info("Starting data transformation...")
        transformer = ConcordiaDataTransformer(config)
        transformed_data = transformer.transform()
        
        logger.info(f"Data transformation completed. Output saved to {config.output_transformed_path}")
        logger.info(f"Summary: {len(transformed_data.get('buildings', []))} buildings, "
                   f"{len(transformed_data.get('addresses', []))} addresses")
        
        if not transformed_data['buildings'] and not transformed_data['addresses']:
            logger.warning("No data to process")
            return
        
        # Step 3: Map to ontology
        logger.info("Starting ontology mapping...")
        mapper = ConcordiaOntologyMapper(config)
        rdf_graph = mapper.map()
        
        logger.info(f"Ontology mapping completed. Output saved to {config.output_rdf_path}")
        logger.info(f"RDF graph contains {len(rdf_graph)} triples")
        
        if len(rdf_graph) == 0:
            print("WARNING: RDF graph is empty! Check your ontology classes and data structure.")
            return
        
        # Step 4: Load into Neo4j
        logger.info("Loading RDF data into Neo4j...")
        load_rdf_to_neo4j(rdf_graph, neo4j_uri, username, password)
        
        # Step 5: Validation summary
        logger.info("Validation summary:")
        required_types = mapper.get_required_ontology_types()
        for rdf_type in required_types:
            triples = list(rdf_graph.triples((None, None, rdf_type)))
            logger.info(f"  {rdf_type}: {len(triples)} instances")
        
        logger.info("Concordia to Neo4j pipeline completed successfully!")
        
        # Print summary for verification
        print(f"\nPipeline Summary:")
        print(f"- RDF graph contains {len(rdf_graph)} triples")
        print(f"- Turtle file saved as concordia_neo4j_output.ttl")
        print(f"- Data loaded into Neo4j at {neo4j_uri}")
        print(f"- Check Neo4j browser for imported data")
        print(f"- Buildings: {len(transformed_data.get('buildings', []))}")
        print(f"- Addresses: {len(transformed_data.get('addresses', []))}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    concordia_to_neo4j_pipeline() 