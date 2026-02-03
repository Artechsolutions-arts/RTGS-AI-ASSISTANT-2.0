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

// Robust 2026 Timestamp Handling
const nowMs = (msgTs < 10000000000) ? msgTs * 1000 : msgTs;

// Get IST Date Components Safely
const formatter = new Intl.DateTimeFormat('en-US', {
  timeZone: 'Asia/Kolkata', year: 'numeric', month: '2-digit', day: '2-digit'
});
const parts = formatter.formatToParts(new Date(nowMs));
const p = {}; parts.forEach(pt => { p[pt.type] = pt.value; });

let y = parseInt(p.year);
let m = parseInt(p.month);
let d = parseInt(p.day);

let dateLabel = 'Today';
if (messageText.includes('tomorrow') || messageText.includes('రేపు')) {
    const tomorrow = new Date(new Date(nowMs).toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    tomorrow.setDate(tomorrow.getDate() + 1);
    y = tomorrow.getFullYear();
    m = tomorrow.getMonth() + 1;
    d = tomorrow.getDate();
    dateLabel = 'Tomorrow';
}

const pad = (n) => n.toString().padStart(2, '0');
const timeMin = `${y}-${pad(m)}-${pad(d)}T00:00:00+05:30`;
const timeMax = `${y}-${pad(m)}-${pad(d)}T23:59:59+05:30`;

let intent = aiResponse.intent;
if (messageText.includes('meetings') || messageText.includes('schedule')) {
    intent = 'view_calendar';
}

const OWNERS = ['1287706792', '5309276394', '1371540949'];
const isOwner = OWNERS.includes(String(parseData.telegram_user_id || parseData.sender_id));
const isBookingKeyword = messageText.includes('appointment') || (/\bmeet\b/.test(messageText) && !messageText.includes('meetings'));
const authorized = (intent === 'request_appointment' || isBookingKeyword) ? true : isOwner;

let reqStart, reqEnd, specificTimeLabel = '';
if ((intent === 'request_appointment' || isBookingKeyword) && intent !== 'view_calendar') {
    const ents = aiResponse.entities || {};
    if (ents.time && ents.time.length > 0) {
        const tVal = ents.time[0].value.toLowerCase();
        const match = tVal.match(/(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)?/);
        if (match) {
            let h = parseInt(match[1]);
            const minutes = match[2] ? parseInt(match[2]) : 0;
            const ampm = match[3];
            if (ampm === 'pm' && h < 12) h += 12;
            if (ampm === 'am' && h === 12) h = 0;
            reqStart = `${y}-${pad(m)}-${pad(d)}T${pad(h)}:${pad(minutes)}:00+05:30`;
            reqEnd = `${y}-${pad(m)}-${pad(d)}T${pad(h+1)}:${pad(minutes)}:00+05:30`;
            specificTimeLabel = tVal;
        }
    }
}

return [{
    json: {
        timeMin, timeMax, reqStart, reqEnd, dateLabel, 
        targetDate: `${y}-${pad(m)}-${pad(d)}`, 
        authorized, intent, specificTimeLabel, isOwner, nowMs
    }
}];'''

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['executeOnce'] = True
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;
const userName = parseData.sender_name || 'User';

if (!dateQuery.authorized) {
    return [{ json: { chat_id: parseInt(userChatId), message: '⛔ *Access Denied*', bot_token: botToken } }];
}

// Ensure we get ALL events
const allItems = $items("Get Calendar Events");
const uniqueEvents = Array.from(new Map(allItems.filter(e => e.json.id).map(e => [e.json.id, e.json])).values());

const nowMs = dateQuery.nowMs;

if (dateQuery.intent === 'request_appointment') {
    if (!dateQuery.reqStart) {
        return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*', bot_token: botToken } }];
    }
    const reqS = new Date(dateQuery.reqStart).getTime();
    const reqE = new Date(dateQuery.reqEnd).getTime();
    const collisions = uniqueEvents.filter(e => {
        const s = new Date(e.start.dateTime).getTime();
        const en = new Date(e.end.dateTime).getTime();
        return (s < reqE && en > reqS);
    });
    if (collisions.length > 0) {
        return [{ json: { chat_id: parseInt(userChatId), message: '❌ *Slot Unavailable*\n\nThe Collector is busy at ' + dateQuery.specificTimeLabel + '.', bot_token: botToken } }];
    } else {
        const collectorId = '1287706792';
        const msg = '📅 *New Appointment Request*\n\n👤 *From:* ' + userName + '\n🕒 *Time:* ' + dateQuery.targetDate + ' at ' + dateQuery.specificTimeLabel;
        const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + dateQuery.reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + dateQuery.reqStart }]] };
        return [{ json: { chat_id: parseInt(userChatId), message: '✅ *Request Sent*', bot_token: botToken } }, { json: { chat_id: parseInt(collectorId), message: msg, bot_token: botToken, reply_markup: kb } }];
    }
}

if (dateQuery.intent === 'view_calendar') {
    let filtered = uniqueEvents;
    if (dateQuery.dateLabel === 'Today') {
        filtered = uniqueEvents.filter(e => {
            const end = new Date(e.end.dateTime || e.end.date).getTime();
            return end > (nowMs - 60000); 
        });
    }

    if (filtered.length === 0) {
        let msg = '📅 *Schedule for Today*\n\nAll scheduled meetings for today have concluded! ✅';
        if (uniqueEvents.length === 0) msg = '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\nNo meetings scheduled! ✅';
        return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
    }

    let msg = '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\n';
    filtered.forEach((e, i) => {
        const start = new Date(e.start.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
        const end = new Date(e.end.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
        msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + start + ' - ' + end + '\n\n';
    });
    msg += '_Total: ' + filtered.length + ' upcoming meeting(s)_';
    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
}
return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
