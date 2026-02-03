import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data['nodes']:
    # REMOVE executeOnce: true which is blocking multiple tests
    if 'executeOnce' in node:
        print(f"Removing executeOnce from node: {node.get('name')}")
        del node['executeOnce']

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Blocking 'executeOnce' parameter removed.")
