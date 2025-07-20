#!/usr/bin/env python3
"""
Enhanced Sensor Hierarchy Transformer
Extends the existing hierarchy to include sensors and their measurements
"""

import json
import os
import sys
from collections import defaultdict

# Add the parent directory to the path to import ontology_classes
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ontology_classes import (
    Building, Address, BuildingSpace, PhysicalObject, 
    Sensor, Gateway, Measurement, TimeInterval,
    get_feature_of_interest
)

def create_address_key(street_name, street_number, postal_code):
    return f"{street_number}_{street_name}_{postal_code}".replace(" ", "_")

def serialize_physical_object(obj):
    """Serialize a PhysicalObject (desk, sensor, or gateway)"""
    result = {
        "uri": str(obj.uri),
        "label": obj.label,
    }
    
    # Add desk-specific properties
    if hasattr(obj, 'deskDescription') and obj.deskDescription:
        result["deskDescription"] = obj.deskDescription
    
    # Add sensor-specific properties
    if isinstance(obj, Sensor):
        result["sensorUID"] = obj.sensorUID
        result["sensorId"] = obj.sensorId
        result["vendorName"] = obj.vendorName
        result["installationDate"] = obj.installationDate
        result["sensorType"] = getattr(obj, 'sensor_type', None)
        
        # Add gateway connection if exists
        if hasattr(obj, 'gateway_connection') and obj.gateway_connection:
            result["gateway_connection"] = str(obj.gateway_connection.uri)
        
        # Add measurement if exists
        if obj.has_measurement:
            result["measurement"] = {
                "uri": str(obj.has_measurement.uri),
                "measured_property": str(obj.has_measurement.measured_property) if obj.has_measurement.measured_property else None,
                "unit": obj.has_measurement.unit,
                "sensor_type": obj.has_measurement.sensor_type
            }
            # Add time interval if exists
            if obj.has_measurement.time_interval:
                result["measurement"]["time_interval"] = str(obj.has_measurement.time_interval.time_interval)
    
    # Add gateway-specific properties
    if isinstance(obj, Gateway):
        result["gatewayUID"] = obj.gatewayUID
    
    # If this is a desk (PhysicalObject) and has sensors in 'contains', serialize them
    if hasattr(obj, 'contains') and obj.contains:
        result["contains"] = [serialize_physical_object(child) for child in obj.contains]
    
    return result

def serialize_building_space(space):
    """Serialize a BuildingSpace with all its contents"""
    # Serialize physical objects (desks and sensors)
    building_objects = [
        serialize_physical_object(obj)
        for obj in getattr(space, 'building_object', [])
    ]
    
    # Serialize nested spaces
    nested_spaces = [serialize_building_space(s) for s in getattr(space, 'spaces', [])]
    
    result = {
        "uri": str(space.uri),
        "label": space.label,
        "spaces": nested_spaces,
        "building_object": building_objects
    }
    return result

def create_sensor_from_data(sensor_data, contained_in):
    """Create a Sensor instance from sensor data"""
    sensor_uid = sensor_data.get('sensorUID')
    sensor_id = sensor_data.get('sensorId')
    sensor_type = sensor_data.get('sensorType')
    
    # Create sensor URI
    sensor_uri = f"http://concordia.ca/sensor/{sensor_uid}"
    
    # Create sensor instance
    sensor = Sensor(
        uri=sensor_uri,
        sensorUID=sensor_uid,
        sensorId=sensor_id,
        vendorName=sensor_data.get('vendorName'),
        installationDate=sensor_data.get('installationDate'),
        contained_in=contained_in
    )
    
    # Add sensor type for measurement mapping
    sensor.sensor_type = sensor_type
    
    # Create measurement if sensor type is supported
    if sensor_type and get_feature_of_interest(sensor_type):
        # Create measurement with time interval
        measurement_uri = f"http://example.com/measurement/{sensor_uid}/{sensor_type}_measurement"
        measured_property = get_feature_of_interest(sensor_type)
        
        # Create time interval if available
        time_interval = None
        time_interval_str = sensor_data.get('timeInterval')
        if time_interval_str:
            time_interval_uri = f"http://example.com/timeInterval/{time_interval_str}"
            time_interval = TimeInterval(
                uri=time_interval_uri,
                time_interval=float(time_interval_str) if time_interval_str else None
            )
        
        measurement = Measurement(
            uri=measurement_uri,
            time_interval=time_interval,
            measured_property=measured_property,
            unit=sensor_data.get('unit'),
            sensor_type=sensor_type
        )
        sensor.has_measurement = measurement
    
    return sensor

