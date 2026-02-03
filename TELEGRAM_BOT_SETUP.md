# Telegram Bot Setup Guide

## 🎯 Purpose

This guide helps you set up a Telegram bot for **demo purposes** while waiting for Meta WhatsApp Business API verification. Your WhatsApp workflows remain unchanged and ready for production.

## 📋 Quick Setup (5 Minutes)

### Step 1: Create Telegram Bot

1. **Open Telegram** on your phone or desktop
2. **Search for** `@BotFather` (official Telegram bot)
3. **Start a chat** with BotFather
4. **Send command**: `/newbot`
5. **Follow the prompts**:
   - Bot name: `AP Government AI Assistant` (or your choice)
   - Bot username: `ap_gov_ai_assistant_bot` (must end with `_bot`)
6. **Save the bot token** - it looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Configure Bot Settings

Send these commands to BotFather:

```
/setdescription
```
Then select your bot and paste:
```
AI Personal Assistant for Government of Andhra Pradesh Officers. Automatically analyzes messages, creates tasks, and manages calendar events.
```

```
/setabouttext
```
Then select your bot and paste:
```
Official AI Assistant for AP Government Officers
```

```
/setcommands
```
Then select your bot and paste:
```
start - Start the assistant
help - Get help
status - Check system status
```

### Step 3: Get Your Chat ID

1. **Send a message** to your bot (any message)
2. **Open this URL** in browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. **Find your chat ID** in the response:
   ```json
   {
     "result": [{
       "message": {
         "chat": {
           "id": 123456789  ← This is your chat ID
         }
       }
     }]
   }
   ```

### Step 4: Create Telegram Groups (Optional)

For department routing demo:

1. **Create 3 Telegram groups**:
   - `AP Gov - Disaster Management`
   - `AP Gov - Electricity Department`
   - `AP Gov - Infrastructure`

2. **Add your bot** to each group (as admin)

3. **Get group chat IDs**:
   - Send a message in each group
   - Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
   - Find negative chat IDs (like `-1001234567890`)

### Step 5: Update Configuration

Edit `n8n-workflows/telegram_config.json` with your values:

```json
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "webhook_url": "http://localhost:5678/webhook/telegram-intake",
  "department_groups": {
    "disaster_management": {
      "chat_id": "-1001234567890",
      "name": "AP Gov - Disaster Management"
    },
    "electricity": {
      "chat_id": "-1001234567891",
      "name": "AP Gov - Electricity Department"
    },
    "infrastructure": {
      "chat_id": "-1001234567892",
      "name": "AP Gov - Infrastructure"
    }
  },
  "collector": {
    "chat_id": "123456789",
    "name": "Murali (Collector)"
  },
  "allowed_users": [
    123456789
  ]
}
```

## 🔧 Import Telegram Workflows to n8n

1. **Open n8n**: http://localhost:5678
2. **Import workflows**:
   - `01-telegram-intake.json`
   - `07-telegram-group-router.json`
3. **Activate both workflows**

## 🧪 Test Your Bot

### Test 1: Basic Message

Send this to your bot:
```
Urgent: Flood alert in Vijayawada. Immediate action required.
```

**Expected**: Bot receives message, AI analyzes it, stores in MongoDB

### Test 2: Department Routing

Send this to your bot:
```
Power outage in Krishna district affecting 5000 homes. Need immediate restoration.
```

**Expected**: Message routed to Electricity Department group

### Test 3: Meeting Request

Send this to your bot:
```
Meeting scheduled for 20th January 2026 at 3 PM to discuss budget allocation.
```

**Expected**: Calendar event created, confirmation sent

## 🔄 Switching Between WhatsApp and Telegram

### For Demo (Telegram):
1. **Activate** Telegram workflows in n8n
2. **Deactivate** WhatsApp workflows (optional)
3. Use Telegram bot for demonstrations

### For Production (WhatsApp):
1. **Deactivate** Telegram workflows
2. **Activate** WhatsApp workflows
3. Configure Meta WhatsApp Business API
4. Update webhook URLs

## 🎬 Demo Script

### Introduction (30 seconds)
> "This is our AI Personal Assistant for AP Government Officers. It automatically processes messages, detects urgency, and routes them to the right departments."

### Demo Flow (2 minutes)

1. **Send disaster alert** to bot:
   ```
   URGENT: Cyclone warning for Visakhapatnam. Evacuate coastal areas immediately.
   ```
   
   **Show**:
   - Bot receives message instantly
   - AI detects: High Priority, Disaster Alert
   - Message appears in Disaster Management group
   - Collector receives summary

2. **Send routine update**:
   ```
   FYI: New circular regarding office timings uploaded to portal.
   ```
   
   **Show**:
   - AI detects: Low Priority, FYI
   - Stored for weekly digest
   - No immediate alerts

3. **Send meeting request**:
   ```
   Meeting on 25th January at 2 PM for infrastructure review.
   ```
   
   **Show**:
   - AI extracts date/time
   - Calendar event created
   - Confirmation sent

### Conclusion (30 seconds)
> "The system works identically with WhatsApp Business API. We're using Telegram for this demo while our WhatsApp verification is in progress."

## 🐛 Troubleshooting

### Bot doesn't respond
- Check bot token is correct
- Verify n8n workflows are active
- Check n8n logs: `docker-compose logs -f n8n`

### Messages not routing to groups
- Verify bot is admin in groups
- Check group chat IDs are correct (negative numbers)
- Ensure `telegram_config.json` is loaded correctly

### AI analysis not working
- Check AI service is running: http://localhost:8000/health
- Verify MongoDB connection
- Check n8n logs for errors

## 📊 Monitoring During Demo

### n8n Dashboard
- http://localhost:5678
- Shows real-time workflow executions
- View execution history

### MongoDB Data
```bash
docker exec -it ai-assist-mongodb mongosh
use gov_ai_assistant
db.messages.find().sort({created_at: -1}).limit(5)
```

### AI Service Stats
- http://localhost:8000/stats
- Shows processing statistics

## 🔐 Security Notes

- **Keep bot token secret** - don't commit to git
- **Restrict allowed users** - update `allowed_users` in config
- **Use private groups** - don't make department groups public
- **For production**: Use HTTPS webhook URLs

## 📱 Mobile Demo Tips

1. **Install Telegram** on demo device
2. **Add bot** to contacts
3. **Prepare test messages** in advance
4. **Screen mirror** to show live processing
5. **Have backup** screenshots/recordings

## 🎯 Key Points for Demo

✅ **Emphasize**:
- Real-time AI analysis
- Automatic priority detection
- Smart department routing
- Same system works with WhatsApp

❌ **Don't mention**:
- Meta verification issues
- This is temporary
- Technical implementation details

## 🔄 After Meta Verification

Once WhatsApp Business API is approved:

1. Keep Telegram workflows as backup
2. Activate WhatsApp workflows
3. Update webhook URLs to Meta
4. Test thoroughly
5. Switch production traffic to WhatsApp

Both systems can run in parallel if needed!

---

**Need Help?** Check the main README.md or contact the development team.
