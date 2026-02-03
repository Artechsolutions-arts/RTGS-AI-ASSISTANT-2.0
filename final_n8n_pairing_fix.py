import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data['nodes']:
    # 1. Broaden Intent Detection
    if node.get('name') == "Check Intent":
        node['parameters']['rules']['values'][0]['conditions']['conditions'][1]['rightValue'] = r"reason:|raason:|reson:|name:|naam:|appointment|meet|schedule|slot|book|available"
    
    # 2. Fix 'Extract Date Query' JS Code
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd":
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = ($('Call AI Service').item.json && $('Call AI Service').item.json.analysis) || {};
const messageText = (parseData.message_text || '').toLowerCase();

// FAIL-SAFE HISTORY
let history = [];
try { 
    const histItems = $items("Get User History");
    if (histItems && histItems.length > 0) {
        history = histItems.map(i => i.json).filter(j => j && j.message_text);
    }
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
const targetDate = `${yNum}-${pad(mNum)}-${pad(dNum)}`;

let intent = aiResponse.intent || 'UNKNOWN';
if (/\bbook\b|\bappointment\b|\bmeet\b|\bcollector\b|\bavailable\b/i.test(messageText)) {
    intent = 'request_appointment';
}

const nameMatch = messageText.match(/(?:name|naam):\s*([^,.\n]+)/i);
const reasonMatch = messageText.match(/(?:reason|raason|reson|regarding|re|subject):\s*([^,.\n]+)/i);
const applicantName = nameMatch ? nameMatch[1].trim() : (aiResponse.entities?.person?.[0]?.value || '');
const meetingReason = reasonMatch ? reasonMatch[1].trim() : (aiResponse.entities?.reason?.[0]?.value || '');

if ((applicantName || meetingReason) && intent !== 'view_calendar') {
    intent = 'request_appointment';
}

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
    reqStart = `${targetDate}T${pad(h)}:${pad(mins)}:00+05:30`;
    reqEnd = `${targetDate}T${pad(h+1)}:${pad(mins)}:00+05:30`;
    specificTimeLabel = `${timeMatch[1]}:${pad(mins)} ${ampm}`;
}

return [{
    json: {
        timeMin: `${targetDate}T00:00:00+05:30`,
        timeMax: `${targetDate}T23:59:59+05:30`,
        authorized: true, isOwner, intent, msgNowMs,
        targetDate, reqStart, reqEnd, specificTimeLabel, 
        applicantName, meetingReason, dateLabel, messageText
    }
}];'''

    # 3. Fix 'Format Calendar Response' - USE ROBUST DATA ACCESS (Fix for n8n "Paired item data" error)
    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0":
        node['parameters']['jsCode'] = r'''const botToken = '8360642437:AAHCj2KamG8W8J5hsUcvmR3SFbftXKtgh8Y';

// ROBUST DATA ACCESS: Use $items() to avoid "Paired item data unavailable" error
const extractDateItems = $items("Extract Date Query");
const parseMsgItems = $items("Parse Telegram Message");

if (!extractDateItems.length || !parseMsgItems.length) return [];

const dateQuery = extractDateItems[0].json;
const parseData = parseMsgItems[0].json;
const userChatId = parseData.telegram_chat_id || parseData.chat_id || parseData.sender_id;

const reply = (msg, kb) => [{ json: { chat_id: String(userChatId), message: msg, bot_token: botToken, parse_mode: 'Markdown', reply_markup: kb } }];

