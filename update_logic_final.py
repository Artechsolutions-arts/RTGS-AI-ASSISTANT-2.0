import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0":
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
         return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*\n\nPlease specify the time for the appointment.', bot_token: botToken } }];
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
        // 10:00 IST = 04:30 UTC
        scanDate.setUTCHours(4, 30, 0, 0);

        // Scan until 5:00 PM IST (11:30 UTC)
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

             const isRequestedSlot = (Math.abs(slotStart.getTime() - reqStart.getTime()) < 60000);

             if (!slotBusy && !isRequestedSlot) {
                 let hour = (slotStart.getUTCHours() + 5);
                 if (slotStart.getUTCMinutes() >= 30) hour++;
                 const ampm = hour >= 12 ? 'PM' : 'AM';
                 hour = hour % 12 || 12;
                 suggestedTime = hour + ' ' + ampm;
                 break;
             }
             scanDate.setUTCHours(scanDate.getUTCHours() + 1);
        }

        const suggestionMsg = suggestedTime ? 'Suggested Time: *' + suggestedTime + '*' : 'No slots available today.';

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
            inline_keyboard: [
                [
                    { text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + cmdTime },
                    { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + cmdTime }
                ]
            ]
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

    let msg = '📅 *Schedule for ' + dateLabel + '*\n\n';
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

print("Workflow updated successfully.")
