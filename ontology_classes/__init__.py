# Ontology Mapping Package
# This package contains reusable ontology classes for RDF mapping

from .building import Building
from .address import Address
from .namespaces import *
from .physical_object import PhysicalObject
from .building_space import BuildingSpace

__all__ = ['Building', 'Address', 'PhysicalObject', 'BuildingSpace'] 