"""
Configuration management for ontology mapping framework.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from .exceptions import ConfigurationError


@dataclass
class OntologyMappingConfig:
    """
    Configurable mapping for arbitrary JSON schemas into ontology graph builders.
    
    This class provides a flexible, data-driven approach to mapping JSON data
    to ontology structures. Users define field mappings in JSON configuration
    files, making it easy to adapt to different datasets without code changes.
    
    Attributes:
        base_namespace: Base namespace for the organization (e.g., "http://concordia.ca")
        input_data_path: Path to the input sensor data file
        output_transformed_path: Path for the transformed hierarchical data
        output_rdf_path: Path for the generated RDF/Turtle file
        output_debug_path: Path for debug output files
        
        required_fields: List of logical field names that must be present in all records
        field_categories: Mappings by category: logical_name -> JSON key
        
        # Optional configurations
        custom_namespaces: Additional custom namespaces
        validation_rules: Custom validation rules
        
        # Processing settings
        enable_debug: Whether to enable debug output
        validate_data: Whether to validate input data - TODO: add validation rules
        create_time_intervals: Whether to create time interval entities
        create_gateway_relationships: Whether to create sensor-gateway relationships
        ignore_null_values: Whether to ignore null values in optional fields
        ignore_missing_fields: Whether to ignore missing optional fields
        strict_validation: Whether to enforce strict validation rules
    """
    
    # Core configuration
    base_namespace: str
    input_data_path: str
    output_transformed_path: str = "transformed_data.json"
    output_rdf_path: str = "ontology_output.ttl"
    output_debug_path: str = "debug_output.ttl"
    
    # Required data fields (logical names)
    required_fields: List[str] = field(default_factory=lambda: [
        "sensorUID",
        "building",  
        "sensorType"
    ])
    
    # Mappings by category: logical_name -> JSON key
    field_categories: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "spatial": {},
        "sensor": {},
        "building_object": {},
        "address": {}
    })
    
    # Custom namespaces
    custom_namespaces: Dict[str, str] = field(default_factory=dict)
    
    # Validation rules  --- TODO: add validation rules
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Optional settings
    enable_debug: bool = True
    validate_data: bool = True
    create_time_intervals: bool = True
    create_gateway_relationships: bool = True
    
    # Field handling settings
    ignore_null_values: bool = True
    ignore_missing_fields: bool = True
    strict_validation: bool = False
    
    @classmethod
    def from_file(cls, config_path: str) -> 'OntologyMappingConfig':
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {config_path}: {e}")
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to a JSON file."""
        try:
            with open(config_path, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration to {config_path}: {e}")
    
    def validate(self) -> None:
        """Validate the configuration."""
        if not self.base_namespace:
            raise ConfigurationError("base_namespace is required")
        
        if not os.path.exists(self.input_data_path):
            raise ConfigurationError(f"Input data file not found: {self.input_data_path}")
        
        # Ensure output directories exist
        for output_path in [self.output_transformed_path, self.output_rdf_path, self.output_debug_path]:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
    
    def get_uri(self, entity_type: str, identifier: str) -> str:
        """Generate URI for an entity using the base namespace."""
        return f"{self.base_namespace.rstrip('/')}/{entity_type}/{identifier}"
    
    def _get(self, record: Dict[str, Any], key: str) -> Optional[Any]:
        """
        Get field value safely, handling null values and missing fields based on configuration.
        
        Args:
            record: Data record
            key: JSON field name to extract
            
        Returns:
            Field value or None if missing/null and configured to ignore
        """
        if key not in record:
            return None if self.ignore_missing_fields else record.get(key)
        val = record.get(key)
        return None if val is None and self.ignore_null_values else val
    
    def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single data record.
        
        Args:
            record: Raw data record
            
        Returns:
            Dictionary with validation results
        """
        out = {"valid": True, "missing": [], "null": []}
        
        # Check required fields
        for logical in self.required_fields:
            # Find JSON key for this logical name
            json_key = next((v for cat in self.field_categories.values() 
                           for k, v in cat.items() if k == logical), None)
            
            if not json_key or json_key not in record:
                out["missing"].append(logical)
                out["valid"] = False
            elif record.get(json_key) is None and not self.ignore_null_values:
                out["null"].append(logical)
                out["valid"] = False
        
        return out
    
    def extract(self, record: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Extract data for any category using field mappings.
        
        Args:
            record: Data record
            category: Category name (e.g., "spatial", "sensor", "building_object", "address")
            
        Returns:
            Dictionary with extracted data using logical names as keys
        """
        result = {}
        for logical, key in self.field_categories.get(category, {}).items():
            val = self._get(record, key)
            if val is not None:
                result[logical] = val
        return result
    
    def extract_spatial(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spatial hierarchy data."""
        return self.extract(record, "spatial")
    
    def extract_sensor(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sensor data."""
        return self.extract(record, "sensor")
    
    def extract_building_object(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract building object data."""
        return self.extract(record, "building_object")
    
    def extract_address(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract address data."""
        return self.extract(record, "address") 