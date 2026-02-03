import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = r'''const messageData = $('Set Message Data').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userId = String(parseData.telegram_user_id || parseData.sender_id);
const chatId = String(parseData.telegram_chat_id || parseData.chat_id);
const aiResponse = $('Call AI Service').item.json.analysis;
let intent = aiResponse.intent;
const entities = aiResponse.entities || {};

const messageText = (messageData.message_text || '').toLowerCase();
const msgTimestamp = parseData.timestamp;

// --- AUTHORIZATION ---
const OWNERS = ['1287706792', '5309276394', '1371540949'];
const isOwner = OWNERS.includes(userId) || OWNERS.includes(chatId);

// Force schedule intent if user says "meetings" or "schedule"
if (messageText.includes('meetings') || messageText.includes('schedule')) {
    intent = 'view_calendar';
}

const isBookingKeyword = messageText.includes('appointment') || (/\bmeet\b/.test(messageText) && !messageText.includes('meetings')) || messageText.includes('book') || messageText.includes('slot');
const authorized = (intent === 'request_appointment' || isBookingKeyword) ? true : isOwner;

// --- TIMEZONE ROBUST DATE PARTS ---
const queryDate = new Date(msgTimestamp);
const parts = new Intl.DateTimeFormat('en-US', {
  timeZone: 'Asia/Kolkata',
  year: 'numeric', month: 'numeric', day: 'numeric',
  hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: false
}).formatToParts(queryDate);

const p = {};
parts.forEach(part => { p[part.type] = part.value; });

let year = parseInt(p.year);
let month = parseInt(p.month);
let day = parseInt(p.day);

let dateLabel = 'Today';
if (messageText.includes('tomorrow') || messageText.includes('రేపు')) {
  const tomorrow = new Date(queryDate.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
  tomorrow.setDate(tomorrow.getDate() + 1);
  year = tomorrow.getFullYear();
  month = tomorrow.getMonth() + 1;
  day = tomorrow.getDate();
  dateLabel = 'Tomorrow';
}

const buildISO = (h, min, s) => {
  const pad = (n) => n.toString().padStart(2, '0');
  return `${year}-${pad(month)}-${pad(day)}T${pad(h)}:${pad(min)}:${pad(s)}+05:30`;
};

const timeMin = buildISO(0, 0, 0);
const timeMax = buildISO(23, 59, 59);

let reqStart, reqEnd;
let specificTimeLabel = '';

if ((intent === 'request_appointment' || isBookingKeyword) && intent !== 'view_calendar') {
    let hours = 9; 
    let minutes = 0;
    let foundTime = false;

    if (entities.time && entities.time.length > 0) {
       const timeVal = entities.time[0].value.toLowerCase();
       const match = timeVal.match(/(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)?/);
       if (match) {
           hours = parseInt(match[1]);
           minutes = match[2] ? parseInt(match[2]) : 0;
           const meridiem = match[3];
           if (meridiem === 'pm' && hours < 12) hours += 12;
           if (meridiem === 'am' && hours === 12) hours = 0;
           specificTimeLabel = timeVal;
           foundTime = true;
       }
    }

    if (!foundTime) {
        return [{ json: { authorized: true, missing_time: true, dateLabel, intent: 'request_appointment' } }];
    }
    
    reqStart = buildISO(hours, minutes, 0);
    reqEnd = buildISO(hours + 1, minutes, 0);
}

return [{
  json: {
    timeMin, timeMax, reqStart, reqEnd,
    dateLabel, targetDate: `${year}-${month.toString().padStart(2,'0')}-${day.toString().padStart(2,'0')}`,
    authorized, intent, specificTimeLabel, isOwner
  }
}];'''

    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['executeOnce'] = True
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;
const userName = parseData.sender_name || 'User';
const isOwner = dateQuery.isOwner;

// CRITICAL: Use $items() to get ALL events from the calendar node, 
// because executeOnce:true only sees the FIRST item in the current stream.
const allEvents = $items("Get Calendar Events");

const uniqueEvents = [];
const seenIds = new Set();
for (const item of allEvents) {
    if (item.json && item.json.id && !seenIds.has(item.json.id)) {
        uniqueEvents.push(item);
        seenIds.add(item.json.id);
    }
}

// --- AUTHORIZATION CHECK ---
if (dateQuery.authorized === false) {
    return [{ json: { chat_id: parseInt(userChatId), message: '⛔ *Access Denied*\n\nYou are not authorized to view the Executive Calendar.', bot_token: botToken } }];
}

