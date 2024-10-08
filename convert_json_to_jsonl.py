import json

# Read the JSON file
with open('app/models/formatted_training_data.json', 'r') as json_file:
    data = json.load(json_file)

# Write to a JSONL file
with open('app/models/training_data.jsonl', 'w') as jsonl_file:
    for entry in data:
        jsonl_file.write(json.dumps(entry) + '\n')