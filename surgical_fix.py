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
const OWNER_ID = '1287706792'; 
const isOwner = (userId === OWNER_ID || chatId === OWNER_ID);

// Force schedule intent if user says "meetings" or "schedule"
if (messageText.includes('meetings') || messageText.includes('schedule')) {
    intent = 'view_calendar';
}

const isBookingKeyword = messageText.includes('appointment') || (/\bmeet\b/.test(messageText) && !messageText.includes('meetings')) || messageText.includes('book') || messageText.includes('slot');
const authorized = (intent === 'request_appointment' || isBookingKeyword) ? true : isOwner;

// Base Date
const getIST = (ts) => new Date(new Date(ts).toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
let istBase = getIST(msgTimestamp);
let dateLabel = 'Today';

if (messageText.includes('tomorrow') || messageText.includes('రేపు')) {
  istBase.setDate(istBase.getDate() + 1);
  dateLabel = 'Tomorrow';
}

const buildISO = (h, m, s) => {
  const pad = (n) => n.toString().padStart(2, '0');
  return istBase.getFullYear() + '-' + pad(istBase.getMonth() + 1) + '-' + pad(istBase.getDate()) + 'T' + pad(h) + ':' + pad(m) + ':' + pad(s) + '+05:30';
};

const timeMin = buildISO(0, 0, 0);
const timeMax = buildISO(23, 59, 59);

let reqStart, reqEnd;
let specificTimeLabel = '';

if ((intent === 'request_appointment' || isBookingKeyword) && intent !== 'view_calendar') {
    if (entities.time && entities.time.length > 0) {
       const timeVal = entities.time[0].value.toLowerCase();
       let hours = 9; 
       let minutes = 0;
       
       const match = timeVal.match(/(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)?/);
       if (match) {
           hours = parseInt(match[1]);
           minutes = match[2] ? parseInt(match[2]) : 0;
           const meridiem = match[3];
           if (meridiem === 'pm' && hours < 12) hours += 12;
           if (meridiem === 'am' && hours === 12) hours = 0;
       }
       
       reqStart = buildISO(hours, minutes, 0);
       reqEnd = buildISO(hours + 1, minutes, 0);
       specificTimeLabel = timeVal;
    } else {
        return [{ json: { authorized: true, missing_time: true, dateLabel, intent: 'request_appointment' } }];
    }
}

return [{
  json: {
    timeMin, timeMax, reqStart, reqEnd,
    dateLabel, targetDate: buildISO(0,0,0).split('T')[0],
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

// --- AUTHORIZATION CHECK ---
if (dateQuery.authorized === false) {
    return [{ json: { chat_id: parseInt(userChatId), message: '⛔ *Access Denied*\n\nYou are not authorized to view the Executive Calendar.', bot_token: botToken } }];
}

// --- APPOINTMENT LOGIC ---
if (dateQuery.intent === 'request_appointment') {
    if (dateQuery.missing_time) {
         return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*\n\nPlease specify the time for the appointment.\nExample: "Appointment tomorrow at 10 am"', bot_token: botToken } }];
    }

    const allEvents = $input.all();
    const reqStart = new Date(dateQuery.reqStart);
    const reqEnd = new Date(dateQuery.reqEnd);

    const collisions = allEvents.filter(e => {
        if (!e.json.start || !e.json.start.dateTime) return false;
        const evStart = new Date(e.json.start.dateTime);
        const evEnd = new Date(e.json.end.dateTime);
        return (evStart < reqEnd && evEnd > reqStart);
    });

    if (collisions.length > 0) {
        let suggestedTime = null;
        const scanDate = new Date(reqStart);
        scanDate.setUTCHours(4, 30, 0, 0); // 10:00 IST

        while (scanDate.getUTCHours() < 11 || (scanDate.getUTCHours() === 11 && scanDate.getUTCMinutes() < 30)) {
             const slotStart = new Date(scanDate);
             const slotEnd = new Date(scanDate);
             slotEnd.setUTCHours(slotEnd.getUTCHours() + 1);

             const slotBusy = allEvents.some(e => {
                if (!e.json.start || !e.json.start.dateTime) return false;
                const evStart = new Date(e.json.start.dateTime);
                const evEnd = new Date(e.json.end.dateTime);
                return (evStart < slotEnd && evEnd > slotStart);
             });

             if (!slotBusy && Math.abs(slotStart.getTime() - reqStart.getTime()) > 60000) {
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
                message: '❌ *Slot Unavailable*\n\nThe Collector has a meeting at ' + dateQuery.specificTimeLabel + '.\n\n' + suggestionMsg,
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
    const allEvents = $input.all();
    const uniqueEvents = Array.from(new Map(allEvents.filter(e => e.json.id).map(e => [e.json.id, e])).values());

    if (uniqueEvents.length === 0) {
        return [{ json: { chat_id: parseInt(userChatId), message: '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\nNo meetings scheduled! ✅', bot_token: botToken } }];
    }

    let msg = '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\n';
    uniqueEvents.forEach((ev, idx) => {
        const d = ev.json;
        let timeStr = 'All Day';
        if (d.start.dateTime) {
            const start = new Date(d.start.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const end = new Date(d.end.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            timeStr = start + ' - ' + end;
        }
        msg += (idx + 1) + '. *' + (d.summary || 'Untitled') + '*\n   🕐 ' + timeStr + '\n\n';
    });

    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
}

return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Workflow surgical fix applied.")