def main():
    input_file = "sensors_file/concordia_sensors_finalized.json"
    output_file = "enhanced_transformed_data.json"
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Group by building, floor, mainRoom, room/zone
    buildings = {}
    addresses = {}
    floors = {}
    main_rooms = {}
    rooms = {}
    zones = {}
    desks = {}
    sensors = {}
    gateways = {}
    
    print(f"Processing {len(data)} sensor records...")
    
    for entry in data:
        building_code = entry.get('building')
        floor_code = entry.get('floor')
        main_room_code = entry.get('mainRoom')
        room_code = entry.get('room')
        zone_code = entry.get('zone')
        desk_id = entry.get('deskID')
        desk_desc = entry.get('deskDescription')
        street_name = entry.get('street_name')
        street_number = entry.get('street_number')
        postal_code = entry.get('postal_code')
        sensor_type = entry.get('sensorType')
        gateway_uid = entry.get('gatewayUID')
        
        # Skip if missing required fields
        if not all([building_code, floor_code, main_room_code]):
            print(f"Skipping sensor {entry.get('sensorUID')} - missing required location data")
            continue
        
        # Create address
        address_key = create_address_key(street_name, street_number, postal_code)
        address_uri = f"http://concordia.ca/address/{address_key}"
        if address_key not in addresses:
            addresses[address_key] = Address(
                uri=address_uri,
                street_name=street_name,
                street_number=street_number,
                postal_code=postal_code
            )
        
        # Create building
        building_uri = f"http://concordia.ca/building/{building_code}"
        if building_code not in buildings:
            buildings[building_code] = Building(
                uri=building_uri,
                label=building_code,
                address=addresses[address_key],
                spaces=[]
            )
        
        # Create floor
        floor_uri = f"http://concordia.ca/floor/{floor_code}"
        if floor_code not in floors:
            floors[floor_code] = BuildingSpace(
                uri=floor_uri,
                label=floor_code,
                building=buildings[building_code],
                spaces=[]
            )
            buildings[building_code].spaces.append(floors[floor_code])
        
        # Create main room
        main_room_uri = f"http://concordia.ca/mainRoom/{main_room_code}"
        if main_room_code not in main_rooms:
            main_rooms[main_room_code] = BuildingSpace(
                uri=main_room_uri,
                label=main_room_code,
                parent_space=floors[floor_code],
                spaces=[]
            )
            floors[floor_code].spaces.append(main_rooms[main_room_code])
        
        # Create gateway if not exists and place it in the main room
        if gateway_uid and gateway_uid not in gateways:
            gateway_uri = f"http://concordia.ca/gateway/{gateway_uid}"
            gateway = Gateway(
                uri=gateway_uri,
                gatewayUID=gateway_uid,
                label=f"Gateway {gateway_uid}",
                contained_in=main_rooms[main_room_code]
            )
            gateways[gateway_uid] = gateway
            # Add gateway to the main room's building objects
            main_rooms[main_room_code].building_object.append(gateway)
        
        # Handle desk sensors (must have deskID)
        if sensor_type == 'deskSensor':
            if not desk_id:
                print(f"Warning: Desk sensor {entry.get('sensorUID')} missing deskID")
                continue
                
            # Create room if exists
            if room_code:
                room_uri = f"http://concordia.ca/room/{room_code}"
                if room_code not in rooms:
                    rooms[room_code] = BuildingSpace(
                        uri=room_uri,
                        label=room_code,
                        parent_space=main_rooms[main_room_code],
                        spaces=[]
                    )
                    main_rooms[main_room_code].spaces.append(rooms[room_code])
                desk_parent = rooms[room_code]
            else:
                desk_parent = main_rooms[main_room_code]
            
            # Create desk if not exists
            if desk_id not in desks:
                desk_uri = f"http://concordia.ca/desk/{desk_id}"
                desk_obj = PhysicalObject(
                    uri=desk_uri,
                    label=desk_id,
                    contained_in=desk_parent
                )
                desk_obj.deskDescription = desk_desc
                desks[desk_id] = desk_obj
                desk_parent.building_object.append(desk_obj)
            
            # Create sensor (contained in desk)
            sensor = create_sensor_from_data(entry, desks[desk_id])
            if sensor.sensorUID not in sensors:
                sensors[sensor.sensorUID] = sensor
                desks[desk_id].contains.append(sensor)
                # Connect to gateway
                if gateway_uid and gateway_uid in gateways:
                    sensor.gateway_connection = gateways[gateway_uid]
        
        # Handle other sensors (non-desk sensors)
        else:
            # Create zone if exists
            if zone_code:
                zone_uri = f"http://concordia.ca/zone/{zone_code}"
                if zone_code not in zones:
                    zones[zone_code] = BuildingSpace(
                        uri=zone_uri,
                        label=zone_code,
                        parent_space=main_rooms[main_room_code],
                        spaces=[]
                    )
                    main_rooms[main_room_code].spaces.append(zones[zone_code])
                sensor_parent = zones[zone_code]
            else:
                sensor_parent = main_rooms[main_room_code]
            
            # Create sensor (contained in zone or main room)
            sensor = create_sensor_from_data(entry, sensor_parent)
            if sensor.sensorUID not in sensors:
                sensors[sensor.sensorUID] = sensor
                sensor_parent.building_object.append(sensor)
                
                # Connect to gateway
                if gateway_uid and gateway_uid in gateways:
                    sensor.gateway_connection = gateways[gateway_uid]
    
    # Prepare output structure
    output = {
        "buildings": [],
        "addresses": [],
        "gateways": []
    }
    
    # Serialize buildings with full hierarchy
    for b in buildings.values():
        building_dict = {
            "uri": str(b.uri),
            "label": b.label,
            "address_uri": str(b.address.uri) if b.address else None,
            "spaces": [serialize_building_space(f) for f in b.spaces]
        }
        output["buildings"].append(building_dict)
    
    # Serialize addresses
    for a in addresses.values():
        output["addresses"].append({
            "uri": str(a.uri),
            "street_name": a.street_name,
            "street_number": a.street_number,
            "postal_code": a.postal_code
        })
    
    # Serialize gateways
    for g in gateways.values():
        output["gateways"].append({
            "uri": str(g.uri),
            "gatewayUID": g.gatewayUID,
            "label": g.label
        })
    
    # Save output
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print(f"\nEnhanced sensor hierarchy transformed data saved to {output_file}")
    print(f"Summary:")
    print(f"- Buildings: {len(buildings)}")
    print(f"- Floors: {len(floors)}")
    print(f"- MainRooms: {len(main_rooms)}")
    print(f"- Rooms: {len(rooms)}")
    print(f"- Zones: {len(zones)}")
    print(f"- Desks: {len(desks)}")
    print(f"- Sensors: {len(sensors)}")
    print(f"- Gateways: {len(gateways)}")
    
    # Count measurements
    measurement_count = sum(1 for sensor in sensors.values() if sensor.has_measurement)
    print(f"- Measurements: {measurement_count}")
    
    # Print some examples of sensor placement
    print(f"\nSensor placement examples:")
    desk_sensor_count = sum(1 for sensor in sensors.values() if sensor.sensor_type == 'deskSensor')
    other_sensor_count = len(sensors) - desk_sensor_count
    print(f"- Desk sensors: {desk_sensor_count}")
    print(f"- Other sensors: {other_sensor_count}")

if __name__ == "__main__":
    main() 