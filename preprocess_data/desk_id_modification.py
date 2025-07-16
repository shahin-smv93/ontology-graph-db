import json
import os

# File paths
orig_path = '../sensors_file/concordia_sensors_finalized.json'
backup_path = '../sensors_file/concordia_sensors_finalized__.json'

# Rename the original file to backup
os.rename(orig_path, backup_path)

# Load the data
with open(backup_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Modify deskID
for entry in data:
    if 'deskID' in entry and entry['deskID']:
        entry['deskID'] = f"{entry['sensorUID']}_desk{entry['deskID']}"

# Write the modified data to the original file
with open(orig_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print('Updated deskID to sensorUID_desk<deskID> and wrote to concordia_sensors_finalized.json') 