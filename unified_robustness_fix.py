import json

file_path = r'd:\RTGS-AI-ASSISTANT\n8n-workflows\telegram\01-telegram-intake.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for node in data['nodes']:
    # 1. Fix 'Get User History' Node
    if node.get('name') == "Get User History":
        # Use a robust expression for the query
        node['parameters']['query'] = '={{ JSON.stringify({ "$or": [ { "telegram_user_id": String($(\'Parse Telegram Message\').item.json.telegram_user_id) }, { "telegram_user_id": Number($(\'Parse Telegram Message\').item.json.telegram_user_id) } ] }) }}'
        node['parameters']['options'] = {
            "sort": "{ \"timestamp\": -1 }",
            "limit": 5
        }
        node['alwaysOutputData'] = True
        node['notesInFlow'] = True
        node['notes'] = "Fetches recent context"

    # 2. Fix 'Extract Date Query' JS Code
    if node.get('id') == "6a30192d-f46f-4ed8-87cf-3cd917bf2ccd":
        node['parameters']['jsCode'] = r'''const parseData = $('Parse Telegram Message').item.json;
const aiResponse = $('Call AI Service').item.json.analysis || {};
const messageText = (parseData.message_text || '').toLowerCase();

// HISTORY: Get previous messages safely
let history = [];
try { 
    const histNode = $node["Get User History"];
    if (histNode && histNode.runIndex >= 0) {
        history = $items("Get User History").map(i => i.json).filter(j => j && j.message_text);
    }
} catch (e) { history = []; }

const msgIso = parseData.timestamp;
const msgNowMs = new Date(msgIso).getTime();
const istOffset = 5.5 * 60 * 60 * 1000;
const istDate = new Date(msgNowMs + istOffset);

const dateRegex = /\btomorrow\b|\b రేపు\b|\bnext day\b/i;
let isTomorrow = dateRegex.test(messageText);

if (!isTomorrow) {
    // Check history (last 3 messages)
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

const timeMin = `${targetDate}T00:00:00+05:30`;
const timeMax = `${targetDate}T23:59:59+05:30`;

let intent = aiResponse.intent || 'UNKNOWN';
if (/\bmeetings\b|\bschedule\b/i.test(messageText)) intent = 'view_calendar';

const applicantNameMatch = messageText.match(/name:\s*([^,.\n]+)/i);
const reasonMatch = messageText.match(/reason:\s*([^,.\n]+)/i);
const applicantName = applicantNameMatch ? applicantNameMatch[1].trim() : (aiResponse.entities?.person?.[0]?.value || '');
const meetingReason = reasonMatch ? reasonMatch[1].trim() : (aiResponse.entities?.reason?.[0]?.value || '');

if ((applicantName || meetingReason) && intent !== 'view_calendar') {
    intent = 'request_appointment';
}

const OWNERS = ['1287706792', '5309276394', '1371540949'];
const isOwner = OWNERS.includes(String(parseData.telegram_user_id));

let reqStart, reqEnd, specificTimeLabel = '';
const timeRegex = /(\d{1,2})[:\.]?(\d{2})?\s*(am|pm)/i;
let timeMatch = messageText.match(timeRegex);

if (!timeMatch && aiResponse.entities?.time?.[0]?.value) {
    timeMatch = aiResponse.entities.time[0].value.match(timeRegex);
}

if (!timeMatch) {
    // Check history
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
    if (intent !== 'view_calendar') intent = 'request_appointment';
}

return [{
    json: {
        timeMin, timeMax, authorized: true, isOwner, intent, msgNowMs,
        targetDate, reqStart, reqEnd, specificTimeLabel, 
        applicantName, meetingReason, dateLabel, messageText
    }
}];'''

    # 3. Fix 'Format Calendar Response' JS Code (Simplify Prompt)
    if node.get('id') == "eece68d8-5235-446a-b163-a12b9d7fa4c0":
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
                    const str = `${baseDateStr}T${h.toString().padStart(2,'0')}:${m}:00+05:30`;
                    const scanS = new Date(str).getTime();
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

        if (!finalName || !finalReason) {
             return [{ json: { chat_id: parseInt(userChatId), message: `✅ *${specificTimeLabel}* on ${dateQuery.dateLabel} is available!\n\nPlease provide your **Full Name and Reason** to finalize the request (e.g., "Name: Murali, Reason: Industrial Meeting").`, bot_token: botToken, parse_mode: 'Markdown' } }];
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
    upcoming.forEach((e, i) => {
        const s = new Date(e.start.dateTime || e.start.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
        const en = new Date(e.end.dateTime || e.end.date).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata' });
        msg += (i + 1) + '. *' + (e.summary || 'Meeting') + '*\n   🕐 ' + s + ' - ' + en + '\n\n';
    });
    if (upcoming.length === 0) msg += 'No meetings scheduled! ✅';
    return [{ json: { chat_id: parseInt(userChatId), message: msg, bot_token: botToken, parse_mode: 'Markdown' } }];
}
return [];'''

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Unified robustness fix applied for memory and silence.")
