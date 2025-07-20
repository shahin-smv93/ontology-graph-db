"""
Custom exceptions for the ontology mapping framework.
"""

class OntologyMappingError(Exception):
    """Base exception for ontology mapping errors."""
    pass

class ConfigurationError(OntologyMappingError):
    """Raised when there's an issue with configuration."""
    pass

class DataTransformationError(OntologyMappingError):
    """Raised when data transformation fails."""
    pass

class OntologyMappingValidationError(OntologyMappingError):
    """Raised when ontology mapping validation fails."""
    pass

class MissingRequiredFieldError(OntologyMappingError):
    """Raised when a required field is missing from the data."""
    pass 