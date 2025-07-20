"""
Abstract base class for ontology mappers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from rdflib import Graph, URIRef
from .config import OntologyMappingConfig
from .exceptions import OntologyMappingError, OntologyMappingValidationError

logger = logging.getLogger(__name__)


class BaseOntologyMapper(ABC):
    """
    Abstract base class for mapping hierarchical data to RDF ontology.
    
    Users must implement the abstract methods to define how their specific
    hierarchical structure should be mapped to ontology classes and relationships.
    """
    
    def __init__(self, config: OntologyMappingConfig):
        """
        Initialize the mapper with configuration.
        
        Args:
            config: Configuration object containing dataset-specific settings
        """
        self.config = config
        self.config.validate()
        
    def load_transformed_data(self) -> Dict[str, Any]:
        """
        Load the transformed hierarchical data.
        
        Returns:
            Transformed hierarchical data structure
        """
        try:
            import json
            with open(self.config.output_transformed_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded transformed data from {self.config.output_transformed_path}")
            return data
            
        except Exception as e:
            raise OntologyMappingError(f"Failed to load transformed data: {e}")
    
    @abstractmethod
    def create_building_objects(self, data: Dict[str, Any]) -> List[Any]:
        """
        Create building objects from the hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            List of building objects
        """
        raise NotImplementedError("Subclasses must implement create_building_objects")
    
    @abstractmethod
    def create_address_objects(self, data: Dict[str, Any]) -> List[Any]:
        """
        Create address objects from the hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            List of address objects
        """
        raise NotImplementedError("Subclasses must implement create_address_objects")
    
    @abstractmethod
    def create_spatial_objects(self, data: Dict[str, Any]) -> List[Any]:
        """
        Create spatial objects (floors, rooms, zones) from the hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            List of spatial objects
        """
        raise NotImplementedError("Subclasses must implement create_spatial_objects")
    
    @abstractmethod
    def create_sensor_objects(self, data: Dict[str, Any]) -> List[Any]:
        """
        Create sensor objects from the hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            List of sensor objects
        """
        raise NotImplementedError("Subclasses must implement create_sensor_objects")
    
    @abstractmethod
    def create_measurement_objects(self, data: Dict[str, Any]) -> List[Any]:
        """
        Create measurement objects from the hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            List of measurement objects
        """
        raise NotImplementedError("Subclasses must implement create_measurement_objects")
    
    @abstractmethod
    def create_gateway_objects(self, data: Dict[str, Any]) -> List[Any]:
        """
        Create gateway objects from the hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            List of gateway objects
        """
        raise NotImplementedError("Subclasses must implement create_gateway_objects")
    
    @abstractmethod
    def setup_namespaces(self, graph: Graph) -> None:
        """
        Set up ontology namespaces in the RDF graph.
        
        Args:
            graph: RDF graph to add namespaces to
        """
        raise NotImplementedError("Subclasses must implement setup_namespaces")
    
    def create_rdf_graph(self, data: Dict[str, Any]) -> Graph:
        """
        Create RDF graph from hierarchical data.
        
        Args:
            data: Transformed hierarchical data
            
        Returns:
            RDF graph containing ontology triples
        """
        try:
            graph = Graph()
            
            # Setup namespaces
            self.setup_namespaces(graph)
            
            # Create ontology objects
            buildings = self.create_building_objects(data)
            addresses = self.create_address_objects(data)
            spatial_objects = self.create_spatial_objects(data)
            sensors = self.create_sensor_objects(data)
            measurements = self.create_measurement_objects(data)
            gateways = self.create_gateway_objects(data)
            
            # Add all objects to graph
            all_objects = buildings + addresses + spatial_objects + sensors + measurements + gateways
            
            for obj in all_objects:
                if hasattr(obj, 'add_to_graph'):
                    obj.add_to_graph(graph)
                else:
                    logger.warning(f"Object {obj} does not have add_to_graph method")
            
            logger.info(f"Created RDF graph with {len(graph)} triples")
            return graph
            
        except Exception as e:
            raise OntologyMappingError(f"Failed to create RDF graph: {e}")
    
    def save_rdf_graph(self, graph: Graph, output_path: Optional[str] = None) -> None:
        """
        Save RDF graph to file.
        
        Args:
            graph: RDF graph to save
            output_path: Optional custom output path
        """
        try:
            output_path = output_path or self.config.output_rdf_path
            
            # Save as Turtle
            turtle_data = graph.serialize(format='turtle')
            with open(output_path, 'w') as f:
                f.write(turtle_data)
            
            logger.info(f"RDF graph saved to {output_path}")
            
            # Save debug version if enabled
            if self.config.enable_debug:
                debug_data = graph.serialize(format='turtle')
                with open(self.config.output_debug_path, 'w') as f:
                    f.write(debug_data)
                logger.info(f"Debug RDF graph saved to {self.config.output_debug_path}")
                
        except Exception as e:
            raise OntologyMappingError(f"Failed to save RDF graph: {e}")
    
    def validate_rdf_graph(self, graph: Graph) -> bool:
        """
        Validate the generated RDF graph.
        
        Args:
            graph: RDF graph to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - check if graph has content
            if len(graph) == 0:
                logger.error("RDF graph is empty")
                return False
            
            # Check for required ontology types
            required_types = self.get_required_ontology_types()
            for rdf_type in required_types:
                triples = list(graph.triples((None, None, rdf_type)))
                if not triples:
                    logger.warning(f"No instances of {rdf_type} found in graph")
            
            logger.info("RDF graph validation passed")
            return True
            
        except Exception as e:
            logger.error(f"RDF graph validation failed: {e}")
            return False
    
    @abstractmethod
    def get_required_ontology_types(self) -> List[URIRef]:
        """
        Get list of required ontology types that should be present in the graph.
        
        Returns:
            List of required RDF types
        """
        raise NotImplementedError("Subclasses must implement get_required_ontology_types")
    
    def map(self) -> Graph:
        """
        Main mapping method that orchestrates the entire ontology mapping process.
        
        Returns:
            RDF graph containing ontology triples
        """
        try:
            # Load transformed data
            data = self.load_transformed_data()
            
            if not data:
                raise OntologyMappingError("No transformed data loaded")
            
            # Create RDF graph
            graph = self.create_rdf_graph(data)
            
            # Validate graph if enabled
            if self.config.validate_data:
                if not self.validate_rdf_graph(graph):
                    raise OntologyMappingValidationError("RDF graph validation failed")
            
            # Save graph
            self.save_rdf_graph(graph)
            
            return graph
            
        except Exception as e:
            raise OntologyMappingError(f"Ontology mapping failed: {e}")
    
    def create_uri(self, entity_type: str, identifier: str) -> str:
        """
        Create URI for an entity using the configured namespace.
        
        Args:
            entity_type: Type of entity (e.g., 'building', 'sensor')
            identifier: Unique identifier for the entity
            
        Returns:
            Full URI for the entity
        """
        return self.config.get_uri(entity_type, identifier) 