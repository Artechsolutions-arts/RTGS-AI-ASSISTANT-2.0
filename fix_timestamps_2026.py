import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = node['parameters']['jsCode'].replace(
            "const msgTimestamp = parseData.timestamp;",
            "const msgTs = parseData.timestamp; const msgTimestamp = (msgTs < 10000000000) ? msgTs * 1000 : msgTs;"
        )

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['parameters']['jsCode'] = node['parameters']['jsCode'].replace(
            "const now = (rawTimestamp > 2000000000) ? rawTimestamp : rawTimestamp * 1000;",
            "const now = (rawTimestamp < 10000000000) ? rawTimestamp * 1000 : rawTimestamp;"
        )

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Timestamp detection threshold fixed for 2026 dates.")
