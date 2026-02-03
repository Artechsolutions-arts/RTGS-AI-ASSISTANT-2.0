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

// Extraction of Name and Reason
const ents = aiResponse.entities || {};
const applicantName = ents.person?.[0]?.value || '';
const meetingReason = ents.reason?.[0]?.value || '';

// Force appointment intent if reason/name is provided and it's not a view_calendar request
if ((applicantName || meetingReason) && intent !== 'view_calendar') {
    intent = 'request_appointment';
}

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
        applicantName, meetingReason, dateLabel, messageText
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
    // If no time is in CURRENT message, we check the text for a time mention directly 
    // or we might need to ask for it again. But let's try to extract from text first.
    let reqStart = dateQuery.reqStart;
    let specificTimeLabel = dateQuery.specificTimeLabel;
    
    if (!reqStart) {
        // Fallback: Check if the text itself has "at 1:00 pm" or similar
        const timeMatch = dateQuery.messageText.match(/at\s*(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)/);
        if (timeMatch) {
             let h = parseInt(timeMatch[1]);
             if (timeMatch[3] === 'pm' && h < 12) h += 12;
             const mins = timeMatch[2] ? parseInt(timeMatch[2]) : '00';
             reqStart = `${dateQuery.targetDate}T${h.toString().padStart(2,'0')}:${mins}:00+05:30`;
             specificTimeLabel = `${timeMatch[1]}:${mins} ${timeMatch[3]}`;
        }
    }

    if (!reqStart) {
        return [{ json: { chat_id: parseInt(userChatId), message: '❓ *Time Required*\n\nPlease specify the time (e.g., "at 2:00 PM") along with your name and reason.', bot_token: botToken, parse_mode: 'Markdown' } }];
    }

    const reqS = new Date(reqStart).getTime();
    const reqE = reqS + 3600000;
    
    const isBusy = unique.some(e => {
        const s = new Date(e.start.dateTime || e.start.date).getTime();
        const en = new Date(e.end.dateTime || e.end.date).getTime();
        return (s < reqE && en > reqS);
    });

    if (isBusy) {
        // IMPROVED SUGGESTION LOOP (Scan 10 AM to 5 PM)
        let suggestion = '';
        const day = dateQuery.targetDate;
        for (let h = 10; h < 17; h++) {
            if (h === 13) continue; // Lunch
            for (let m of ['00', '30']) {
                const scanS = new Date(`${day}T${h.toString().padStart(2,'0')}:${m}:00+05:30`).getTime();
                const scanE = scanS + 1800000; // 30 min slots
                if (scanS < dateQuery.msgNowMs + 300000) continue; 
                
                const collision = unique.some(e => {
                    const s = new Date(e.start.dateTime || e.start.date).getTime();
                    const en = new Date(e.end.dateTime || e.end.date).getTime();
                    return (s < scanE && en > scanS);
                });
                if (!collision) {
                    const sugH = (h > 12) ? h - 12 : h;
                    suggestion = `${sugH}:${m} ${(h >= 12) ? 'PM' : 'AM'}`;
                    break;
                }
            }
            if (suggestion) break;
        }
        
        const sugMsg = suggestion ? `\n\n💡 *Suggested Slot:* Collector is free at *${suggestion}* ${dateQuery.dateLabel}.` : '';
        return [{ json: { chat_id: parseInt(userChatId), message: `❌ *Slot Unavailable*\n\nThe Collector is busy at *${specificTimeLabel}* on ${dateQuery.dateLabel}.${sugMsg}`, bot_token: botToken, parse_mode: 'Markdown' } }];
    } else {
        const finalName = dateQuery.applicantName || userName;
        const finalReason = dateQuery.meetingReason;

        if (!finalReason) {
             return [{ json: { chat_id: parseInt(userChatId), message: `✅ *${specificTimeLabel}* is available!\n\nPlease provide the **Reason** for the meeting and your **Full Name** (e.g., "Reason: Discussion, Name: Revanth") to complete the booking.`, bot_token: botToken, parse_mode: 'Markdown' } }];
        }

        const collectorId = '1287706792';
        const msgToCollector = `📅 *New Appointment Request*\n\n👤 *Applicant:* ${finalName}\n🏢 *Reason:* ${finalReason}\n🕒 *Time:* ${dateQuery.targetDate} at ${specificTimeLabel}`;
        const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + reqStart }]] };
        
        return [
            { json: { chat_id: parseInt(userChatId), message: `✅ *Request Sent*\n\nYour appointment for *${specificTimeLabel}* has been sent for approval.\n\n*Details:* ${finalReason}`, bot_token: botToken, parse_mode: 'Markdown' } },
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

print("Logic fixed: Added time extraction to code node and improved suggestion scan.")
