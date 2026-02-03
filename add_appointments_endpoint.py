import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\shared\08-dashboard-api.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Add appointments webhook and nodes
appointments_webhook = {
    "parameters": {
        "httpMethod": "GET",
        "path": "appointments-approved",
        "responseMode": "responseNode",
        "options": {}
    },
    "id": "webhook-appointments",
    "name": "Webhook - Appointments",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 1.1,
    "position": [250, 700],
    "webhookId": "appointments-approved"
}

appointments_query = {
    "parameters": {
        "operation": "find",
        "collection": "appointments",
        "options": {
            "queryParameters": "={ \"district\": \"{{ $json.query.district || 'ntr-district' }}\", \"status\": \"approved\" }",
            "sort": "{ \"start_time\": -1 }",
            "limit": 100
        }
    },
    "id": "mongodb-get-appointments",
    "name": "MongoDB - Get Appointments",
    "type": "n8n-nodes-base.mongoDb",
    "typeVersion": 1.1,
    "position": [450, 700],
    "credentials": {
        "mongoDb": {
            "id": "YJ4wyhn68TKaChpn",
            "name": "MongoDB account"
        }
    }
}

format_appointments = {
    "parameters": {
        "jsCode": "return $input.all().map(item => ({\n  id: item.json._id,\n  citizen_name: item.json.citizen_name,\n  reason: item.json.reason,\n  start: item.json.start_time,\n  end: item.json.end_time,\n  status: item.json.status,\n  approved_at: item.json.approved_at,\n  telegram_id: item.json.citizen_telegram_id\n}));"
    },
    "id": "format-appointments",
    "name": "Format Appointments",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [650, 700]
}

respond_appointments = {
    "parameters": {
        "respondWith": "json",
        "responseBody": "={{ $input.all().map(i => i.json) }}",
        "options": {}
    },
    "id": "respond-appointments",
    "name": "Respond Appointments",
    "type": "n8n-nodes-base.respondToWebhook",
    "typeVersion": 1.1,
    "position": [850, 700]
}

# Add nodes if they don't exist
new_nodes = [appointments_webhook, appointments_query, format_appointments, respond_appointments]
existing_ids = {n.get('id') for n in data['nodes']}

for node in new_nodes:
    if node['id'] not in existing_ids:
        data['nodes'].append(node)

# Add connections
data['connections']['Webhook - Appointments'] = {"main": [[{"node": "MongoDB - Get Appointments", "type": "main", "index": 0}]]}
data['connections']['MongoDB - Get Appointments'] = {"main": [[{"node": "Format Appointments", "type": "main", "index": 0}]]}
data['connections']['Format Appointments'] = {"main": [[{"node": "Respond Appointments", "type": "main", "index": 0}]]}

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Added appointments endpoint to Dashboard API workflow")
