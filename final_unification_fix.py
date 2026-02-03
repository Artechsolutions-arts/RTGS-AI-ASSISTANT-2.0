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

// Safe timestamp handling for 2026
const nowMs = (msgTs < 10000000000) ? msgTs * 1000 : msgTs;
// We need current day start/end for the search
const dateISTStr = new Date(nowMs).toLocaleString('en-US', { timeZone: 'Asia/Kolkata' });
const dateIST = new Date(dateISTStr);

let targetDate = new Date(dateIST);
let dateLabel = 'Today';

if (messageText.includes('tomorrow') || messageText.includes('రేపు')) {
    targetDate.setDate(targetDate.getDate() + 1);
    dateLabel = 'Tomorrow';
}

const pad = (n) => n.toString().padStart(2, '0');
const y = targetDate.getFullYear();
const m = pad(targetDate.getMonth() + 1);
const d = pad(targetDate.getDate());

const timeMin = `${y}-${m}-${d}T00:00:00+05:30`;
const timeMax = `${y}-${m}-${d}T23:59:59+05:30`;

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
            reqStart = `${y}-${m}-${d}T${pad(h)}:${pad(minutes)}:00+05:30`;
            const endH = (minutes === 0) ? h + 1 : h;
            const endM = (minutes === 0) ? 0 : (minutes + 1) % 60;
            reqEnd = `${y}-${m}-${d}T${pad(endH)}:${pad(endM)}:00+05:30`;
            specificTimeLabel = tVal;
        }
    }
}

return [{
    json: {
        timeMin, timeMax, reqStart, reqEnd, dateLabel, 
        targetDate: `${y}-${m}-${d}`, 
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

// CRITICAL FIX: Use $items() to see ALL events, not just the first one.
const allItems = $items("Get Calendar Events");
const uniqueEvents = [];
const seenIds = new Set();
for (const item of allItems) {
    if (item.json && item.json.id && !seenIds.has(item.json.id)) {
        uniqueEvents.push(item.json);
        seenIds.add(item.json.id);
    }
}

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
           const end = new Date(e.end.dateTime).getTime();
           return end > (nowMs - 60000); 
        });
    }
    
    if (filtered.length === 0) {
        let msg = '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\nNo upcoming meetings! ✅';
        if (uniqueEvents.length > 0 && dateQuery.dateLabel === 'Today') msg = '📅 *Schedule for Today*\n\nAll scheduled meetings for today have concluded! ✅';
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
