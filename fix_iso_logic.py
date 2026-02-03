import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = $('Call AI Service').item.json.analysis;
const messageText = (parseData.message_text || '').toLowerCase();

// Get the message timestamp (always an ISO string from our Parse node)
const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();

// Handle IST Offset (UTC + 5.5 hours) for display and search windows
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

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
const userId = String(parseData.telegram_user_id || parseData.sender_id);
const chatId = String(parseData.telegram_chat_id || parseData.chat_id);
const authorized = OWNERS.includes(userId) || OWNERS.includes(chatId);

return [{
    json: {
        timeMin, timeMax, authorized, intent, msgNowMs,
        debugTime: pad(istDate.getUTCHours()) + ":" + pad(istDate.getUTCMinutes()),
        targetDate: `${yStr}-${mStr}-${dStr}`
    }
}];'''

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;

const msgNowMs = dateQuery.msgNowMs;

if (!dateQuery.authorized) {
    return [{ json: { chat_id: parseInt(userChatId), message: '⛔ *Access Denied*\n\nYou are not authorized to view the Executive Calendar.', bot_token: botToken, parse_mode: 'Markdown' } }];
}

// Fetch all events
let allItems = [];
try { allItems = $items("Get Calendar Events"); } catch (e) { allItems = []; }

const unique = [];
const seen = new Set();
allItems.forEach(item => {
    if (item.json && item.json.id && !seen.has(item.json.id)) {
        unique.push(item.json);
        seen.add(item.json.id);
    }
});

if (dateQuery.intent === 'view_calendar') {
    // Show meetings ending in the future
    const upcoming = unique.filter(e => {
        const endTime = e.end.dateTime || e.end.date;
        return new Date(endTime).getTime() > (msgNowMs - 60000);
    });

    let msg = '📅 *Schedule for Today*\n\n';
    if (upcoming.length === 0) {
        msg += (unique.length > 0) 
            ? 'All scheduled meetings for today have concluded! ✅'
            : 'No meetings scheduled! ✅';
    } else {
        upcoming.forEach((e, i) => {
            const s = e.start.dateTime || e.start.date;
            const en = e.end.dateTime || e.end.date;
            const sStr = new Date(s).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const eStr = new Date(en).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + sStr + ' - ' + eStr + '\n\n';
        });
        msg += '_Total: ' + upcoming.length + ' upcoming meeting(s)_';
    }

    msg += '\n\n`[System Debug: ' + unique.length + ' fetched, Clock: ' + dateQuery.debugTime + ']`';

    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken, parse_mode: 'Markdown' } }];
}

// Default response if no intent matched (should not happen for calendar users)
return [{ json: { chat_id: parseInt(userChatId), message: 'I processed your request but found no relevant calendar data.', bot_token: botToken } }];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Workflow timestamp logic fixed (ISO string handling).")
