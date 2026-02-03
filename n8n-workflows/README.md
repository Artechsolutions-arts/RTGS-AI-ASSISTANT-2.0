# n8n Workflows - Folder Structure

This directory contains all n8n workflows for the Government AI Personal Assistant project, organized by platform and functionality.

## Folder Structure

```
n8n-workflows/
├── telegram/           # Telegram-specific workflows
├── whatsapp/          # WhatsApp-specific workflows
└── shared/            # Platform-agnostic workflows
```

---

## 📱 Telegram Workflows

**Location:** `telegram/`

| File | Description | Status |
|------|-------------|--------|
| `01-telegram-intake.json` | Main message intake workflow | ✅ Active |
| `02-telegram-callback-handler.json` | Handles inline button callbacks | ✅ Active |
| `07-telegram-group-router.json` | Routes messages to department groups | ⚠️ Optional |
| `telegram_config.json` | Telegram bot configuration | 🔧 Config |

**Key Features:**
- Message intake and processing
- Inline button status updates
- Department group routing
- AI analysis integration

---

## 💬 WhatsApp Workflows

**Location:** `whatsapp/`

| File | Description | Status |
|------|-------------|--------|
| `01-whatsapp-intake.json` | Main message intake workflow | ⚠️ Inactive |
| `07-whatsapp-group-router.json` | Routes messages to department groups | ⚠️ Inactive |

**Note:** WhatsApp integration is currently inactive due to hackathon timeline constraints. All functionality is implemented via Telegram.

---

## 🔄 Shared Workflows

**Location:** `shared/`

These workflows work with both Telegram and WhatsApp:

| File | Description | Status |
|------|-------------|--------|
| `03-rule-routing.json` | Rule-based message routing | ✅ Active |
| `03-task-reminders.json` | Daily task reminder system | ✅ Active |
| `04-task-creation.json` | Task extraction and creation | ✅ Active |
| `05-calendar-management.json` | Google Calendar integration | ✅ Active |
| `06-weekly-digest.json` | Weekly report generation | ⚠️ Planned |
| `department_config.json` | Department configuration | 🔧 Config |

---

## 🚀 Quick Start

### Import Telegram Workflows

1. Open n8n at `http://localhost:5678`
2. Navigate to **Workflows**
3. Click **Import from File**
4. Import files in order:
   ```
   telegram/01-telegram-intake.json
   telegram/02-telegram-callback-handler.json
   shared/03-task-reminders.json
   shared/05-calendar-management.json
   ```

### Configure

1. Update `telegram/telegram_config.json` with your bot token
2. Update `shared/department_config.json` with department mappings
3. Set up MongoDB credentials in n8n
4. Set up Google Calendar credentials in n8n

### Activate Workflows

1. Open each workflow in n8n
2. Click the **Activate** toggle
3. Verify webhook URLs are accessible

---

## 📋 Workflow Dependencies

### Telegram Intake Flow
```
01-telegram-intake.json
  ↓
AI Service (task extraction)
  ↓
MongoDB (messages & tasks)
  ↓
02-telegram-callback-handler.json (for status updates)
```

### Task Reminder Flow
```
03-task-reminders.json (scheduled daily)
  ↓
MongoDB (query pending tasks)
  ↓
Telegram API (send reminders)
```

### Calendar Flow
```
05-calendar-management.json
  ↓
Google Calendar API
  ↓
MongoDB (store events)
  ↓
Telegram API (send notifications)
```

---

## 🔧 Configuration Files

### telegram_config.json
```json
{
  "bot_token": "YOUR_BOT_TOKEN",
  "default_chat_id": "YOUR_CHAT_ID",
  "department_groups": {
    "Health": "-1001234567890",
    "Revenue": "-1001234567891"
  }
}
```

### department_config.json
```json
{
  "departments": [
    "Health",
    "Revenue",
    "Education",
    "Infrastructure",
    "Police"
  ],
  "routing_rules": {
    "health": "Health",
    "revenue": "Revenue"
  }
}
```

---

## 📊 Workflow Status

| Category | Total | Active | Inactive | Planned |
|----------|-------|--------|----------|---------|
| Telegram | 4 | 3 | 0 | 1 |
| WhatsApp | 2 | 0 | 2 | 0 |
| Shared | 6 | 4 | 0 | 2 |
| **Total** | **12** | **7** | **2** | **3** |

---

## 🔄 Migration Notes

**Previous Structure:**
- All workflows in root directory
- No organization by platform

**New Structure:**
- Platform-specific folders (telegram, whatsapp)
- Shared workflows folder
- Config files with their respective workflows

**Benefits:**
- ✅ Better organization
- ✅ Easier to find workflows
- ✅ Clear separation of concerns
- ✅ Scalable structure

---

## 📝 Next Steps

1. **Import workflows** to n8n from new locations
2. **Update file paths** in any scripts that reference workflows
3. **Test all workflows** to ensure they work after reorganization
4. **Update documentation** to reflect new paths

---

## 🆘 Troubleshooting

### Workflow Import Issues
- Ensure JSON files are valid
- Check MongoDB credentials are configured
- Verify API endpoints are accessible

### File Path Issues
- Update any hardcoded paths in scripts
- Use relative paths where possible
- Check config file locations

---

## 📚 Related Documentation

- [Status Tracking Setup](../brain/STATUS_TRACKING_SETUP.md)
- [Task Management Setup](../brain/TASK_MANAGEMENT_SETUP.md)
- [Implementation Plan](../brain/implementation_plan.md)
