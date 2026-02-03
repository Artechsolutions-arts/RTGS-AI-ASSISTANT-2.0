import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
node_names = {node.get('name') for node in nodes}

connections = data.get('connections', {})
for source_node, targets in connections.items():
    if source_node not in node_names:
        print(f"ERROR: Source node '{source_node}' in connections does not exist in nodes list")
    
    for connection_type, output_groups in targets.items():
        for output_group in output_groups:
            for connection in output_group:
                target_node = connection.get('node')
                if target_node not in node_names:
                    print(f"ERROR: Target node '{target_node}' in connections (from '{source_node}') does not exist in nodes list")

print("Connection verification complete.")
