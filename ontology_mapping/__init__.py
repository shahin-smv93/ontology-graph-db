"""
Ontology Mapping Framework
A general, extensible framework for mapping sensor and building data to ontologies.
"""

from .config import OntologyMappingConfig
from .base_transformer import BaseDataTransformer
from .base_mapper import BaseOntologyMapper
from .exceptions import OntologyMappingError

__all__ = [
    'OntologyMappingConfig',
    'BaseDataTransformer', 
    'BaseOntologyMapper',
    'OntologyMappingError'
] 