import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        # Update OWNER_ID to include users from the screenshot
        node['parameters']['jsCode'] = node['parameters']['jsCode'].replace(
            "const OWNER_ID = '1287706792';",
            "const OWNERS = ['1287706792', '5309276394', '1371540949'];"
        ).replace(
            "const isOwner = (userId === OWNER_ID || chatId === OWNER_ID);",
            "const isOwner = OWNERS.includes(userId) || OWNERS.includes(chatId);"
        )

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Owners updated.")
