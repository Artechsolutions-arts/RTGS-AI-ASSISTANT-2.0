import json

with open('intake_clean.json', encoding='utf-8') as f:
    data = json.load(f)[0]

nodes = {n['name'] for n in data['nodes']}
print(f"Total nodes: {len(nodes)}")

missing = set()
for node_name, node_conns in data['connections'].items():
    if node_name not in nodes:
        print(f"Source node not found: {node_name}")
    
    for conn_type, conn_outputs in node_conns.items():
        for output_index, targets in enumerate(conn_outputs):
            for target in targets:
                target_name = target.get('node')
                if target_name not in nodes:
                    print(f"Target node not found: {target_name} (from {node_name})")
                    missing.add(target_name)

if not missing:
    print("All connections valid.")
else:
    print(f"Found {len(missing)} missing targets.")
