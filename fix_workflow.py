import json

file_path = r'd:\AI Assist\n8n-workflows\telegram\01-telegram-intake.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Helper to find node index by name
def get_node_index(name):
    for i, node in enumerate(data['nodes']):
        if node['name'] == name:
            return i
    return None

# 1. Update Check Intent Node with robust condition
idx = get_node_index("Check Intent")
if idx is not None:
    data['nodes'][idx]['parameters']['conditions'] = {
        "string": [
            {
                "value1": "={{ $json.ai_analysis.intent.toLowerCase() }}",
                "operation": "contains",
                "value2": "view_calendar"
            }
        ]
    }
else:
    print("Error: Check Intent node not found")

# 2. Update Get Upcoming Events Node with IST Timezone Logic
idx = get_node_index("Get Upcoming Events")
if idx is not None:
    data['nodes'][idx]['parameters']['jsCode'] = """
const now = new Date();
const istOffset = 5.5 * 60 * 60 * 1000;
const nowIST = new Date(now.getTime() + istOffset);

// Parse time context from message
let timeFilter = 'today'; // default
const text = $('Set Message Data').item.json.message_text.toLowerCase();

if (text.includes('tomorrow')) {
  timeFilter = 'tomorrow';
} else if (text.includes('this week') || text.includes('week')) {
  timeFilter = 'week';
}

// Calculate time range
let startTime, endTime;

if (timeFilter === 'today') {
  // Use current absolute time for start (exclude past events)
  startTime = now.toISOString(); 
  
  // End of Today in IST (23:59:59 IST)
  const endOfDayIST = new Date(nowIST);
  endOfDayIST.setUTCHours(23, 59, 59, 999);
  // Adjust back to UTC for query
  endTime = new Date(endOfDayIST.getTime() - istOffset).toISOString();
  
} else if (timeFilter === 'tomorrow') {
  // Tomorrow Start (00:00:00 IST)
  const tomorrowStartIST = new Date(nowIST);
  tomorrowStartIST.setUTCDate(tomorrowStartIST.getUTCDate() + 1);
  tomorrowStartIST.setUTCHours(0, 0, 0, 0);
  startTime = new Date(tomorrowStartIST.getTime() - istOffset).toISOString();
  
  // Tomorrow End (23:59:59 IST)
  const tomorrowEndIST = new Date(tomorrowStartIST);
  tomorrowEndIST.setUTCHours(23, 59, 59, 999);
  endTime = new Date(tomorrowEndIST.getTime() - istOffset).toISOString();
  
} else if (timeFilter === 'week') {
  startTime = now.toISOString();
  // 7 days from now
  const nextWeek = new Date(now);
  nextWeek.setDate(nextWeek.getDate() + 7);
  endTime = nextWeek.toISOString();
}

return [{
  query_type: 'calendar',
  time_filter: timeFilter,
  start_time: startTime,
  end_time: endTime,
  message_data: $json
}];
"""

# 3. Update Format Calendar Reply to be cleaner and verify inputs
idx = get_node_index("Format Calendar Reply")
if idx is not None:
     data['nodes'][idx]['parameters']['jsCode'] = """
const fs = require('fs');
const configPath = 'd:/AI Assist/n8n-workflows/telegram_config.json';
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

const events = $input.all().map(item => item.json);
const timeFilter = $('Get Upcoming Events').item.json.time_filter;

let responseText = '';
if (events.length === 0) {
  responseText = `📅 *No upcoming events* ${timeFilter === 'today' ? 'today' : timeFilter === 'tomorrow' ? 'tomorrow' : 'this week'}.`;
} else {
  let response = `📅 *Your Schedule*\\n\\n`;
  if (timeFilter === 'today') {
    response += `*Today's Upcoming Events:*\\n\\n`;
  } else if (timeFilter === 'tomorrow') {
    response += `*Tomorrow's Events:*\\n\\n`;
  } else {
    response += `*This Week's Events:*\\n\\n`;
  }

  events.forEach((event, index) => {
    // Format time in IST
    const eventTime = new Date(event.start_time);
    const eventEndTime = new Date(event.end_time);
    
    // Manual formatting to ensure IST
    const options = { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' };
    const startStr = eventTime.toLocaleTimeString('en-US', options);
    const endStr = eventEndTime.toLocaleTimeString('en-US', options);
    
    response += `${index + 1}. *${event.title}*\\n`;
    response += `   ⏰ ${startStr} - ${endStr}\\n`;
    
    const location = event.location || 'Not specified';
    response += `   📍 ${location}\\n`;
    
    if (event.conflict_detected) {
      response += `   ⚠️ *Conflict detected*\\n`;
    }
    
    response += `\\n`;
  });
  responseText = response;
}

return [{
  response: responseText,
  event_count: events.length,
  bot_token: config.bot_token
}];
"""

# 4. FIX CONNECTIONS - Ensure Update with AI Analysis ONLY goes to Check Intent
if "Update with AI Analysis" in data['connections']:
    # Completely overwrite
    data['connections']["Update with AI Analysis"] = {
        "main": [[{"node": "Check Intent", "type": "main", "index": 0}]]
    }

# 5. FIX CHECK INTENT CONNECTIONS - Ensure FALSE path goes to Check Priority
data['connections']["Check Intent"] = {
    "main": [
        [{"node": "Get Upcoming Events", "type": "main", "index": 0}], # Path 0: True
        [{"node": "Check Priority", "type": "main", "index": 0}]      # Path 1: False
    ]
}

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("Workflow fixed successfully")
