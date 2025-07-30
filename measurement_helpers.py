#!/usr/bin/env python3
"""
Helper functions for creating Measurement instances from sensor data
"""

from ontology_classes.measurement import Measurement, TimeInterval
from ontology_classes.sensor_type_mapping import get_feature_of_interest
from rdflib import URIRef

def create_measurement_from_sensor_data(sensor_data, measurement_id=None):
    """
    Create a Measurement instance from sensor data.
    
    Args:
        sensor_data (dict): Dictionary containing sensor information
        measurement_id (str, optional): Unique identifier for the measurement
        
    Returns:
        Measurement: A configured Measurement instance
    """
    # Extract sensor information
    sensor_uid = sensor_data.get('sensorUID')
    sensor_type = sensor_data.get('sensorType')
    unit = sensor_data.get('unit')
    time_interval_value = sensor_data.get('timeInterval')
    
    # Create measurement URI using sensorUID for linking
    if measurement_id:
        measurement_uri = f"http://example.com/measurement/{sensor_uid}/{measurement_id}"
    else:
        measurement_uri = f"http://example.com/measurement/{sensor_uid}/default"
    
    # Get the appropriate FeatureOfInterest based on sensor type
    measured_property = get_feature_of_interest(sensor_type)
    
    # Create time interval if specified
    time_interval = None
    if time_interval_value:
        time_interval_uri = f"http://example.com/time/{sensor_uid}/interval"
        time_interval = TimeInterval(
            uri=time_interval_uri,
            time_interval=float(time_interval_value)
        )
    
    # Create and return the measurement
    measurement = Measurement(
        uri=measurement_uri,
        time_interval=time_interval,
        measured_property=measured_property,
        unit=unit,
        sensor_type=sensor_type
    )
    
    return measurement

def create_measurements_for_sensor(sensor_data):
    """
    Create multiple measurements for a sensor that has multiple sensor types.
    This is useful for sensors that measure multiple properties (like IAQ sensors).
    
    Args:
        sensor_data (dict): Dictionary containing sensor information
        
    Returns:
        list: List of Measurement instances
    """
    measurements = []
    sensor_uid = sensor_data.get('sensorUID')
    
    # Check if this sensor has multiple measurements (e.g., IAQ sensors)
    # Look for sensor types that end with specific suffixes
    base_sensor_uid = sensor_uid.split('_')[0] if '_' in sensor_uid else sensor_uid
    
    # Create a measurement for the main sensor type
    main_measurement = create_measurement_from_sensor_data(sensor_data)
    if main_measurement.measured_property:  # Only add if we have a valid mapping
        measurements.append(main_measurement)
    
    return measurements 