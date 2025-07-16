import json

input_path = 'neo4j_etl/concordia_sensors_finalized.json'
output_path = 'neo4j_etl/concordia_sensors_finalized.json'  # Overwrite in place

with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for entry in data:
    if 'timeInterval' in entry and entry['timeInterval'] is not None:
        entry['timeInterval'] = str(entry['timeInterval'])

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print('Converted all non-null timeInterval values to strings.') 