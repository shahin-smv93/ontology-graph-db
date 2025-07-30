#!/usr/bin/env python3
"""
Main script for running Concordia ontology mapping using the framework.
"""

import logging
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_mapping import OntologyMappingConfig
from ontology_mapping.concordia_transformer import ConcordiaDataTransformer
from ontology_mapping.concordia_mapper import ConcordiaOntologyMapper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the complete ontology mapping pipeline."""
    try:
        # Load configuration
        config_path = "ontology_mapping/concordia_config.json"
        logger.info(f"Loading configuration from {config_path}")
        config = OntologyMappingConfig.from_file(config_path)
        
        # Step 1: Transform data
        logger.info("Starting data transformation...")
        transformer = ConcordiaDataTransformer(config)
        transformed_data = transformer.transform()
        
        logger.info(f"Data transformation completed. Output saved to {config.output_transformed_path}")
        logger.info(f"Summary: {len(transformed_data.get('buildings', []))} buildings, "
                   f"{len(transformed_data.get('addresses', []))} addresses, "
                   f"{len(transformed_data.get('gateways', []))} gateways")
        
        # Step 2: Map to ontology
        logger.info("Starting ontology mapping...")
        mapper = ConcordiaOntologyMapper(config)
        rdf_graph = mapper.map()
        
        logger.info(f"Ontology mapping completed. Output saved to {config.output_rdf_path}")
        logger.info(f"RDF graph contains {len(rdf_graph)} triples")
        
        # Step 3: Validation summary
        logger.info("Validation summary:")
        required_types = mapper.get_required_ontology_types()
        for rdf_type in required_types:
            triples = list(rdf_graph.triples((None, None, rdf_type)))
            logger.info(f"  {rdf_type}: {len(triples)} instances")
        
        logger.info("Ontology mapping pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 