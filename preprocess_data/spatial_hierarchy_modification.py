import json
import os

# File paths
json_path = 'sensors_file/concordia_sensors_finalized.json'

# Load the data
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Modify the data
for entry in data:
    building = entry.get('building', '')
    floor = entry.get('floor', '')
    mainRoom = entry.get('mainRoom', '')
    room = entry.get('room')
    zone = entry.get('zone')
    deskID = entry.get('deskID')
    
    # Modify floor: <building>-<floor>
    if building and floor:
        entry['floor'] = f"{building}-{floor}"
    
    # Modify mainRoom: <building>-<floor>-<mainRoom>
    if building and floor and mainRoom:
        entry['mainRoom'] = f"{building}-{floor}-{mainRoom}"
    
    # Modify room: <building>-<floor>-<mainRoom>-<room> (if not null)
    if room and building and floor and mainRoom:
        entry['room'] = f"{building}-{floor}-{mainRoom}-{room}"
    
    # Modify zone: <building>-<floor>-<mainRoom>-<zone> (if not null)
    if zone and building and floor and mainRoom:
        entry['zone'] = f"{building}-{floor}-{mainRoom}-{zone}"
    
    # Modify deskID based on room presence
    if deskID:
        if room:
            # If room is not null: <mainRoom>-<room>-<deskID>
            entry['deskID'] = f"{mainRoom}-{room}-{deskID}"
        else:
            # If room is null: <mainRoom>-<deskID>
            entry['deskID'] = f"{mainRoom}-{deskID}"

# Write the modified data back to the file
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print('Successfully modified spatial hierarchy in concordia_sensors_finalized.json')
print('Changes made:')
print('- floor: <building>-<floor>')
print('- mainRoom: <building>-<floor>-<mainRoom>')
print('- room: <building>-<floor>-<mainRoom>-<room> (if not null)')
print('- zone: <building>-<floor>-<mainRoom>-<zone> (if not null)')
print('- deskID: <mainRoom>-<room>-<deskID> (if room not null) or <mainRoom>-<deskID> (if room null)') 