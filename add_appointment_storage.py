import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the "Create Google Meeting" node and add a MongoDB node after it
nodes = data['nodes']
connections = data['connections']

# Add a new node to store appointment in MongoDB
store_appointment_node = {
    "parameters": {
        "operation": "insert",
        "collection": "appointments",
        "fields": "={{ JSON.stringify({\n  appointment_id: 'appt_' + $('Parse Approve').item.json.userChatId + '_' + Date.now(),\n  citizen_telegram_id: $('Parse Approve').item.json.userChatId,\n  citizen_name: $('Parse Telegram Message').item.json.sender_name || 'Citizen',\n  reason: $('Parse Approve').item.json.description || 'Meeting with Collector',\n  start_time: $('Parse Approve').item.json.start,\n  end_time: $('Parse Approve').item.json.end,\n  status: 'approved',\n  approved_by: 'Collector',\n  approved_at: new Date().toISOString(),\n  district: 'ntr-district',\n  created_via: 'telegram_bot',\n  google_calendar_event_id: $json.id\n}) }}",
        "options": {}
    },
    "id": "store-appointment-db",
    "name": "Store Appointment in DB",
    "type": "n8n-nodes-base.mongoDb",
    "typeVersion": 1.1,
    "position": [11400, 1500],
    "credentials": {
        "mongoDb": {
            "id": "YJ4wyhn68TKaChpn",
            "name": "MongoDB account"
        }
    }
}

# Check if node already exists
if not any(n.get('id') == 'store-appointment-db' for n in nodes):
    nodes.append(store_appointment_node)
    
    # Update connections: Create Google Meeting -> Store Appointment -> Notify User
    if "Create Google Meeting" in connections:
        connections["Create Google Meeting"]["main"] = [[{"node": "Store Appointment in DB", "type": "main", "index": 0}]]
    
    connections["Store Appointment in DB"] = {
        "main": [[{"node": "Notify User Approve", "type": "main", "index": 0}]]
    }

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Added appointment storage node to Telegram workflow")
