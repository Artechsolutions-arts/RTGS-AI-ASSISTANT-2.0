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
const msgNowMs = (msgTs < 10000000000) ? msgTs * 1000 : msgTs;

// Use a fixed 5.5 hour offset for IST
const istDate = new Date(msgNowMs + (5.5 * 60 * 60 * 1000));

const y = istDate.getUTCFullYear();
const m = istDate.getUTCMonth() + 1;
const d = istDate.getUTCDate();

const pad = (n) => n.toString().padStart(2, '0');
const timeMin = `${y}-${pad(m)}-${pad(d)}T00:00:00+05:30`;
const timeMax = `${y}-${pad(m)}-${pad(d)}T23:59:59+05:30`;

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
        debugTime: pad(istDate.getUTCHours()) + ":" + pad(istDate.getUTCMinutes())
    }
}];'''

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['executeOnce'] = True
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;

if (!dateQuery.authorized) {
    return [{ json: { chat_id: parseInt(userChatId), message: '⛔ *Access Denied*\n\nYou are not authorized to view this calendar.', bot_token: botToken } }];
}

// Robust item fetching
let allItems = [];
try {
    allItems = $items("Get Calendar Events");
} catch (e) {
    allItems = [];
}

const unique = [];
const seen = new Set();
allItems.forEach(item => {
    if (item.json && item.json.id && !seen.has(item.json.id)) {
        unique.push(item.json);
        seen.add(item.json.id);
    }
});

const nowMs = dateQuery.msgNowMs;

if (dateQuery.intent === 'view_calendar') {
    // Show meetings that are upcoming or happened recently
    const upcoming = unique.filter(e => {
        if (!e.end) return false;
        const endTs = new Date(e.end.dateTime || e.end.date).getTime();
        return endTs > (nowMs - 300000); 
    });

    let msg = '📅 *Schedule for Today*\n\n';
    if (upcoming.length === 0) {
        msg += (unique.length > 0) 
            ? 'All scheduled meetings for today have concluded! ✅'
            : 'No meetings scheduled! ✅';
    } else {
        upcoming.forEach((e, i) => {
            const sTime = e.start.dateTime || e.start.date;
            const eTime = e.end.dateTime || e.end.date;
            const startStr = new Date(sTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const endStr = new Date(eTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + startStr + ' - ' + endStr + '\n\n';
        });
        msg += '_Total: ' + upcoming.length + ' upcoming meeting(s)_';
    }

    msg += '\n\n`[Debug: ' + unique.length + ' fetched, IST: ' + dateQuery.debugTime + ']`';

    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken, parse_mode: 'Markdown' } }];
}

// Fallback if intent wasn't caught
return [{ json: { chat_id: parseInt(userChatId), message: 'Sorry, I couldn\'t process that request. Try asking "today schedule".', bot_token: botToken } }];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Workflow code hardened with error handling.")
