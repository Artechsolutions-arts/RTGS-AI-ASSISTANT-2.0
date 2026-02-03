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

const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

let yNum = istDate.getUTCFullYear();
let mNum = istDate.getUTCMonth() + 1;
let dNum = istDate.getUTCDate();

let dateLabel = 'Today';
if (messageText.includes('tomorrow') || messageText.includes('రేపు')) {
    const tom = new Date(msgNowMs + 86400000 + istOffset);
    yNum = tom.getUTCFullYear();
    mNum = tom.getUTCMonth() + 1;
    dNum = tom.getUTCDate();
    dateLabel = 'Tomorrow';
}

const pad = (n) => n.toString().padStart(2, '0');
const yStr = yNum.toString();
const mStr = pad(mNum);
const dStr = pad(dNum);

const timeMin = `${yStr}-${mStr}-${dStr}T00:00:00+05:30`;
const timeMax = `${yStr}-${mStr}-${dStr}T23:59:59+05:30`;

let intent = aiResponse.intent;
if (messageText.includes('meetings') || messageText.includes('schedule')) intent = 'view_calendar';

// Extraction of Name and Reason from Entities
const ents = aiResponse.entities || {};
const applicantName = ents.person?.[0]?.value || '';
const meetingReason = ents.reason?.[0]?.value || '';

const OWNERS = ['1287706792', '5309276394', '1371540949'];
const userId = String(parseData.telegram_user_id || parseData.sender_id);
const chatId = String(parseData.telegram_chat_id || parseData.chat_id);
const isOwner = OWNERS.includes(userId) || OWNERS.includes(chatId);

let reqStart, reqEnd, specificTimeLabel = '';
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
        if (intent !== 'view_calendar') intent = 'request_appointment';
    }
}

return [{
    json: {
        timeMin, timeMax, authorized: true, isOwner, intent, msgNowMs,
        debugTime: pad(istDate.getUTCHours()) + ":" + pad(istDate.getUTCMinutes()),
        targetDate: `${yStr}-${mStr}-${dStr}`,
        reqStart, reqEnd, specificTimeLabel, 
        applicantName, meetingReason, dateLabel
    }
}];'''

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
    if (!dateQuery.reqStart) {
        return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*\n\nPlease specify the time (e.g., "Tomorrow at 2pm").', bot_token: botToken, parse_mode: 'Markdown' } }];
    }

    const reqS = new Date(dateQuery.reqStart).getTime();
    const reqE = new Date(dateQuery.reqEnd).getTime();
    
    const isBusy = unique.some(e => {
        const s = new Date(e.start.dateTime || e.start.date).getTime();
        const en = new Date(e.end.dateTime || e.end.date).getTime();
        return (s < reqE && en > reqS);
    });

    if (isBusy) {
        // SUGGEST TIME LOGIC
        let suggestion = '';
        const day = dateQuery.targetDate;
        const workHours = [10, 11, 12, 14, 15, 16]; // 10 AM - 5 PM (Avoiding 1 PM lunch)
        for (const h of workHours) {
            const scanS = new Date(`${day}T${h.toString().padStart(2,'0')}:00:00+05:30`).getTime();
            const scanE = scanS + 3600000;
            if (scanS < dateQuery.msgNowMs) continue; // Skip past times
            
            const collision = unique.some(e => {
                const s = new Date(e.start.dateTime || e.start.date).getTime();
                const en = new Date(e.end.dateTime || e.end.date).getTime();
                return (s < scanE && en > scanS);
            });
            if (!collision) {
                suggestion = (h > 12) ? `${h-12}:00 PM` : `${h}:00 AM`;
                break;
            }
        }
        
        const sugMsg = suggestion ? `\n\n*Suggestion:* Collector is free at *${suggestion}* ${dateQuery.dateLabel}.` : '';
        return [{ json: { chat_id: parseInt(userChatId), message: `❌ *Slot Unavailable*\n\nThe Collector is busy at *${dateQuery.specificTimeLabel}* on ${dateQuery.dateLabel}.${sugMsg}\n\nTo book another time, please specify it clearly.`, bot_token: botToken, parse_mode: 'Markdown' } }];
    } else {
        // SLOT IS FREE - CHECK FOR DATA
        const finalName = dateQuery.applicantName || userName;
        const finalReason = dateQuery.meetingReason;

        if (!finalReason) {
             return [{ json: { chat_id: parseInt(userChatId), message: `✅ *${dateQuery.specificTimeLabel}* is available!\n\nPlease provide the **Reason** for the meeting and your **Full Name** to complete the request.`, bot_token: botToken, parse_mode: 'Markdown' } }];
        }

        const collectorId = '1287706792';
        const msgToCollector = `📅 *New Appointment Request*\n\n👤 *Applicant:* ${finalName}\n🏢 *Reason:* ${finalReason}\n🕒 *Time:* ${dateQuery.targetDate} at ${dateQuery.specificTimeLabel}`;
        const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + dateQuery.reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + dateQuery.reqStart }]] };
        
        return [
            { json: { chat_id: parseInt(userChatId), message: `✅ *Request Sent*\n\nYour request for *${dateQuery.specificTimeLabel}* (Reason: ${finalReason}) has been sent for approval.`, bot_token: botToken, parse_mode: 'Markdown' } },
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

print("Enhanced appointment logic with suggestion and reasoning applied.")