try {
    if (dateQuery.intent === 'request_appointment') {
        let reqStart = dateQuery.reqStart;
        if (!reqStart) {
            return reply('🕒 *Time Required:* Please specify the time (e.g., "at 2:00 PM tomorrow").');
        }

        let allEvents = [];
        try { 
            allEvents = $items("Get Calendar Events").map(i => i.json);
        } catch (e) { allEvents = []; }

        const reqS = new Date(reqStart).getTime();
        const reqE = reqS + 3600000;
        
        const isBusy = allEvents.some(e => {
            const s = new Date(e.start.dateTime || e.start.date).getTime();
            const en = new Date(e.end.dateTime || e.end.date).getTime();
            return (s < reqE && en > reqS);
        });

        if (isBusy) {
            let suggestion = '';
            let sugDateLabel = dateQuery.dateLabel;
            const pad = (n) => n.toString().padStart(2, '0');
            const scanDay = (baseDateStr) => {
                for (let h = 10; h < 17; h++) {
                    if (h === 13) continue;
                    for (let m of ['00', '30']) {
                        const scanS = new Date(`${baseDateStr}T${pad(h)}:${m}:00+05:30`).getTime();
                        if (scanS < dateQuery.msgNowMs + 600000) continue; 
                        const collision = allEvents.some(e => {
                            const s = new Date(e.start.dateTime || e.start.date).getTime();
                            const en = new Date(e.end.dateTime || e.end.date).getTime();
                            return (s < scanS + 3600000 && en > scanS);
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
            return reply(`❌ *Slot Unavailable*\n\nThe Collector is busy at *${dateQuery.specificTimeLabel}* on *${dateQuery.dateLabel}*.${sugMsg}`);
        } else {
            const name = dateQuery.applicantName;
            const reason = dateQuery.meetingReason;
            if (!name || !reason) {
                 return reply(`✅ *${dateQuery.specificTimeLabel}* on ${dateQuery.dateLabel} is available!\n\nPlease send your **Full Name and Reason** (e.g., "Name: Murali, Reason: Road Issue").`);
            }
            const cleanReason = reason.replace(/\bat\s*\d{1,2}[:\.]?\d{0,2}\s*(am|pm)?/gi, '').replace(/\btomorrow\b|\btoday\b/gi, '').trim();
            const collectorId = '1287706792';
            const msgToCollector = `📅 *New Appointment Request*\n\n👤 *Applicant:* ${name}\n🏢 *Reason:* ${cleanReason}\n🕒 *Time:* ${dateQuery.targetDate} at ${dateQuery.specificTimeLabel}`;
            const kb = { inline_keyboard: [[{ text: "✅ Approve", callback_data: "/approve_" + userChatId + "_" + reqStart }, { text: "❌ Reject", callback_data: "/reject_" + userChatId + "_" + reqStart }]] };
            
            return [
                { json: { chat_id: String(userChatId), message: `✅ *Request Sent*\n\nYour appointment for *${dateQuery.specificTimeLabel}* has been sent for approval.`, bot_token: botToken, parse_mode: 'Markdown' } },
                { json: { chat_id: String(collectorId), message: msgToCollector, bot_token: botToken, reply_markup: kb, parse_mode: 'Markdown' } }
            ];
        }
    }

    if (dateQuery.intent === 'view_calendar') {
        if (!dateQuery.isOwner) return reply('🔒 *Privacy Restriction*\n\nOnly authorized personnel can view the full schedule.');
        let evs = []; try { evs = $items("Get Calendar Events").map(i => i.json); } catch (e) { evs = []; }
        const upcoming = evs.filter(e => new Date(e.end.dateTime || e.end.date).getTime() > (dateQuery.msgNowMs - 60000));
        let msg = `📅 *Schedule for ${dateQuery.dateLabel}*\n\n`;
        if (upcoming.length === 0) msg += 'No meetings scheduled! ✅';
        else upcoming.forEach((e, i) => msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + new Date(e.start.dateTime || e.start.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' }) + '\n\n');
        return reply(msg);
    }
} catch (err) {
    return reply('🤖 *System Notice:* I encountered an error. Please try again or use the format "Name: Murali, Reason: Topic".');
}

return reply('🤖 *I am here!* To book an appointment, please mention the time and date.');'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Paired Item Data fix applied. Bot logic is now fully compatible with n8n version 1.4+")
