import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data['nodes']:
    # 1. Update Extract Date Query for Citizen-First Intent Handling
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd": # Extract Date Query
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = $('Call AI Service').item.json.analysis || {};
const messageText = (parseData.message_text || '').toLowerCase();

// HISTORY: Get previous context
let history = [];
try { 
    history = $items("Get User History").map(i => i.json).filter(j => j && j.message_text);
} catch (e) { history = []; }

const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

const dateRegex = /\btomorrow\b|\b రేపు\b|\bnext day\b/i;
let isTomorrow = dateRegex.test(messageText);

if (!isTomorrow) {
    for (let i = 0; i < Math.min(history.length, 3); i++) {
        if (dateRegex.test(history[i].message_text)) {
            isTomorrow = true;
            break;
        }
    }
}

let yNum = istDate.getUTCFullYear();
let mNum = istDate.getUTCMonth() + 1;
let dNum = istDate.getUTCDate();
let dateLabel = 'Today';

if (isTomorrow) {
    const tom = new Date(msgNowMs + 86400000 + istOffset);
    yNum = tom.getUTCFullYear();
    mNum = tom.getUTCMonth() + 1;
    dNum = tom.getUTCDate();
    dateLabel = 'Tomorrow';
}

const pad = (n) => n.toString().padStart(2, '0');
const targetDateList = `${yNum}-${pad(mNum)}-${pad(dNum)}`;

const timeMin = `${targetDateList}T00:00:00+05:30`;
const timeMax = `${targetDateList}T23:59:59+05:30`;

// --- INTENT REFINEMENT ---
let intent = aiResponse.intent || 'UNKNOWN';

// If citizen says "book" or "appointment", it's ALWAYS a request
if (/\bbook\b|\bappointment\b|\bmeet\b|\bcollector\b/i.test(messageText)) {
    intent = 'request_appointment';
}

// sticky history
if (intent === 'UNKNOWN' || intent === 'general') {
    for (let i = 0; i < Math.min(history.length, 3); i++) {
        if (/\bappointment\b|\bbook\b/i.test(history[i].message_text)) {
            intent = 'request_appointment';
            break;
        }
    }
}

const applicantNameMatch = messageText.match(/name:\s*([^,.\n]+)/i);
const reasonMatch = messageText.match(/reason:\s*([^,.\n]+)/i);
const applicantName = applicantNameMatch ? applicantNameMatch[1].trim() : (aiResponse.entities?.person?.[0]?.value || '');
const meetingReason = reasonMatch ? reasonMatch[1].trim() : (aiResponse.entities?.reason?.[0]?.value || '');

const OWNERS = ['1287706792', '5309276394', '1371540949'];
const isOwner = OWNERS.includes(String(parseData.telegram_user_id));

let reqStart, reqEnd, specificTimeLabel = '';
const timeRegex = /(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)/i;
let timeMatch = messageText.match(timeRegex);

if (!timeMatch) {
    for (let i = 0; i < Math.min(history.length, 3); i++) {
        let hMatch = (history[i].message_text || '').match(timeRegex);
        if (hMatch) {
            timeMatch = hMatch;
            break;
        }
    }
}

if (timeMatch) {
    let h = parseInt(timeMatch[1]);
    const mins = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
    const ampm = (timeMatch[3] || '').toLowerCase();
    if (ampm === 'pm' && h < 12) h += 12;
    if (ampm === 'am' && h === 12) h = 0;
    reqStart = `${targetDateList}T${pad(h)}:${pad(mins)}:00+05:30`;
    reqEnd = `${targetDateList}T${pad(h+1)}:${pad(mins)}:00+05:30`;
    specificTimeLabel = `${timeMatch[1]}:${pad(mins)} ${ampm}`;
}

