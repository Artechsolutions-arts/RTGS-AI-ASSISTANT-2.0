import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Update 'Save to MongoDB' to include telegram_user_id for history tracking
for node in data['nodes']:
    if node.get('name') == "Save to MongoDB":
        node['parameters']['fields'] = "message_id, message_text, district, timestamp, sender_name, sender_role, telegram_user_id"
    
    if node.get('name') == "Set Message Data":
        # Ensure telegram_user_id is available in the items passed to MongoDB
        for assignment in node['parameters']['assignments']['assignments']:
            if assignment['name'] == 'telegram_user_id':
                break
        else:
            node['parameters']['assignments']['assignments'].append({
                "id": "tg_uid",
                "name": "telegram_user_id",
                "value": "={{ $json.telegram_user_id }}",
                "type": "string"
            })

# 2. Add 'Get History' node
history_node = {
    "parameters": {
        "operation": "find",
        "collection": "messages",
        "query": "={ \"telegram_user_id\": \"{{ $('Parse Telegram Message').item.json.telegram_user_id }}\" }",
        "options": {
            "sort": "{ \"timestamp\": -1 }",
            "limit": 10
        }
    },
    "id": "get-history-id",
    "name": "Get User History",
    "type": "n8n-nodes-base.mongoDb",
    "typeVersion": 1.1,
    "position": [
        11136,
        2288
    ],
    "credentials": {
        "mongoDb": {
            "id": "YJ4wyhn68TKaChpn",
            "name": "MongoDB account"
        }
    }
}

if not any(n.get('name') == "Get User History" for n in data['nodes']):
    data['nodes'].append(history_node)

# 3. Connect 'Check Intent' -> 'Get User History' -> 'Extract Date Query'
# Current: Check Intent (output 0) -> Extract Date Query
# New: Check Intent (output 0) -> Get User History -> Extract Date Query

connections = data['connections']
# Update output 0 of Check Intent
switch_conns = connections['Check Intent']['main'][0]
for conn in switch_conns:
    if conn['node'] == 'Extract Date Query':
        conn['node'] = 'Get User History'

# Add output of Get User History
connections['Get User History'] = {
    "main": [
        [
            {
                "node": "Extract Date Query",
                "type": "main",
                "index": 0
            }
        ]
    ]
}

# 4. Update 'Extract Date Query' JS to use history for missing time/date
for node in data['nodes']:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = $('Call AI Service').item.json.analysis;
const messageText = (parseData.message_text || '').toLowerCase();

// HISTORY: Get previous messages to "remember" time/date
let history = [];
try { history = $items("Get User History").map(i => i.json); } catch (e) { history = []; }

const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

let yNum = istDate.getUTCFullYear();
let mNum = istDate.getUTCMonth() + 1;
let dNum = istDate.getUTCDate();

// Look for Date in current OR history
let dateFound = false;
let dateLabel = 'Today';

const dateRegex = /\btomorrow\b|\b రేపు\b|\bnext day\b/i;
if (dateRegex.test(messageText)) {
    dateFound = true;
    dateLabel = 'Tomorrow';
} else {
    // Check history (last 3 messages)
    for (const h of history.slice(1, 4)) {
        if (dateRegex.test(h.message_text)) {
            dateFound = true;
            dateLabel = 'Tomorrow';
            break;
        }
    }
}

if (dateLabel === 'Tomorrow') {
    const tom = new Date(msgNowMs + 86400000 + istOffset);
    yNum = tom.getUTCFullYear();
    mNum = tom.getUTCMonth() + 1;
    dNum = tom.getUTCDate();
}

const pad = (n) => n.toString().padStart(2, '0');
const yStr = yNum.toString();
const mStr = pad(mNum);
const dStr = pad(dNum);

const timeMin = `${yStr}-${mStr}-${dStr}T00:00:00+05:30`;
const timeMax = `${yStr}-${mStr}-${dStr}T23:59:59+05:30`;

let intent = aiResponse.intent;
if (/\bmeetings\b|\bschedule\b/i.test(messageText)) intent = 'view_calendar';

const applicantNameMatch = messageText.match(/name:\s*([^,.\n]+)/i);
const reasonMatch = messageText.match(/reason:\s*([^,.\n]+)/i);
const applicantName = applicantNameMatch ? applicantNameMatch[1].trim() : (aiResponse.entities?.person?.[0]?.value || '');
const meetingReason = reasonMatch ? reasonMatch[1].trim() : (aiResponse.entities?.reason?.[0]?.value || '');

if ((applicantName || meetingReason) && intent !== 'view_calendar') {
    intent = 'request_appointment';
}

const OWNERS = ['1287706792', '5309276394', '1371540949'];
const isOwner = OWNERS.includes(String(parseData.telegram_user_id));

let reqStart, reqEnd, specificTimeLabel = '';
const ents = aiResponse.entities || {};

// Look for Time in current OR history
const timeRegex = /(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)/i;
let timeMatch = null;

if (ents.time && ents.time.length > 0) {
    timeMatch = ents.time[0].value.match(timeRegex);
} else {
    timeMatch = messageText.match(timeRegex);
}

if (!timeMatch) {
    // Check history (last 3 messages)
    for (const h of history.slice(1, 4)) {
        const hMatch = (h.message_text || '').match(timeRegex);
        if (hMatch) {
            timeMatch = hMatch;
            break;
        }
    }
}

if (timeMatch) {
    let h = parseInt(timeMatch[1]);
    const mins = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
    const ampm = (timeMatch[3] || '').toLowerCase();
    if (ampm === 'pm' && h < 12) h += 12;
    if (ampm === 'am' && h === 12) h = 0;
    reqStart = `${yStr}-${mStr}-${dStr}T${pad(h)}:${pad(mins)}:00+05:30`;
    reqEnd = `${yStr}-${mStr}-${dStr}T${pad(h+1)}:${pad(mins)}:00+05:30`;
    specificTimeLabel = `${timeMatch[1]}:${pad(mins)} ${ampm}`;
    if (intent !== 'view_calendar') intent = 'request_appointment';
}

return [{
    json: {
        timeMin, timeMax, authorized: true, isOwner, intent, msgNowMs,
        debugTime: pad(istDate.getUTCHours()) + ":" + pad(istDate.getUTCMinutes()),
        targetDate: `${yStr}-${mStr}-${dStr}`,
        reqStart, reqEnd, specificTimeLabel, 
        applicantName, meetingReason, dateLabel, messageText
    }
}];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Workflow enhanced with memory node (MongoDB history).")
