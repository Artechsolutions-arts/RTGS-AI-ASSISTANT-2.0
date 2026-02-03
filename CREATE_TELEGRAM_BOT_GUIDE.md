# 📱 Step-by-Step: Create Your Telegram Bot

## Method 1: Using Telegram Mobile App (Recommended - Easiest)

### Step 1: Open Telegram on Your Phone

1. Open the **Telegram** app on your phone
2. Make sure you're logged in

### Step 2: Find BotFather

1. Tap the **Search** icon (🔍) at the top
2. Type: `@BotFather`
3. Select **BotFather** (it has a blue checkmark ✓)

![BotFather Search](https://core.telegram.org/file/811140184/1/zlN4goPTupk/9ff2f2f01c4bd1b013)

### Step 3: Start BotFather

1. Tap **START** button at the bottom
2. You'll see a welcome message with available commands

### Step 4: Create New Bot

1. Send this command: `/newbot`
2. BotFather will ask for a name

### Step 5: Name Your Bot

1. Type a name for your bot (can be anything)
   - Example: `AP Government AI Assistant`
   - Example: `My Demo Bot`
2. Press **Send**

### Step 6: Choose Username

1. BotFather will ask for a username
2. Username **must end with "bot"**
3. Examples:
   - ✅ `ap_gov_ai_assistant_bot`
   - ✅ `my_demo_bot`
   - ✅ `test_assistant_bot`
   - ❌ `my_assistant` (doesn't end with bot)
4. Type your chosen username and send

### Step 7: Get Your Bot Token 🔑

**This is the most important step!**

BotFather will send you a message like:

```
Done! Congratulations on your new bot. You will find it at 
t.me/your_bot_name_bot. You can now add a description...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567

For a description of the Bot API, see this page: 
https://core.telegram.org/bots/api
```

**COPY THE TOKEN!** It looks like:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

### Step 8: Save Your Token

**IMPORTANT**: Copy this token and save it somewhere safe!

You'll need to paste it into `telegram_config.json` in the next step.

---

## Method 2: Using Telegram Desktop

### Step 1: Open Telegram Desktop

1. Open **Telegram Desktop** on your computer
2. Make sure you're logged in

### Step 2: Search for BotFather

1. Click the **Search** field at the top
2. Type: `@BotFather`
3. Click on **BotFather** (verified account with blue checkmark)

### Step 3: Create Bot

1. Click **START** or type `/start`
2. Type `/newbot` and press Enter
3. Follow the same steps as mobile (Steps 5-7 above)

---

## Method 3: Using Telegram Web

### Step 1: Open Telegram Web

1. Go to: https://web.telegram.org
2. Log in with your phone number or QR code

### Step 2: Find BotFather

1. In the search box, type: `@BotFather`
2. Click on the official BotFather account

### Step 3: Create Bot

1. Click **START**
2. Type `/newbot`
3. Follow the prompts (same as above)

---

## 🔧 Configure Your Bot (After Creation)

### Set Bot Description

Send to BotFather:
```
/setdescription
```

Then select your bot and paste:
```
AI Personal Assistant for Government of Andhra Pradesh Officers. Automatically analyzes messages, creates tasks, and manages calendar events.
```

### Set About Text

Send to BotFather:
```
/setabouttext
```

Then select your bot and paste:
```
Official AI Assistant for AP Government Officers
```

### Set Commands

Send to BotFather:
```
/setcommands
```

Then select your bot and paste:
```
start - Start the assistant
help - Get help
status - Check system status
```

---

## 📝 Update Your Configuration

### Step 1: Open Configuration File

Open: `d:\AI Assist\n8n-workflows\telegram_config.json`

### Step 2: Paste Your Bot Token

Find this line:
```json
"bot_token": "YOUR_BOT_TOKEN_HERE",
```

Replace `YOUR_BOT_TOKEN_HERE` with your actual token:
```json
"bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567",
```

### Step 3: Save the File

Press `Ctrl+S` to save

---

## 🧪 Test Your Bot

### Step 1: Find Your Bot

1. In Telegram, search for your bot's username
   - Example: `@ap_gov_ai_assistant_bot`
2. Click on it to open the chat

### Step 2: Start the Bot

1. Click **START** button
2. Or type `/start`

### Step 3: Send a Test Message

Type:
```
Hello! This is a test message.
```

**Note**: The bot won't respond yet because we haven't imported the workflows to n8n. That's the next step!

---

## 🎯 Get Your Chat ID (Optional - For Testing)

### Method 1: Using Browser

1. Send any message to your bot
2. Open this URL in browser (replace YOUR_BOT_TOKEN):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id":123456789}`
4. That number is your chat ID

### Method 2: Using curl (Windows PowerShell)

```powershell
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates"
```

---

## ✅ Checklist

After completing these steps, you should have:

- [x] Created a Telegram bot via BotFather
- [x] Received a bot token
- [x] Saved the bot token
- [x] Updated `telegram_config.json` with your token
- [x] (Optional) Set bot description and commands
- [x] (Optional) Found your chat ID

---

## 🚀 Next Steps

Now that your bot is created:

1. **Import workflows to n8n**:
   - Open http://localhost:5678
   - Import `01-telegram-intake.json`
   - Import `07-telegram-group-router.json`
   - Activate both workflows

2. **Test the integration**:
   ```bash
   python test_telegram_integration.py
   ```

3. **Send a real message to your bot**:
   ```
   Urgent: Flood alert in Vijayawada. Immediate action required.
   ```

4. **You should get a response with AI analysis!** ✅

---

## 🐛 Troubleshooting

### "Username is already taken"
- Try a different username
- Add numbers: `my_bot_2024_bot`
- Make it more specific: `ap_gov_assistant_demo_bot`

### "Can't find BotFather"
- Make sure you search for `@BotFather` (with @)
- Look for the verified account (blue checkmark)
- Official BotFather has username: `@BotFather`

### "Lost my bot token"
- Go back to BotFather
- Send `/mybots`
- Select your bot
- Click "API Token"
- BotFather will show your token again

### "Bot doesn't respond to messages"
- This is normal! The bot won't respond until you:
  1. Update `telegram_config.json` with your token
  2. Import workflows to n8n
  3. Activate the workflows

---

## 🔐 Security Tips

- ✅ **Never share your bot token publicly**
- ✅ **Don't commit the token to git**
- ✅ **Keep `telegram_config.json` private**
- ✅ **Regenerate token if compromised** (via BotFather → /mybots → API Token → Revoke)

---

## 📞 Need Help?

If you get stuck:
1. Check the official Telegram Bot documentation: https://core.telegram.org/bots
2. Review the error messages from BotFather
3. Make sure your username ends with "bot"
4. Try a different username if taken

---

**You're ready! Once you have your bot token, proceed to import the n8n workflows.** 🎉
