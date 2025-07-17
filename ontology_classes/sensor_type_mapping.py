#!/usr/bin/env python3
"""
Sensor Type to FeatureOfInterest Mapping
This module provides mappings between sensor types in JSON files and 
predefined saref:FeatureOfInterest instances from extensions.ttl
"""

from rdflib import URIRef
from ontology_classes.namespaces import bigg

# Mapping from sensor types (as they appear in JSON) to FeatureOfInterest URIs
SENSOR_TYPE_TO_FEATURE_MAPPING = {
    # Temperature sensors
    "temperatureSensor": bigg.TemperatureProperty,
    "temp": bigg.TemperatureProperty,
    
    # CO2 sensors
    "co2Sensor": bigg.CO2Property,
    "co2": bigg.CO2Property,
    
    # Humidity sensors
    "relativeHumiditySensor": bigg.RelativeHumidityProperty,
    "humidity": bigg.RelativeHumidityProperty,
    "rh": bigg.RelativeHumidityProperty,
    
    # VOC sensors
    "vocSensor": bigg.VOCProperty,
    "voc": bigg.VOCProperty,
    
    # Ambient sound sensors
    "ambientSoundSensor": bigg.AmbientSoundProperty,
    "ambsound": bigg.AmbientSoundProperty,
    "sound": bigg.AmbientSoundProperty,
    
    # Illuminance sensors
    "illuminanceSensor": bigg.IlluminanceProperty,
    "illum": bigg.IlluminanceProperty,
    "light": bigg.IlluminanceProperty,
    
    # Particulate matter sensors
    "pm1Sensor": bigg.PM1Property,
    "pm1": bigg.PM1Property,
    
    "pm2_5Sensor": bigg.PM25Property,
    "pm2.5": bigg.PM25Property,
    "pm2_5": bigg.PM25Property,
    
    "pm4Sensor": bigg.PM4Property,
    "pm4": bigg.PM4Property,
    
    "pm10Sensor": bigg.PM10Property,
    "pm10": bigg.PM10Property,
    
    # Occupancy/desk sensors
    "deskSensor": bigg.OccupancyProperty,
    "occupancy": bigg.OccupancyProperty,
    "desk": bigg.OccupancyProperty,
}

def get_feature_of_interest(sensor_type):
    """
    Get the appropriate FeatureOfInterest URI for a given sensor type.
    
    Args:
        sensor_type (str): The sensor type from the JSON file
        
    Returns:
        URIRef: The FeatureOfInterest URI, or None if not found
    """
    return SENSOR_TYPE_TO_FEATURE_MAPPING.get(sensor_type)

def get_all_supported_sensor_types():
    """
    Get a list of all supported sensor types.
    
    Returns:
        list: List of supported sensor type strings
    """
    return list(SENSOR_TYPE_TO_FEATURE_MAPPING.keys())

def validate_sensor_type(sensor_type):
    """
    Check if a sensor type is supported.
    
    Args:
        sensor_type (str): The sensor type to validate
        
    Returns:
        bool: True if supported, False otherwise
    """
    return sensor_type in SENSOR_TYPE_TO_FEATURE_MAPPING 