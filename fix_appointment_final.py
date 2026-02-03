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

// Get the message timestamp
const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();

// IST Offset
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

let y = istDate.getUTCFullYear();
let m = istDate.getUTCMonth() + 1;
let d = istDate.getUTCDate();

let dateLabel = 'Today';
if (messageText.includes('tomorrow') || messageText.includes('రేపు')) {
    const tom = new Date(msgNowMs + 86400000 + istOffset);
    y = tom.getUTCFullYear();
    m = tom.getUTCMonth() + 1;
    d = tom.getUTCDate();
    dateLabel = 'Tomorrow';
}

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
const isOwner = OWNERS.includes(userId) || OWNERS.includes(chatId);

let reqStart, reqEnd, specificTimeLabel = '';
const ents = aiResponse.entities || {};
if (ents.time && ents.time.length > 0) {
    const tVal = ents.time[0].value.toLowerCase();
    const match = tVal.match(/(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)?/);
    if (match) {
        let h = parseInt(match[1]);
        const mins = match[2] ? parseInt(match[2]) : 0;
        const ampm = match[3];
        if (ampm === 'pm' && h < 12) h += 12;
        if (ampm === 'am' && h === 12) h = 0;
        reqStart = `${yStr}-${mStr}-${dStr}T${pad(h)}:${pad(mins)}:00+05:30`;
        reqEnd = `${yStr}-${mStr}-${dStr}T${pad(h+1)}:${pad(mins)}:00+05:30`;
        specificTimeLabel = tVal;
        // If they mentioned a time, force appointment intent unless it's a schedule request
        if (intent !== 'view_calendar') intent = 'request_appointment';
    }
}

return [{
    json: {
        timeMin, timeMax, authorized: true, isOwner, intent, msgNowMs,
        debugTime: pad(istDate.getUTCHours()) + ":" + pad(istDate.getUTCMinutes()),
        targetDate: `${yStr}-${mStr}-${dStr}`,
        reqStart, reqEnd, specificTimeLabel
    }
}];'''

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;
const userName = parseData.sender_name || 'User';

// Get ALL events
let allItems = [];
try { allItems = $items("Get Calendar Events"); } catch (e) { allItems = []; }
const unique = Array.from(new Map(allItems.filter(e => e.json.id).map(e => [e.json.id, e.json])).values());

if (dateQuery.intent === 'request_appointment') {
    if (!dateQuery.reqStart) {
        return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*\n\nPlease specify the time (e.g., "Tomorrow at 2pm").', bot_token: botToken, parse_mode: 'Markdown' } }];
    }

    const reqS = new Date(dateQuery.reqStart).getTime();
    const reqE = new Date(dateQuery.reqEnd).getTime();
    
    const collisions = unique.filter(e => {
        const s = new Date(e.start.dateTime || e.start.date).getTime();
        const en = new Date(e.end.dateTime || e.end.date).getTime();
        return (s < reqE && en > reqS);
    });

    if (collisions.length > 0) {
        return [{ json: { chat_id: parseInt(userChatId), message: '❌ *Slot Unavailable*\n\nThe Collector is busy at ' + dateQuery.specificTimeLabel + '.', bot_token: botToken, parse_mode: 'Markdown' } }];
    } else {
        const collectorId = '1287706792';
        const msg = '📅 *New Appointment Request*\n\n👤 *From:* ' + userName + '\n🕒 *Time:* ' + dateQuery.targetDate + ' at ' + dateQuery.specificTimeLabel;
        const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + dateQuery.reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + dateQuery.reqStart }]] };
        
        return [
            { json: { chat_id: parseInt(userChatId), message: '✅ *Request Sent*\n\nYour appointment request for ' + dateQuery.specificTimeLabel + ' has been sent to the Collector for approval.', bot_token: botToken, parse_mode: 'Markdown' } },
            { json: { chat_id: parseInt(collectorId), message: msg, bot_token: botToken, reply_markup: kb, parse_mode: 'Markdown' } }
        ];
    }
}

if (dateQuery.intent === 'view_calendar' && dateQuery.isOwner) {
    const upcoming = unique.filter(e => new Date(e.end.dateTime || e.end.date).getTime() > (dateQuery.msgNowMs - 60000));
    let msg = '📅 *Schedule for Today*\n\n';
    if (upcoming.length === 0) {
        msg += (unique.length > 0) ? 'All scheduled meetings have concluded! ✅' : 'No meetings scheduled! ✅';
    } else {
        upcoming.forEach((e, i) => {
            const s = new Date(e.start.dateTime || e.start.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const en = new Date(e.end.dateTime || e.end.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + s + ' - ' + en + '\n\n';
        });
    }
    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken, parse_mode: 'Markdown' } }];
}

return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Appointment check logic finalized.")
