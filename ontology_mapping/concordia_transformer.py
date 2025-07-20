"""
Concrete implementation of BaseDataTransformer for Concordia dataset.
"""

import sys
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Add the parent directory to the path to import ontology_classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_transformer import BaseDataTransformer
from .config import OntologyMappingConfig
from ontology_classes import (
    Building, Address, BuildingSpace, PhysicalObject, 
    Sensor, Gateway, Measurement, TimeInterval,
    get_feature_of_interest
)


class ConcordiaDataTransformer(BaseDataTransformer):
    """
    Concrete implementation for transforming Concordia sensor data.
    """
    
    def extract_building_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract building information from a record."""
        spatial_data = self.get_spatial_data(record)
        building_code = spatial_data.get("building")
        
        if not building_code:
            raise ValueError("Building information is required")
        
        return {
            "uri": self.create_uri("building", building_code),
            "label": building_code,
            "address_uri": self._create_address_uri(record)
        }
    
    def extract_address_info(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract address information from a record."""
        address_data = self.get_address_data(record)
        
        # Check for minimum required address fields
        street_name = address_data.get("street_name")
        street_number = address_data.get("street_number")
        postal_code = address_data.get("postal_code")
        
        if not all([street_name, street_number, postal_code]):
            return None
        
        address_key = f"{street_number}_{street_name}_{postal_code}".replace(" ", "_")
        
        return {
            "uri": self.create_uri("address", address_key),
            **address_data
        }
    
    def extract_spatial_hierarchy(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract spatial hierarchy information from a record."""
        return self.get_spatial_data(record)
    
    def extract_sensor_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sensor information from a record."""
        sensor_data = self.get_sensor_data(record)
        building_object_data = self.get_building_object_data(record)
        
        sensor_uid = sensor_data.get("sensorUID")
        if not sensor_uid:
            raise ValueError("Sensor UID is required")
        
        return {
            "uri": self.create_uri("sensor", sensor_uid),
            **sensor_data,
            **building_object_data
        }
    
    def extract_measurement_info(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract measurement information from a record."""
        sensor_data = self.get_sensor_data(record)
        sensor_type = sensor_data.get("sensorType")
        time_interval = sensor_data.get("timeInterval")
        
        if not sensor_type or not get_feature_of_interest(sensor_type):
            return None
        
        sensor_uid = sensor_data.get("sensorUID")
        measured_property = get_feature_of_interest(sensor_type)
        
        return {
            "uri": f"http://concordia.ca/measurement/{sensor_uid}/{sensor_type}_measurement",
            "measured_property": str(measured_property),
            "sensor_type": sensor_type,
            "time_interval": time_interval,
            "unit": sensor_data.get("unit")
        }
    
    def create_hierarchical_structure(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the hierarchical structure from the transformed data."""
        buildings = {}
        addresses = {}
        floors = {}
        main_rooms = {}
        rooms = {}
        zones = {}
        desks = {}
        sensors = {}
        gateways = {}
        
        for record in data:
            # Extract information
            building_info = self.extract_building_info(record)
            address_info = self.extract_address_info(record)
            spatial_info = self.extract_spatial_hierarchy(record)
            sensor_info = self.extract_sensor_info(record)
            measurement_info = self.extract_measurement_info(record)
            
            # Create address if not exists
            if address_info:
                address_key = address_info["uri"]
                if address_key not in addresses:
                    addresses[address_key] = address_info
            
            # Create building if not exists
            building_key = building_info["label"]
            if building_key not in buildings:
                buildings[building_key] = building_info
            
            # Create floor if not exists
            floor_key = spatial_info["floor"]
            if floor_key not in floors:
                floors[floor_key] = {
                    "uri": self.create_uri("floor", floor_key),
                    "label": floor_key,
                    "building": buildings[building_key]["uri"],
                    "spaces": []
                }
            
            # Create main room if not exists
            main_room_key = spatial_info["mainRoom"]
            if main_room_key not in main_rooms:
                main_rooms[main_room_key] = {
                    "uri": self.create_uri("mainRoom", main_room_key),
                    "label": main_room_key,
                    "parent_space": floors[floor_key]["uri"],
                    "spaces": [],
                    "building_object": []
                }
                floors[floor_key]["spaces"].append(main_rooms[main_room_key])
            
            # Create gateway if not exists
            gateway_uid = sensor_info.get("gatewayUID")
            if gateway_uid and gateway_uid not in gateways:
                gateways[gateway_uid] = {
                    "uri": self.create_uri("gateway", gateway_uid),
                    "gatewayUID": gateway_uid,
                    "label": f"Gateway {gateway_uid}",
                    "contained_in": main_rooms[main_room_key]["uri"]
                }
                main_rooms[main_room_key]["building_object"].append(gateways[gateway_uid])
            
            # Handle desk sensors
            if sensor_info["sensorType"] == "deskSensor":
                desk_id = sensor_info.get("deskID")
                if desk_id:
                    if desk_id not in desks:
                        room_key = spatial_info.get("room")
                        
                        # Determine desk parent based on whether room exists
                        if room_key:
                            # Create room if not exists
                            if room_key not in rooms:
                                rooms[room_key] = {
                                    "uri": self.create_uri("room", room_key),
                                    "label": room_key,
                                    "parent_space": main_rooms[main_room_key]["uri"],
                                    "spaces": [],
                                    "building_object": []
                                }
                                main_rooms[main_room_key]["spaces"].append(rooms[room_key])
                            desk_parent = rooms[room_key]
                        else:
                            # Room is null, desk goes directly under main room
                            desk_parent = main_rooms[main_room_key]
                        
                        # Create desk as a PhysicalObject
                        desks[desk_id] = {
                            "uri": self.create_uri("desk", desk_id),
                            "label": desk_id,
                            "deskDescription": sensor_info.get("deskDescription"),
                            "contained_in": desk_parent["uri"],
                            "contains": []
                        }
                        desk_parent["building_object"].append(desks[desk_id])
                    
                    # Add sensor to desk's contains (sensors are contained by desks)
                    sensor_with_measurement = self._create_sensor_with_measurement(sensor_info, measurement_info)
                    sensors[sensor_info["sensorUID"]] = sensor_with_measurement
                    desks[desk_id]["contains"].append(sensor_with_measurement)
            
            # Handle other sensors (IAQ sensors)
            else:
                zone_key = spatial_info.get("zone")
                
                # Determine sensor parent based on whether zone exists
                if zone_key:
                    # Create zone if not exists
                    if zone_key not in zones:
                        zones[zone_key] = {
                            "uri": self.create_uri("zone", zone_key),
                            "label": zone_key,
                            "parent_space": main_rooms[main_room_key]["uri"],
                            "spaces": [],
                            "building_object": []
                        }
                        main_rooms[main_room_key]["spaces"].append(zones[zone_key])
                    sensor_parent = zones[zone_key]
                else:
                    # Zone is null, sensor goes directly under main room
                    sensor_parent = main_rooms[main_room_key]
                
                # Add sensor to zone or main room's building_object
                sensor_with_measurement = self._create_sensor_with_measurement(sensor_info, measurement_info)
                sensors[sensor_info["sensorUID"]] = sensor_with_measurement
                sensor_parent["building_object"].append(sensor_with_measurement)
        
        # Connect buildings to their floors
        for floor in floors.values():
            building_uri = floor["building"]
            # Find building by URI
            for building in buildings.values():
                if building["uri"] == building_uri:
                    building["spaces"] = building.get("spaces", [])
                    building["spaces"].append(floor)
                    break
        
        # Convert to final structure
        return {
            "buildings": list(buildings.values()),
            "addresses": list(addresses.values())
        }
    
    def _create_sensor_with_measurement(self, sensor_info: Dict[str, Any], measurement_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create sensor object with measurement if available."""
        sensor_obj = sensor_info.copy()
        if measurement_info:
            sensor_obj["measurement"] = measurement_info
        return sensor_obj
    
    def _create_address_uri(self, record: Dict[str, Any]) -> Optional[str]:
        """Create address URI from record."""
        address_info = self.extract_address_info(record)
        return address_info["uri"] if address_info else None 