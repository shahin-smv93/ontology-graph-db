import json
import os
from collections import defaultdict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ontology_classes import Building, Address, BuildingSpace, PhysicalObject

def create_address_key(street_name, street_number, postal_code):
    return f"{street_number}_{street_name}_{postal_code}".replace(" ", "_")

def serialize_physical_object(obj):
    return {
        "uri": str(obj.uri),
        "label": obj.label,
        "deskDescription": getattr(obj, 'deskDescription', None)
    }

def serialize_building_space(space):
    # Serialize desks (building_object)
    building_objects = [
        serialize_physical_object(desk)
        for desk in getattr(space, 'building_object', [])
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

def main():
    input_file = "sensors_file/concordia_sensors_finalized.json"
    output_file = "transformed_data.json"
    
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
        
        # Address
        address_key = create_address_key(street_name, street_number, postal_code)
        address_uri = f"http://concordia.ca/address/{address_key}"
        if address_key not in addresses:
            addresses[address_key] = Address(
                uri=address_uri,
                street_name=street_name,
                street_number=street_number,
                postal_code=postal_code
            )
        
        # Building
        building_uri = f"http://concordia.ca/building/{building_code}"
        if building_code not in buildings:
            buildings[building_code] = Building(
                uri=building_uri,
                label=building_code,
                address=addresses[address_key],
                spaces=[]
            )
        
        # Floor
        floor_uri = f"http://concordia.ca/floor/{floor_code}"
        if floor_code not in floors:
            floors[floor_code] = BuildingSpace(
                uri=floor_uri,
                label=floor_code,
                building=buildings[building_code],
                spaces=[]
            )
            buildings[building_code].spaces.append(floors[floor_code])
        
        # MainRoom
        main_room_uri = f"http://concordia.ca/mainRoom/{main_room_code}"
        if main_room_code not in main_rooms:
            main_rooms[main_room_code] = BuildingSpace(
                uri=main_room_uri,
                label=main_room_code,
                parent_space=floors[floor_code],
                spaces=[]
            )
            floors[floor_code].spaces.append(main_rooms[main_room_code])
        
        # Handle desk sensors (with rooms)
        if sensor_type == 'deskSensor':
            # Room (optional for desk sensors)
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
            
            # Desk
            desk_uri = f"http://concordia.ca/desk/{desk_id}"
            if desk_id not in desks:
                desk_obj = PhysicalObject(
                    uri=desk_uri,
                    label=desk_id,
                    contained_in=desk_parent
                )
                desk_obj.deskDescription = desk_desc
                desks[desk_id] = desk_obj
                desk_parent.building_object.append(desk_obj)
        
        # Handle other sensors (with zones)
        else:
            # Zone (optional for other sensors)
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
                # Note: Sensors will be added to zones in the future
                # For now, we just create the zone structure
    
    # Prepare output structure
    output = {
        "buildings": [],
        "addresses": []
    }
    for b in buildings.values():
        building_dict = {
            "uri": str(b.uri),
            "label": b.label,
            "address_uri": str(b.address.uri) if b.address else None,
            "spaces": [serialize_building_space(f) for f in b.spaces]
        }
        output["buildings"].append(building_dict)
    for a in addresses.values():
        output["addresses"].append({
            "uri": str(a.uri),
            "street_name": a.street_name,
            "street_number": a.street_number,
            "postal_code": a.postal_code
        })
    
    # Save output
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print(f"Sensor hierarchy transformed data saved to {output_file}")
    print(f"Summary:")
    print(f"- Buildings: {len(buildings)}")
    print(f"- Floors: {len(floors)}")
    print(f"- MainRooms: {len(main_rooms)}")
    print(f"- Rooms: {len(rooms)}")
    print(f"- Zones: {len(zones)}")
    print(f"- Desks: {len(desks)}")

if __name__ == "__main__":
    main() 