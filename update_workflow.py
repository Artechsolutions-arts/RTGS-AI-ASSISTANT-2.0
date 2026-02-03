import json

file_path = r'd:\AI Assist\n8n-workflows\telegram\01-telegram-intake.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Helper to find node by name
def get_node_id(name):
    for node in data['nodes']:
        if node['name'] == name:
            return node['id']
    return None

# Check if nodes already exist to prevent duplicates
if get_node_id("Check Intent"):
    print("Nodes already exist, skipping update.")
    exit(0)

# New Nodes
new_nodes = [
    {
        "parameters": {
            "conditions": {
                "string": [
                    {
                        "value1": "={{ $json.ai_analysis.intent }}",
                        "operation": "equals",
                        "value2": "view_calendar"
                    }
                ]
            }
        },
        "id": "check-intent",
        "name": "Check Intent",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1650, 100]
    },
    {
        "parameters": {
            "jsCode": "const now = new Date();\n\n// Parse time context from message\nlet timeFilter = 'today'; // default\nconst text = $('Set Message Data').item.json.message_text.toLowerCase();\n\nif (text.includes('tomorrow')) {\n  timeFilter = 'tomorrow';\n} else if (text.includes('this week') || text.includes('week')) {\n  timeFilter = 'week';\n}\n\n// Calculate time range\nlet startTime, endTime;\n\nif (timeFilter === 'today') {\n  startTime = now.toISOString(); // Current time\n  endTime = new Date(now);\n  endTime.setHours(23, 59, 59, 999);\n  endTime = endTime.toISOString();\n} else if (timeFilter === 'tomorrow') {\n  startTime = new Date(now);\n  startTime.setDate(startTime.getDate() + 1);\n  startTime.setHours(0, 0, 0, 0);\n  startTime = startTime.toISOString();\n  \n  endTime = new Date(startTime);\n  endTime.setHours(23, 59, 59, 999);\n  endTime = endTime.toISOString();\n} else if (timeFilter === 'week') {\n  startTime = now.toISOString();\n  endTime = new Date(now);\n  endTime.setDate(endTime.getDate() + 7);\n  endTime = endTime.toISOString();\n}\n\nreturn [{\n  query_type: 'calendar',\n  time_filter: timeFilter,\n  start_time: startTime,\n  end_time: endTime,\n  message_data: $json\n}];"
        },
        "id": "get-upcoming-events",
        "name": "Get Upcoming Events",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1850, 100]
    },
    {
        "parameters": {
            "operation": "find",
            "collection": "calendar_events",
            "options": {
                "sort": { "start_time": 1 }
            },
             "queryParameters": "{ \"start_time\": { \"$gte\": \"={{ $json.start_time }}\", \"$lte\": \"={{ $json.end_time }}\" }, \"status\": { \"$in\": [\"scheduled\", \"confirmed\"] } }"
        },
        "id": "query-calendar-events",
        "name": "Query Calendar Events",
        "type": "n8n-nodes-base.mongoDb",
        "typeVersion": 1.1,
        "position": [2050, 100],
        "credentials": {
            "mongoDb": {
                "id": "1",
                "name": "MongoDB - Gov AI Assistant"
            }
        }
    },
    {
        "parameters": {
            "jsCode": "const fs = require('fs');\nconst configPath = 'd:/AI Assist/n8n-workflows/telegram_config.json';\nconst config = JSON.parse(fs.readFileSync(configPath, 'utf8'));\n\nconst events = $input.all().map(item => item.json);\nconst timeFilter = $('Get Upcoming Events').item.json.time_filter;\n\nlet responseText = '';\nif (events.length === 0) {\n  responseText = `📅 *No upcoming events* ${timeFilter === 'today' ? 'today' : timeFilter === 'tomorrow' ? 'tomorrow' : 'this week'}.`;\n} else {\n  let response = `📅 *Your Schedule*\\n\\n`;\n  if (timeFilter === 'today') {\n    response += `*Today's Upcoming Events:*\\n\\n`;\n  } else if (timeFilter === 'tomorrow') {\n    response += `*Tomorrow's Events:*\\n\\n`;\n  } else {\n    response += `*This Week's Events:*\\n\\n`;\n  }\n\n  events.forEach((event, index) => {\n    const startTime = new Date(event.start_time);\n    const endTime = new Date(event.end_time);\n    \n    response += `${index + 1}. *${event.title}*\\n`;\n    response += `   ⏰ ${startTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;\n    response += ` - ${endTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`;\n    const location = event.location || 'Not specified';\n    response += `\\n   📍 ${location}\\n`;\n    \n    if (event.conflict_detected) {\n      response += `   ⚠️ *Conflict detected*\\n`;\n    }\n    \n    response += `\\n`;\n  });\n  responseText = response;\n}\n\nreturn [{\n  response: responseText,\n  event_count: events.length,\n  bot_token: config.bot_token\n}];"
        },
        "id": "format-calendar-reply",
        "name": "Format Calendar Reply",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [2250, 100]
    },
    {
        "parameters": {
            "url": "=https://api.telegram.org/bot{{ $json.bot_token }}/sendMessage",
            "method": "POST",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ { chat_id: $('Set Message Data').item.json.telegram_data.chat_id, text: $json.response, parse_mode: 'Markdown' } }}",
            "options": {}
        },
        "id": "send-calendar-reply",
        "name": "Send Calendar Reply",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [2450, 100]
    }
]

# Add new nodes
data['nodes'].extend(new_nodes)

# Update connections
# Remove Update with AI Analysis -> Check Priority
if "Update with AI Analysis" in data['connections']:
    del data['connections']["Update with AI Analysis"]

# Add Update with AI Analysis -> Check Intent
data['connections']["Update with AI Analysis"] = {
    "main": [[{"node": "Check Intent", "type": "main", "index": 0}]]
}

# Add Check Intent connections
data['connections']["Check Intent"] = {
    "main": [
        [{"node": "Get Upcoming Events", "type": "main", "index": 0}], # True (Calendar)
        [{"node": "Check Priority", "type": "main", "index": 0}]      # False (Other)
    ]
}

# Add Calendar flow connections
data['connections']["Get Upcoming Events"] = {
    "main": [[{"node": "Query Calendar Events", "type": "main", "index": 0}]]
}
data['connections']["Query Calendar Events"] = {
    "main": [[{"node": "Format Calendar Reply", "type": "main", "index": 0}]]
}
data['connections']["Format Calendar Reply"] = {
    "main": [[{"node": "Send Calendar Reply", "type": "main", "index": 0}]]
}
data['connections']["Send Calendar Reply"] = {
    "main": [[{"node": "Respond Success", "type": "main", "index": 0}]]
}

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("Workflow updated successfully")
