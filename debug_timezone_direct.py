import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = $('Call AI Service').item.json.analysis;
const msgTs = parseData.timestamp;
const messageText = (parseData.message_text || '').toLowerCase();

// Threshold: 10 Billion separates seconds from milliseconds
const nowMs = (msgTs < 10000000000) ? msgTs * 1000 : msgTs;

// FORCE IST components directly from the Epoch
// IST is UTC + 5:30
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(nowMs + istOffset);

const y = istDate.getUTCFullYear();
const m = istDate.getUTCMonth() + 1;
const d = istDate.getUTCDate();

const pad = (n) => n.toString().padStart(2, '0');
const yStr = y.toString();
const mStr = pad(m);
const dStr = pad(d);

const timeMin = `${yStr}-${mStr}-${dStr}T00:00:00+05:30`;
const timeMax = `${yStr}-${mStr}-${dStr}T23:59:59+05:30`;

let intent = aiResponse.intent;
if (messageText.includes('meetings') || messageText.includes('schedule')) {
    intent = 'view_calendar';
}

const OWNERS = ['1287706792', '5309276394', '1371540949'];
const isOwner = OWNERS.includes(String(parseData.telegram_user_id || parseData.sender_id));

return [{
    json: {
        timeMin, timeMax, dateLabel: 'Today', 
        targetDate: `${yStr}-${mStr}-${dStr}`, 
        authorized: isOwner, intent, nowMs,
        debugTime: istDate.getUTCHours() + ":" + pad(istDate.getUTCMinutes())
    }
}];'''

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['executeOnce'] = True
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;

if (!dateQuery.authorized) {
    return [{ json: { chat_id: parseInt(userChatId), message: '⛔ *Access Denied*', bot_token: botToken } }];
}

// Get ALL events regardless of stream position
const allItems = $items("Get Calendar Events");
const unique = Array.from(new Map(allItems.filter(e => e.json.id).map(e => [e.json.id, e.json])).values());

const nowTs = dateQuery.nowMs;

if (dateQuery.intent === 'view_calendar') {
    // Filter out meetings that ended more than 5 minutes ago
    const upcoming = unique.filter(e => {
        const endFull = e.end.dateTime || e.end.date;
        const endTs = new Date(endFull).getTime();
        return endTs > (nowTs - 300000); 
    });

    let msg = '';
    if (upcoming.length === 0) {
        msg = (unique.length > 0) 
            ? '📅 *Schedule for Today*\n\nAll scheduled meetings for today have concluded! ✅'
            : '📅 *Schedule for Today*\n\nNo meetings scheduled! ✅';
    } else {
        msg = '📅 *Schedule for Today*\n\n';
        upcoming.forEach((e, i) => {
            const startStr = new Date(e.start.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const endStr = new Date(e.end.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + startStr + ' - ' + endStr + '\n\n';
        });
        msg += '_Total: ' + upcoming.length + ' upcoming meeting(s)_';
    }

    // DEBUG FOOTER - To see exactly why it's failing
    msg += '\n\n`[System Debug: ' + unique.length + ' found, Clock: ' + dateQuery.debugTime + ']`';

    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
}
return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
