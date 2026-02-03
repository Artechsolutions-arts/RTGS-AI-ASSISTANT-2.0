# Telegram Demo Quick Start Guide

## 🎯 Purpose
Quick guide to set up and demo the Telegram bot integration while waiting for WhatsApp Meta verification.

## ⚡ 5-Minute Setup

### Step 1: Create Telegram Bot (2 minutes)

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose name: `AP Government AI Assistant`
4. Choose username: `ap_gov_ai_assistant_bot` (must end with `_bot`)
5. **Copy the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Update Configuration (1 minute)

Edit `n8n-workflows/telegram_config.json`:

```json
{
  "bot_token": "PASTE_YOUR_BOT_TOKEN_HERE",
  ...
}
```

### Step 3: Import Workflows to n8n (2 minutes)

1. Open n8n: http://localhost:5678
2. Click **Workflows** → **Import from File**
3. Import these files:
   - `n8n-workflows/01-telegram-intake.json`
   - `n8n-workflows/07-telegram-group-router.json`
4. **Activate both workflows** (toggle switch)

### Step 4: Test the Bot

Open Telegram, find your bot, and send:
```
Urgent: Flood alert in Vijayawada. Immediate action required.
```

You should get a response with AI analysis!

## 🎬 Demo Script (3 Minutes)

### Demo Message 1: High Priority Disaster
**Send to bot:**
```
URGENT: Cyclone warning for Visakhapatnam. Evacuate coastal areas immediately.
```

**Show audience:**
- ✅ Bot receives message instantly
- ✅ AI detects: High Priority, Disaster Alert
- ✅ Message stored in MongoDB
- ✅ Bot responds with analysis

### Demo Message 2: Power Outage
**Send to bot:**
```
Power outage in Krishna district affecting 5000 homes. Need immediate restoration.
```

**Show audience:**
- ✅ AI detects: Medium Priority, Electricity Department
- ✅ Would route to Electricity Department group (if configured)

### Demo Message 3: Meeting Request
**Send to bot:**
```
Meeting on 25th January at 2 PM for infrastructure review.
```

**Show audience:**
- ✅ AI extracts date/time automatically
- ✅ Would create calendar event
- ✅ Low priority, no immediate alerts

## 🔧 Optional: Set Up Department Groups

For full demo with group routing:

1. **Create 3 Telegram groups:**
   - `AP Gov - Disaster Management`
   - `AP Gov - Electricity`
   - `AP Gov - Infrastructure`

2. **Add your bot** to each group (as admin)

3. **Get group chat IDs:**
   - Send message in each group
   - Visit: `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
   - Copy the negative chat IDs (like `-1001234567890`)

4. **Update `telegram_config.json`** with the chat IDs

5. **Test department routing:**
   ```bash
   python test_telegram_integration.py
   ```

## 📊 What to Show During Demo

### n8n Dashboard
- http://localhost:5678
- Show real-time workflow executions
- Click on executions to show data flow

### MongoDB Data
```bash
docker exec -it ai-assist-mongodb mongosh
use gov_ai_assistant
db.messages.find().sort({created_at: -1}).limit(3).pretty()
```

### AI Service Stats
- http://localhost:8000/stats
- Shows processing statistics

## 💡 Demo Talking Points

### Introduction
> "We've built an AI Personal Assistant for AP Government Officers. While our WhatsApp Business API verification is in progress with Meta, we're demonstrating the full functionality using Telegram, which has an identical workflow."

### Key Features to Highlight
1. **Instant AI Analysis** - Real-time intent and priority detection
2. **Smart Routing** - Automatic department identification
3. **Multi-language Support** - English, Telugu, and mixed
4. **Calendar Integration** - Automatic event extraction
5. **Task Management** - Priority-based task creation

### Technical Architecture
> "The system uses:
> - FastAPI for AI/NLP processing
> - MongoDB for data storage
> - n8n for workflow orchestration
> - Same AI engine works for both WhatsApp and Telegram"

### Production Readiness
> "Once WhatsApp verification completes:
> - Simply activate WhatsApp workflows
> - Same AI engine, same database
> - Zero code changes needed
> - Both platforms can run in parallel if needed"

## 🐛 Troubleshooting

### Bot doesn't respond
```bash
# Check n8n logs
docker-compose logs -f n8n

# Check AI service
curl http://localhost:8000/health

# Verify workflows are active in n8n dashboard
```

### "Unauthorized" error
- Check bot token in `telegram_config.json`
- Ensure no extra spaces in the token

### Messages not routing to groups
- Verify bot is admin in groups
- Check group chat IDs are negative numbers
- Ensure `telegram_config.json` is loaded correctly

## 🔄 Switching Back to WhatsApp

When Meta verification completes:

1. **In n8n:**
   - Deactivate Telegram workflows
   - Activate WhatsApp workflows

2. **Update WhatsApp webhook URL** in Meta dashboard

3. **Test with WhatsApp** using same test messages

4. **Keep Telegram as backup** - both can run in parallel!

## 📱 Mobile Demo Tips

1. **Prepare test messages** in Telegram Saved Messages
2. **Screen mirror** your phone to projector
3. **Have backup** screenshots ready
4. **Test everything** 30 minutes before demo
5. **Keep n8n dashboard** open on laptop

## ✅ Pre-Demo Checklist

- [ ] Bot token configured
- [ ] Both workflows imported and active
- [ ] AI service running (http://localhost:8000/health)
- [ ] MongoDB running
- [ ] n8n accessible (http://localhost:5678)
- [ ] Test messages prepared
- [ ] Backup screenshots ready
- [ ] Internet connection stable

## 🎯 Success Metrics to Show

- **Response Time**: < 2 seconds
- **AI Accuracy**: Show confidence scores
- **Data Persistence**: Show MongoDB records
- **Scalability**: Mention can handle 1000s of messages

---

**Good luck with your demo! 🚀**

For detailed setup, see [TELEGRAM_BOT_SETUP.md](./TELEGRAM_BOT_SETUP.md)
