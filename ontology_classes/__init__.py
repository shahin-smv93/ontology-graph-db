# Ontology Mapping Package
# This package contains reusable ontology classes for RDF mapping

from .building import Building
from .address import Address
from .namespaces import *
from .physical_object import PhysicalObject
from .building_space import BuildingSpace
from .sensors import Sensor, Gateway
from .measurement import Measurement, TimeInterval
from .sensor_type_mapping import get_feature_of_interest, validate_sensor_type, get_all_supported_sensor_types

__all__ = [
    'Building', 'Address', 'PhysicalObject', 'BuildingSpace', 
    'Sensor', 'Gateway', 'Measurement', 'TimeInterval',
    'get_feature_of_interest', 'validate_sensor_type', 'get_all_supported_sensor_types'
] 