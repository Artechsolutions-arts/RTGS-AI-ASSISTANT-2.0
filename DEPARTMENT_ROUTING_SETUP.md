# Multi-Department WhatsApp Routing - Setup Guide

## 🎯 Overview

This system routes incident updates from department heads to their respective WhatsApp groups and notifies the District Collector.

### People & Roles

| Name | Role | Phone | Sends To |
|------|------|-------|----------|
| **Pava** | Disaster Management Head | +919876543210 | Disaster Management Group |
| **Santosh** | Electricity Head | +919876543211 | Electricity Department Group |
| **Ramya** | Infrastructure Head | +919876543212 | Infrastructure Department Group |
| **Murali** | District Collector | +919876543213 | Receives summaries from all |

---

## 📋 Setup Steps

### 1. Configure WhatsApp Group IDs

Edit `d:\AI Assist\n8n-workflows\department_config.json`:

```json
{
  "whatsapp_groups": {
    "disaster_management": {
      "group_id": "YOUR_DISASTER_GROUP_ID",
      "webhook_url": "YOUR_WEBHOOK_URL"
    },
    "electricity": {
      "group_id": "YOUR_ELECTRICITY_GROUP_ID",
      "webhook_url": "YOUR_WEBHOOK_URL"
    },
    "infrastructure": {
      "group_id": "YOUR_INFRASTRUCTURE_GROUP_ID",
      "webhook_url": "YOUR_WEBHOOK_URL"
    }
  }
}
```

**To get WhatsApp Group IDs:**
1. Open WhatsApp Business API dashboard
2. Navigate to Groups section
3. Copy the Group ID for each department group
4. Update the `group_id` fields in the config

### 2. Import New Workflow

1. Open n8n: http://localhost:5678
2. Go to **Workflows** → **Import from File**
3. Import: `d:\AI Assist\n8n-workflows\07-whatsapp-group-router.json`
4. **Activate** the workflow

### 3. Configure MongoDB Credentials

In the imported workflow:
1. Click on **Save to MongoDB** node
2. Select existing MongoDB credentials or create new
3. Ensure connection string: `mongodb://mongodb:27017`
4. Database: `gov_ai_assistant`

### 4. Test the System

Run the test script:

```bash
cd "d:\AI Assist"
test_department_routing.bat
```

This will send 3 test messages:
- From Pava (Disaster)
- From Santosh (Electricity)
- From Ramya (Infrastructure)

---

## 🔄 Message Flow

```
Department Head sends WhatsApp message
    ↓
n8n Webhook receives message
    ↓
Identify sender (Pava/Santosh/Ramya)
    ↓
AI analyzes message content
    ↓
Format message for WhatsApp group
    ↓
Send to appropriate group + Notify Murali
    ↓
Save to MongoDB
```

---

## 📱 WhatsApp Integration

### For Testing (Current Setup)

Messages are **logged to console** instead of sent to WhatsApp. Check n8n execution logs to see formatted messages.

### For Production

1. **Get WhatsApp Business API Access**
   - Sign up at https://business.whatsapp.com
   - Verify your business
   - Get API credentials

2. **Update Workflow Nodes**
   
   In `07-whatsapp-group-router.json`, update these nodes:
   
   **Send to WhatsApp Group:**
   ```javascript
   const response = await fetch(data.webhook_url, {
     method: 'POST',
     headers: {
       'Authorization': 'Bearer YOUR_WHATSAPP_TOKEN',
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       messaging_product: 'whatsapp',
       to: data.group_id,
       type: 'text',
       text: { body: data.group_message }
     })
   });
   ```

   **Send to Collector:**
   ```javascript
   const response = await fetch('https://graph.facebook.com/v18.0/YOUR_PHONE_ID/messages', {
     method: 'POST',
     headers: {
       'Authorization': 'Bearer YOUR_WHATSAPP_TOKEN',
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       messaging_product: 'whatsapp',
       to: data.collector_phone,
       type: 'text',
       text: { body: data.collector_message }
     })
   });
   ```

3. **Add WhatsApp Credentials to n8n**
   - Create new credentials in n8n
   - Type: HTTP Header Auth
   - Name: `Authorization`
   - Value: `Bearer YOUR_WHATSAPP_TOKEN`

---

## 📊 Example Messages

### Message from Pava → Disaster Group

**Input:**
```json
{
  "from": "+919876543210",
  "message": "Heavy rainfall in Vijayawada. Flood alert issued."
}
```

**Output to Disaster Management Group:**
```
📢 INCIDENT UPDATE - HIGH

From: Pava (Disaster Management Head)
Department: DISASTER MANAGEMENT
Time: 12 Jan 2026, 5:45 PM

Message:
Heavy rainfall in Vijayawada. Flood alert issued.

---
AI Analysis:
• Priority: HIGH
• Intent: DISASTER ALERT
• Entities: location: Vijayawada
```

**Output to Murali:**
```
📊 DEPARTMENT UPDATE

Pava (Disaster Mgmt) sent update to Disaster Management Group
Priority: HIGH | Intent: DISASTER ALERT

View full details in dashboard.
```

---

## ✅ Verification

### Check n8n Executions
1. Open http://localhost:5678
2. Click **Executions** tab
3. Verify workflow executed successfully
4. Click execution to see message flow

### Check MongoDB
```bash
docker exec -i ai-assist-mongodb mongosh gov_ai_assistant --eval "db.messages.find({}, {sender_info: 1, routing: 1, message_text: 1}).pretty()"
```

### Check Console Logs
```bash
docker logs ai-assist-n8n --tail 50
```

Look for:
```
=== SENDING TO WHATSAPP GROUP ===
Group ID: DISASTER_GROUP_ID
Message: 📢 INCIDENT UPDATE...
===================================
```

---

## 🔧 Customization

### Change Message Format

Edit `department_config.json` → `message_templates`:

```json
{
  "message_templates": {
    "group_update": "Your custom template with {{PLACEHOLDERS}}",
    "collector_summary": "Your custom summary template"
  }
}
```

Available placeholders:
- `{{PRIORITY}}` - HIGH/MEDIUM/LOW
- `{{NAME}}` - Sender name
- `{{ROLE}}` - Sender role
- `{{DEPARTMENT}}` - Department name
- `{{TIMESTAMP}}` - Current time
- `{{MESSAGE}}` - Original message
- `{{INTENT}}` - AI detected intent
- `{{ENTITIES}}` - Extracted entities

### Add More Department Heads

Edit `department_config.json` → `department_heads`:

```json
{
  "+919876543214": {
    "name": "New Person",
    "role": "New Department Head",
    "department": "new_department",
    "whatsapp_group_id": "NEW_GROUP_ID",
    "priority_default": "medium"
  }
}
```

---

## 📞 Troubleshooting

**Issue:** Webhook returns "Unknown sender"
- **Fix:** Add the phone number to `department_config.json` → `department_heads`

**Issue:** MongoDB save fails
- **Fix:** Verify MongoDB credentials in workflow node

**Issue:** AI analysis fails
- **Fix:** Ensure AI service is running on port 8000

**Issue:** WhatsApp messages not sent
- **Fix:** Currently simulated. For production, configure WhatsApp Business API credentials

---

## 🚀 Next Steps

1. ✅ Import workflow to n8n
2. ✅ Configure WhatsApp group IDs
3. ✅ Run test script
4. ⏳ Set up WhatsApp Business API (for production)
5. ⏳ Update workflow with real WhatsApp credentials
6. ⏳ Test with real WhatsApp messages
