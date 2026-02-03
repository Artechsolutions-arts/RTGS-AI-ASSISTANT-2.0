import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data.get('nodes', [])
for node in nodes:
    # Update Format Calendar Response to remove the requirement to repeat time/date in the prompt
    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;
const userName = parseData.sender_name || 'User';

let allItems = [];
try { allItems = $items("Get Calendar Events"); } catch (e) { allItems = []; }
const unique = Array.from(new Map(allItems.filter(e => e.json.id).map(e => [e.json.id, e.json])).values());

if (dateQuery.intent === 'request_appointment') {
    let reqStart = dateQuery.reqStart;
    let specificTimeLabel = dateQuery.specificTimeLabel;
    
    // Time extraction from text
    if (!reqStart) {
        const timeMatch = dateQuery.messageText.match(/(?:at|on|@)?\s*(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)/i);
        if (timeMatch) {
             let h = parseInt(timeMatch[1]);
             if (timeMatch[3].toLowerCase() === 'pm' && h < 12) h += 12;
             if (timeMatch[3].toLowerCase() === 'am' && h === 12) h = 0;
             const mins = timeMatch[2] ? timeMatch[2] : '00';
             reqStart = `${dateQuery.targetDate}T${h.toString().padStart(2,'0')}:${mins}:00+05:30`;
             specificTimeLabel = `${timeMatch[1]}:${mins} ${timeMatch[3].toLowerCase()}`;
        }
    }

    if (!reqStart) {
        return [{ json: { chat_id: parseInt(userChatId), message: '🕒 *Time Required:* Please tell me what time you would like to meet (e.g. "at 2:00 PM tomorrow").', bot_token: botToken, parse_mode: 'Markdown' } }];
    }

    const reqS = new Date(reqStart).getTime();
    const reqE = reqS + 3600000;
    
    const isBusy = unique.some(e => {
        const s = new Date(e.start.dateTime || e.start.date).getTime();
        const en = new Date(e.end.dateTime || e.end.date).getTime();
        return (s < reqE && en > reqS);
    });

    if (isBusy) {
        // Suggestion scanning...
        let suggestion = '';
        let sugDateLabel = dateQuery.dateLabel;
        const scanDay = (baseDateStr) => {
            for (let h = 10; h < 17; h++) {
                if (h === 13) continue;
                for (let m of ['00', '30']) {
                    const scanS = new Date(`${baseDateStr}T${h.toString().padStart(2,'0')}:${m}:00+05:30`).getTime();
                    const scanE = scanS + 3600000;
                    if (scanS < dateQuery.msgNowMs + 300000) continue; 
                    const collision = unique.some(e => {
                        const s = new Date(e.start.dateTime || e.start.date).getTime();
                        const en = new Date(e.end.dateTime || e.end.date).getTime();
                        return (s < scanE && en > scanS);
                    });
                    if (!collision) return (h > 12 ? h-12 : h) + ':' + m + (h >= 12 ? ' PM' : ' AM');
                }
            }
            return null;
        };
        suggestion = scanDay(dateQuery.targetDate);
        if (!suggestion) {
            const tom = new Date(dateQuery.msgNowMs + 86400000 + (5.5 * 60 * 60 * 1000));
            const tomStr = tom.getUTCFullYear() + '-' + (tom.getUTCMonth()+1).toString().padStart(2,'0') + '-' + tom.getUTCDate().toString().padStart(2,'0');
            suggestion = scanDay(tomStr);
            if (suggestion) sugDateLabel = 'Tomorrow';
        }
        const sugMsg = suggestion ? `\n\n💡 *Suggested Slot:* Collector is free at *${suggestion}* on *${sugDateLabel}*.` : '';
        return [{ json: { chat_id: parseInt(userChatId), message: `❌ *Slot Unavailable*\n\nThe Collector is busy at *${specificTimeLabel}* on *${dateQuery.dateLabel}*.${sugMsg}`, bot_token: botToken, parse_mode: 'Markdown' } }];
    } else {
        const finalName = dateQuery.applicantName;
        let finalReason = dateQuery.meetingReason;

        // SIMPLIFIED PROMPT: Just ask for Name and Reason
        if (!finalName || !finalReason) {
             return [{ json: { chat_id: parseInt(userChatId), message: `✅ *${specificTimeLabel}* on ${dateQuery.dateLabel} is available!\n\nPlease provide your **Full Name and Reason** to finalize the request (e.g., "Name: Revanth, Reason: Industrial Meeting").`, bot_token: botToken, parse_mode: 'Markdown' } }];
        }

        finalReason = finalReason.replace(/\bat\s*\d{1,2}[:\.]?\d{0,2}\s*(am|pm)?/gi, '')
                                .replace(/\btomorrow\b/gi, '')
                                .replace(/\btoday\b/gi, '')
                                .replace(/\bnext day\b/gi, '')
                                .replace(/\s\s+/g, ' ')
                                .trim();

        const collectorId = '1287706792';
        const msgToCollector = `📅 *New Appointment Request*\n\n👤 *Applicant:* ${finalName}\n🏢 *Reason:* ${finalReason}\n🕒 *Time:* ${dateQuery.targetDate} at ${specificTimeLabel}`;
        const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + reqStart }]] };
        
        return [
            { json: { chat_id: parseInt(userChatId), message: `✅ *Request Sent*\n\nYour appointment for *${specificTimeLabel}* has been sent for approval.`, bot_token: botToken, parse_mode: 'Markdown' } },
            { json: { chat_id: parseInt(collectorId), message: msgToCollector, bot_token: botToken, reply_markup: kb, parse_mode: 'Markdown' } }
        ];
    }
}

if (dateQuery.intent === 'view_calendar' && dateQuery.isOwner) {
    const upcoming = unique.filter(e => new Date(e.end.dateTime || e.end.date).getTime() > (dateQuery.msgNowMs - 60000));
    let msg = `📅 *Schedule for ${dateQuery.dateLabel}*\n\n`;
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

print("Simplified prompt applied (removed requirement to repeat time/date).")
