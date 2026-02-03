import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. Update/Add 'Get User History' node with Type-Agnostic Query and Fail-Safe
history_node = {
    "parameters": {
        "operation": "find",
        "collection": "messages",
        "query": "={ \"$or\": [ { \"telegram_user_id\": \"{{ $('Parse Telegram Message').item.json.telegram_user_id }}\" }, { \"telegram_user_id\": {{ $('Parse Telegram Message').item.json.telegram_user_id || 0 }} } ] }",
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
    "alwaysOutputData": True, # FAIL-SAFE: Continue even if error
    "credentials": {
        "mongoDb": {
            "id": "YJ4wyhn68TKaChpn",
            "name": "MongoDB account"
        }
    }
}

# Update or Append the node
found = False
for i, node in enumerate(data['nodes']):
    if node.get('name') == "Get User History":
        data['nodes'][i] = history_node
        found = True
if not found:
    data['nodes'].append(history_node)

# 2. Fix the connections (ensure they exist and are correctly ordered)
if 'Check Intent' in data['connections']:
    switch_conns = data['connections']['Check Intent']['main'][0]
    for conn in switch_conns:
        if conn['node'] in ['Extract Date Query', 'Get User History']:
            conn['node'] = 'Get User History'
else:
    # This shouldn't happen but let's be safe
    print("Warning: Check Intent connections not found!")

data['connections']['Get User History'] = {
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

# 3. Update 'Extract Date Query' JS for ultimate resilience
for node in data['nodes']:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = $('Call AI Service').item.json.analysis;
const messageText = (parseData.message_text || '').toLowerCase();

// HISTORY: Get previous messages safely
let history = [];
try { 
    const histItems = $items("Get User History");
    if (histItems && histItems.length > 0) {
        history = histItems.map(i => i.json).filter(j => j && j.message_text);
    }
} catch (e) { history = []; }

const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

let yNum = istDate.getUTCFullYear();
let mNum = istDate.getUTCMonth() + 1;
let dNum = istDate.getUTCDate();

const dateRegex = /\btomorrow\b|\b రేపు\b|\bnext day\b/i;
let isTomorrow = dateRegex.test(messageText);

if (!isTomorrow) {
    // Look back at last 3 messages in history
    for (let i = 0; i < Math.min(history.length, 3); i++) {
        if (dateRegex.test(history[i].message_text)) {
            isTomorrow = true;
            break;
        }
    }
}

let dateLabel = 'Today';
if (isTomorrow) {
    const tom = new Date(msgNowMs + 86400000 + istOffset);
    yNum = tom.getUTCFullYear();
    mNum = tom.getUTCMonth() + 1;
    dNum = tom.getUTCDate();
    dateLabel = 'Tomorrow';
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
const timeRegex = /(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)/i;
let timeMatch = messageText.match(timeRegex) || (aiResponse.entities?.time?.[0]?.value || '').match(timeRegex);

if (!timeMatch) {
    // Check history (last 3 messages)
    for (let i = 0; i < Math.min(history.length, 3); i++) {
        let hMatch = (history[i].message_text || '').match(timeRegex);
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

print("Workflow memory logic hardened (Number/String query + error-bypass).")
