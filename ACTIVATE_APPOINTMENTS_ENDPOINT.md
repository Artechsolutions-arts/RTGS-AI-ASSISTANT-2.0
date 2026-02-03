# Quick Fix: Activate Appointments Endpoint

## The Problem

The n8n workflow was imported via CLI, but the webhooks aren't registering properly. This is a known n8n limitation.

## The Solution (2 minutes)

### Step 1: Open n8n UI

1. Go to http://localhost:5678
2. Login with:
   - Username: `admin`
   - Password: `admin123`

### Step 2: Open the Dashboard API Workflow

1. In the left sidebar, click "Workflows"
2. Find and click "**08 - Dashboard API**"
3. The workflow should open in the editor

### Step 3: Activate the Workflow

1. In the top-right corner, you'll see a toggle switch
2. Click it to turn it **ON** (it should turn green/blue)
3. You should see a success message

### Step 4: Test the Endpoint

Run this command in PowerShell:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:5678/webhook/appointments-approved?district=ntr-district"
```

Expected output:

```json
[
  {
    "id": "...",
    "citizen_name": "Citizen",
    "reason": "Approved via Telegram Intake",
    "start": "2026-02-04T14:00:00+05:30",
    "end": "2026-02-04T15:00:00+05:30",
    "status": "approved",
    "approved_at": "...",
    "telegram_id": "unknown"
  },
  ...
]
```

### Step 5: Refresh Dashboard

1. Go to http://localhost:3000/home
2. The "Approved Appointments" block should now show the count
3. Click on it to see the full list

## Alternative: Manual Webhook Test

If you want to test before activating:

1. Open the workflow in n8n UI
2. Click "Execute Workflow" button (play icon)
3. Immediately run:
   ```powershell
   Invoke-RestMethod -Method Get -Uri "http://localhost:5678/webhook-test/appointments-approved?district=ntr-district"
   ```

## Why This Happens

n8n workflows imported via CLI don't automatically register their production webhooks. They need to be opened and saved/activated in the UI at least once to register the webhook endpoints properly.

## What's Already Done

✅ Duplicate workflows cleaned up (deleted 13 old copies)
✅ Latest Dashboard API workflow activated
✅ Appointments database populated (2 appointments)
✅ Dashboard code updated to fetch from appointments endpoint

Just need that one UI activation!
