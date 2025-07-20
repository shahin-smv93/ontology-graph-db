"""
Abstract base class for data transformers.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from .config import OntologyMappingConfig
from .exceptions import DataTransformationError, MissingRequiredFieldError

logger = logging.getLogger(__name__)


class BaseDataTransformer(ABC):
    """
    Abstract base class for transforming sensor data into hierarchical ontology structure.
    
    Users must implement the abstract methods to define how their specific dataset
    should be structured into buildings, floors, rooms, zones, sensors, etc.
    """
    
    def __init__(self, config: OntologyMappingConfig):
        """
        Initialize the transformer with configuration.
        
        Args:
            config: Configuration object containing dataset-specific settings
        """
        self.config = config
        self.config.validate()
        
    def load_data(self) -> List[Dict[str, Any]]:
        """
        Load data from the configured input file.
        
        Returns:
            List of sensor data records
        """
        try:
            with open(self.config.input_data_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise DataTransformationError("Input data must be a list of records")
            
            logger.info(f"Loaded {len(data)} records from {self.config.input_data_path}")
            return data
            
        except Exception as e:
            raise DataTransformationError(f"Failed to load data: {e}")
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        Validate a single data record using enhanced configuration validation.
        
        Args:
            record: Single sensor data record
            
        Returns:
            True if valid, False otherwise
        """
        validation_result = self.config.validate_record(record)
        
        if not validation_result["valid"]:
            # Get sensor ID for logging
            sensor_data = self.get_sensor_data(record)
            sensor_id = sensor_data.get("sensorUID", 'unknown')
            
            if validation_result["missing"]:
                logger.warning(f"Missing required fields {validation_result['missing']} in record: {sensor_id}")
            
            if validation_result["null"]:
                logger.warning(f"Required fields with null values {validation_result['null']} in record: {sensor_id}")
            
            return False
        
        return True
    
    @abstractmethod
    def extract_building_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract building information from a record.
        
        Args:
            record: Single sensor data record
            
        Returns:
            Dictionary containing building information
        """
        raise NotImplementedError("Subclasses must implement extract_building_info")
    
    @abstractmethod
    def extract_address_info(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract address information from a record.
        
        Args:
            record: Single sensor data record
            
        Returns:
            Dictionary containing address information or None
        """
        raise NotImplementedError("Subclasses must implement extract_address_info")
    
    @abstractmethod
    def extract_spatial_hierarchy(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract spatial hierarchy information (floor, room, zone) from a record.
        
        Args:
            record: Single sensor data record
            
        Returns:
            Dictionary containing spatial hierarchy information
        """
        raise NotImplementedError("Subclasses must implement extract_spatial_hierarchy")
    
    @abstractmethod
    def extract_sensor_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sensor information from a record.
        
        Args:
            record: Single sensor data record
            
        Returns:
            Dictionary containing sensor information
        """
        raise NotImplementedError("Subclasses must implement extract_sensor_info")
    
    @abstractmethod
    def extract_measurement_info(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract measurement information from a record.
        
        Args:
            record: Single sensor data record
            
        Returns:
            Dictionary containing measurement information or None
        """
        raise NotImplementedError("Subclasses must implement extract_measurement_info")
    
    @abstractmethod
    def create_hierarchical_structure(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create the hierarchical structure from the transformed data.
        
        Args:
            data: List of transformed sensor records
            
        Returns:
            Dictionary containing the hierarchical structure
        """
        raise NotImplementedError("Subclasses must implement create_hierarchical_structure")
    
    def transform(self) -> Dict[str, Any]:
        """
        Main transformation method that orchestrates the entire process.
        
        Returns:
            Transformed hierarchical data structure
        """
        try:
            # Load raw data
            raw_data = self.load_data()
            
            if not raw_data:
                raise DataTransformationError("No data loaded")
            
            # Validate data if enabled
            if self.config.validate_data:
                valid_data = [record for record in raw_data if self.validate_record(record)]
                logger.info(f"Validated {len(valid_data)} out of {len(raw_data)} records")
            else:
                valid_data = raw_data
            
            # Create hierarchical structure
            hierarchical_data = self.create_hierarchical_structure(valid_data)
            
            # Save transformed data
            with open(self.config.output_transformed_path, 'w') as f:
                json.dump(hierarchical_data, f, indent=2)
            
            logger.info(f"Transformed data saved to {self.config.output_transformed_path}")
            return hierarchical_data
            
        except Exception as e:
            raise DataTransformationError(f"Transformation failed: {e}")
    

    
    def get_field_value_safe(self, record: Dict[str, Any], field_name: str) -> Optional[Any]:
        """
        Get field value safely, handling null values and missing fields.
        
        Args:
            record: Data record
            field_name: Field name to extract
            
        Returns:
            Field value or None if missing/null and configured to ignore
        """
        return self.config._get(record, field_name)
    
    def extract_category(self, record: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Extract data for a specific category using the new unified approach.
        
        Args:
            record: Data record
            category: Category name (e.g., "spatial", "sensor", "building_object", "address")
            
        Returns:
            Dictionary with extracted data using logical names as keys
        """
        return self.config.extract(record, category)
    
    # Convenience methods for common categories
    def get_spatial_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Get spatial hierarchy data."""
        return self.config.extract_spatial(record)
    
    def get_sensor_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Get sensor data."""
        return self.config.extract_sensor(record)
    
    def get_building_object_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Get building object data."""
        return self.config.extract_building_object(record)
    
    def get_address_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Get address data."""
        return self.config.extract_address(record)
    
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