// --- APPOINTMENT LOGIC ---
if (dateQuery.intent === 'request_appointment') {
    if (dateQuery.missing_time) {
         return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*\n\nPlease specify the time.\nExample: "Tomorrow at 10 am"', bot_token: botToken } }];
    }

    const reqStart = new Date(dateQuery.reqStart).getTime();
    const reqEnd = new Date(dateQuery.reqEnd).getTime();

    // Collision check using all unique events
    const collisions = uniqueEvents.filter(e => {
        if (!e.json.start || !e.json.start.dateTime) return false;
        const evStart = new Date(e.json.start.dateTime).getTime();
        const evEnd = new Date(e.json.end.dateTime).getTime();
        return (evStart < reqEnd && evEnd > reqStart);
    });

    if (collisions.length > 0) {
        let suggestedTime = null;
        const scanDate = new Date(dateQuery.reqStart);
        scanDate.setUTCHours(4, 30, 0, 0); // 10:00 IST

        while (scanDate.getUTCHours() < 11 || (scanDate.getUTCHours() === 11 && scanDate.getUTCMinutes() < 30)) {
             const slotStart = new Date(scanDate);
             const slotEnd = new Date(scanDate);
             slotEnd.setUTCHours(slotEnd.getUTCHours() + 1);

             const slotBusy = uniqueEvents.some(e => {
                if (!e.json.start || !e.json.start.dateTime) return false;
                const evStart = new Date(e.json.start.dateTime).getTime();
                const evEnd = new Date(e.json.end.dateTime).getTime();
                return (evStart < slotEnd.getTime() && evEnd > slotStart.getTime());
             });

             if (!slotBusy && Math.abs(slotStart.getTime() - reqStart) > 60000) {
                 let hour = (slotStart.getUTCHours() + 5);
                 if (slotStart.getUTCMinutes() >= 30) hour++;
                 const ampm = hour >= 12 ? 'PM' : 'AM';
                 hour = hour % 12 || 12;
                 suggestedTime = hour + ' ' + ampm;
                 break;
             }
             scanDate.setUTCHours(scanDate.getUTCHours() + 1);
        }

        const suggestionMsg = suggestedTime ? 'Suggested Time: *' + suggestedTime + '*' : 'No other slots today.';

        return [{
            json: {
                chat_id: parseInt(userChatId),
                message: '❌ *Slot Unavailable*\n\nThe Collector is busy at ' + dateQuery.specificTimeLabel + '.\n\n' + suggestionMsg,
                bot_token: botToken
            }
        }];
    } else {
        const collectorId = '1287706792';
        const cmdTime = dateQuery.reqStart;
        const collectorMsg = '📅 *New Appointment Request*\n\n👤 *From:* ' + userName + ' (' + userChatId + ')\n🕒 *Time:* ' + dateQuery.targetDate + ' at ' + dateQuery.specificTimeLabel;

        const replyMarkup = {
            inline_keyboard: [[
                { text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + cmdTime },
                { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + cmdTime }
            ]]
        };

        const userMsg = '✅ *Request Sent*\n\nYour appointment request for ' + dateQuery.specificTimeLabel + ' has been sent to the Collector for approval.';

        return [
            { json: { chat_id: parseInt(userChatId), message: userMsg, bot_token: botToken } },
            { json: { chat_id: parseInt(collectorId), message: collectorMsg, bot_token: botToken, reply_markup: replyMarkup } }
        ];
    }
}

// --- CALENDAR VIEW LOGIC ---
if (dateQuery.intent === 'view_calendar' && isOwner) {
    if (uniqueEvents.length === 0) {
        return [{ json: { chat_id: parseInt(userChatId), message: '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\nNo meetings scheduled! ✅', bot_token: botToken } }];
    }

    let msg = '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\n';
    uniqueEvents.forEach((ev, idx) => {
        const d = ev.json;
        let timeStr = 'All Day';
        if (d.start.dateTime) {
            const startStr = new Date(d.start.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const endStr = new Date(d.end.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            timeStr = startStr + ' - ' + endStr;
        }
        msg += (idx + 1) + '. *' + (d.summary || 'Untitled') + '*\n   🕐 ' + timeStr + '\n\n';
    });
    
    msg += '_Total: ' + uniqueEvents.length + ' meeting' + (uniqueEvents.length > 1 ? 's' : '') + '_';

    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
}

return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Calendar fix V2 applied: using $items() for full list.")
