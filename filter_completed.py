import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;
const userName = parseData.sender_name || 'User';
const isOwner = dateQuery.isOwner;

// Fetch all events from the calendar node
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

        const userMsg = '✅ *Request Sent*\n\nYour appointment request for ' + dateQuery.specificTimeLabel + ' has been sent test';

        return [
            { json: { chat_id: parseInt(userChatId), message: userMsg, bot_token: botToken } },
            { json: { chat_id: parseInt(collectorId), message: collectorMsg, bot_token: botToken, reply_markup: replyMarkup } }
        ];
    }
}

// --- CALENDAR VIEW LOGIC ---
if (dateQuery.intent === 'view_calendar' && isOwner) {
    const rawTimestamp = parseData.timestamp;
    const now = (rawTimestamp > 2000000000) ? rawTimestamp : rawTimestamp * 1000;
    
    let filteredEvents = uniqueEvents;
    if (dateQuery.dateLabel.toLowerCase() === 'today') {
        filteredEvents = uniqueEvents.filter(ev => {
            if (!ev.json.end || !ev.json.end.dateTime) return true;
            const eventEnd = new Date(ev.json.end.dateTime).getTime();
            // Buffer of 1 minute to avoid filtering out meetings that just ended
            return eventEnd > (now - 60000);
        });
    }

    if (filteredEvents.length === 0) {
        const msg = (uniqueEvents.length > 0) 
            ? '📅 *Schedule for Today*\n\nAll scheduled meetings for today have concluded! ✅'
            : '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\nNo meetings scheduled! ✅';
        return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
    }

    let msg = '📅 *Schedule for ' + dateQuery.dateLabel + '*\n\n';
    filteredEvents.forEach((ev, idx) => {
        const d = ev.json;
        let timeStr = 'All Day';
        if (d.start.dateTime) {
            const startStr = new Date(d.start.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const endStr = new Date(d.end.dateTime).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            timeStr = startStr + ' - ' + endStr;
        }
        msg += (idx + 1) + '. *' + (d.summary || 'Untitled') + '*\n   🕐 ' + timeStr + '\n\n';
    });
    
    msg += '_Total: ' + filteredEvents.length + ' upcoming meeting' + (filteredEvents.length > 1 ? 's' : '') + '_';

    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken } }];
}

return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Calendar logic updated: filtering completed meetings.")
