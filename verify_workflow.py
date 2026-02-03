import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for i, node in enumerate(nodes):
    node_name = node.get('name', f'Node {i}')
    node_type = node.get('type')
    node_id = node.get('id')
    
    if not node_type:
        print(f"ERROR: Node '{node_name}' (index {i}) is missing 'type'")
    if not node_id:
        print(f"ERROR: Node '{node_name}' (index {i}) is missing 'id'")
    if 'typeVersion' not in node:
        print(f"ERROR: Node '{node_name}' (index {i}) is missing 'typeVersion'")

print("Verification complete.")