return [{
    json: {
        timeMin, timeMax, authorized: true, isOwner, intent, msgNowMs,
        targetDate: targetDateList, reqStart, reqEnd, specificTimeLabel, 
        applicantName, meetingReason, dateLabel, messageText
    }
}];'''

    # 2. Update Format Calendar Response to handle non-owner schedule requests and hangs
    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0": # Format Calendar Response
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';
const dateQuery = $('Extract Date Query').item.json;
const parseData = $('Parse Telegram Message').item.json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id;

if (dateQuery.intent === 'request_appointment') {
    let reqStart = dateQuery.reqStart;
    let specificTimeLabel = dateQuery.specificTimeLabel;
    
    // Fail-safe for missing time
    if (!reqStart) {
        return [{ json: { chat_id: parseInt(userChatId), message: '🕒 *Time Required:* Please specify the time (e.g., "at 2:00 PM tomorrow").', bot_token: botToken, parse_mode: 'Markdown' } }];
    }

    let allEvents = [];
    try { allEvents = $items("Get Calendar Events"); } catch (e) { allEvents = []; }
    const unique = Array.from(new Map(allEvents.filter(e => e.json.id).map(e => [e.json.id, e.json])).values());

    const reqS = new Date(reqStart).getTime();
    const reqE = reqS + 3600000;
    
    const isBusy = unique.some(e => {
        const s = new Date(e.start.dateTime || e.start.date).getTime();
        const en = new Date(e.end.dateTime || e.end.date).getTime();
        return (s < reqE && en > reqS);
    });

    if (isBusy) {
        // SUGGESTION LOGIC
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
        const finalReason = dateQuery.meetingReason;

        if (!finalName || !finalReason) {
             return [{ json: { chat_id: parseInt(userChatId), message: `✅ *${specificTimeLabel}* on ${dateQuery.dateLabel} is available!\n\nPlease send your **Full Name and Reason** (e.g., "Name: Murali, Reason: Industrial Meeting").`, bot_token: botToken, parse_mode: 'Markdown' } }];
        }

        const cleanedReason = finalReason.replace(/\bat\s*\d{1,2}[:\.]?\d{0,2}\s*(am|pm)?/gi, '').replace(/\btomorrow\b|\btoday\b|\bnext day\b/gi, '').replace(/\s\s+/g, ' ').trim();
        const collectorId = '1287706792';
        const msgToCollector = `📅 *New Appointment Request*\n\n👤 *Applicant:* ${finalName}\n🏢 *Reason:* ${cleanedReason}\n🕒 *Time:* ${dateQuery.targetDate} at ${specificTimeLabel}`;
        const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + reqStart }]] };
        
        return [
            { json: { chat_id: parseInt(userChatId), message: `✅ *Request Sent*\n\nYour appointment for *${specificTimeLabel}* has been sent for approval.`, bot_token: botToken, parse_mode: 'Markdown' } },
            { json: { chat_id: parseInt(collectorId), message: msgToCollector, bot_token: botToken, reply_markup: kb, parse_mode: 'Markdown' } }
        ];
    }
}

// Handle View Calendar for Non-Owners
if (dateQuery.intent === 'view_calendar') {
    if (!dateQuery.isOwner) {
        return [{ json: { chat_id: parseInt(userChatId), message: '🔒 *Privacy Restriction*\n\nOnly authorized personnel can view the full schedule. If you want to meet the Collector, please ask to "Book an appointment".', bot_token: botToken, parse_mode: 'Markdown' } }];
    }
    // Owner view...
    let allEvents = [];
    try { allEvents = $items("Get Calendar Events"); } catch (e) { allEvents = []; }
    const upcoming = allEvents.map(e => e.json).filter(e => new Date(e.end.dateTime || e.end.date).getTime() > (dateQuery.msgNowMs - 60000));
    let msg = `📅 *Schedule for ${dateQuery.dateLabel}*\n\n`;
    if (upcoming.length === 0) {
        msg += 'No meetings scheduled! ✅';
    } else {
        upcoming.forEach((e, i) => {
            const s = new Date(e.start.dateTime || e.start.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            const en = new Date(e.end.dateTime || e.end.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
            msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + s + ' - ' + en + '\n\n';
        });
    }
    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken, parse_mode: 'Markdown' } }];
}

// Default fail-safe message
return [{ json: { chat_id: parseInt(userChatId), message: '🤖 *I am here!* How can I help you today? If you want to meet the Collector, just say "Book an appointment".', bot_token: botToken, parse_mode: 'Markdown' } }];'''

# 3. Add Final Respond Node Connection (Fix the Hang)
if 'Send Calendar Response' not in data['connections']:
    data['connections']['Send Calendar Response'] = {
        "main": [
            [
                {
                    "node": "Respond Success",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Citizen-First logic applied and workflow hang fixed.")
