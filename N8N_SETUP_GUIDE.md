# 🔧 N8N SETUP & TROUBLESHOOTING GUIDE

## ❌ PROBLEM: N8N Pipelines Not Working

## ✅ SOLUTION: Complete Setup Guide

---

## 📋 **PREREQUISITES**

Before n8n can work, you need:

1. **Docker Desktop** installed and running
2. **Docker Compose** available
3. **Ports available**: 5678 (n8n), 27017 (MongoDB), 5432 (PostgreSQL), 8081 (MongoDB Express)

---

## 🚀 **STEP-BY-STEP SETUP**

### **Step 1: Install Docker Desktop**

1. Download Docker Desktop for Windows:
   - Visit: https://www.docker.com/products/docker-desktop
   - Download and install
   - Restart your computer

2. Verify Docker installation:
```powershell
docker --version
docker-compose --version
```

Expected output:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

---

### **Step 2: Start Docker Containers**

1. Open PowerShell in project directory:
```powershell
cd "d:\AI Assist"
```

2. Start all services:
```powershell
docker-compose up -d
```

3. Verify containers are running:
```powershell
docker ps
```

You should see 4 containers:
- `ai-assist-mongodb`
- `ai-assist-postgres`
- `ai-assist-n8n`
- `ai-assist-mongo-express`

---

### **Step 3: Access n8n**

1. Open browser and go to:
```
http://localhost:5678
```

2. **First-time setup:**
   - Create admin account
   - Email: admin@govap.in
   - Password: (choose a strong password)

3. You'll see the n8n dashboard

---

### **Step 4: Configure MongoDB Credentials in n8n**

1. In n8n, click **"Credentials"** in left sidebar

2. Click **"+ New Credential"**

3. Search for **"MongoDB"**

4. Fill in details:
   - **Name**: MongoDB - Gov AI Assistant
   - **Host**: mongodb
   - **Port**: 27017
   - **Database**: gov_ai_assistant
   - **User**: (leave empty for no auth)
   - **Password**: (leave empty for no auth)

5. Click **"Save"**

---

### **Step 5: Import Workflows**

1. In n8n, click **"Workflows"** in left sidebar

2. Click **"+ Add Workflow"**

3. Click the **three dots menu** (⋮) in top-right

4. Select **"Import from File"**

5. Import each workflow file:
   - `n8n-workflows/01-whatsapp-intake.json`
   - `n8n-workflows/02-ai-processing.json`
   - `n8n-workflows/03-rule-routing.json`
   - `n8n-workflows/04-task-creation.json`
   - `n8n-workflows/05-calendar-management.json`
   - `n8n-workflows/06-weekly-digest.json`

6. For each workflow:
   - Click **"Save"**
   - Click **"Activate"** (toggle switch in top-right)

---

### **Step 6: Test WhatsApp Intake Workflow**

1. Open workflow: **"01 - WhatsApp Message Intake"**

2. Click on **"Webhook - WhatsApp Intake"** node

3. Copy the webhook URL (something like):
```
http://localhost:5678/webhook/whatsapp-intake
```

4. Test with curl or Postman:
```powershell
curl -X POST http://localhost:5678/webhook/whatsapp-intake `
  -H "Content-Type: application/json" `
  -d '{
    "message_text": "Urgent: Flood alert in Vijayawada district",
    "forwarded_from": "District Collector",
    "sender_role": "Government Official",
    "timestamp": "2026-01-12T15:00:00Z",
    "attachments": []
  }'
```

5. Expected response:
```json
{
  "status": "success",
  "message_id": "...",
  "priority": "high",
  "intent": "disaster_alert"
}
```

---

## 🔍 **TROUBLESHOOTING**

### **Issue 1: Docker not found**

**Error**: `docker: The term 'docker' is not recognized`

**Solution**:
1. Install Docker Desktop
2. Restart PowerShell
3. Verify: `docker --version`

---

### **Issue 2: Containers won't start**

**Error**: `Cannot start service...`

**Solution**:
```powershell
# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

### **Issue 3: n8n can't connect to MongoDB**

**Error**: `Connection refused` or `ECONNREFUSED`

**Solution**:
1. Check MongoDB is running:
```powershell
docker ps | findstr mongodb
```

2. Verify MongoDB credentials in n8n:
   - Host: `mongodb` (not localhost)
   - Port: `27017`
   - Database: `gov_ai_assistant`

3. Test MongoDB connection:
```powershell
docker exec -it ai-assist-mongodb mongosh
```

---

### **Issue 4: AI Service not reachable**

**Error**: `Cannot reach http://host.docker.internal:8000`

**Solution**:
1. Check if AI service is running:
```powershell
docker ps | findstr ai-service
```

2. If not running, start it:
```powershell
cd ai-service
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. Test AI service:
```powershell
curl http://localhost:8000/health
```

---

### **Issue 5: Workflow not activating**

**Error**: Workflow shows as inactive

**Solution**:
1. Open the workflow
2. Check for red error nodes
3. Fix any configuration issues
4. Click **"Save"**
5. Toggle **"Active"** switch

---

### **Issue 6: Webhook not responding**

**Error**: `404 Not Found` or `Webhook not found`

**Solution**:
1. Ensure workflow is **activated**
2. Check webhook path matches:
   - Workflow: `/whatsapp-intake`
   - URL: `http://localhost:5678/webhook/whatsapp-intake`
3. Restart n8n:
```powershell
docker-compose restart n8n
```

---

## 📊 **VERIFY SETUP**

### **Check 1: All Containers Running**
```powershell
docker ps
```

Should show:
- ✅ mongodb (port 27017)
- ✅ postgres (port 5432)
- ✅ n8n (port 5678)
- ✅ mongo-express (port 8081)

### **Check 2: n8n Accessible**
```
http://localhost:5678
```
Should show n8n login/dashboard

### **Check 3: MongoDB Accessible**
```
http://localhost:8081
```
Should show MongoDB Express UI

### **Check 4: AI Service Running**
```powershell
curl http://localhost:8000/health
```
Should return: `{"status": "healthy"}`

### **Check 5: Workflows Imported**
In n8n, you should see 6 workflows:
1. ✅ 01 - WhatsApp Message Intake
2. ✅ 02 - AI Processing
3. ✅ 03 - Rule Routing
4. ✅ 04 - Task Creation
5. ✅ 05 - Calendar Management
6. ✅ 06 - Weekly Digest

### **Check 6: Workflows Activated**
Each workflow should have green "Active" toggle

---

## 🧪 **COMPLETE TEST FLOW**

### **Test 1: Send Test Message**
```powershell
curl -X POST http://localhost:5678/webhook/whatsapp-intake `
  -H "Content-Type: application/json" `
  -d '{
    "message_text": "Meeting scheduled for tomorrow at 10 AM in Guntur",
    "forwarded_from": "Secretary",
    "sender_role": "Government Official",
    "timestamp": "2026-01-12T15:00:00Z"
  }'
```

### **Test 2: Check MongoDB**
1. Go to: http://localhost:8081
2. Select database: `gov_ai_assistant`
3. Select collection: `messages`
4. You should see the test message with AI analysis

### **Test 3: Check Audit Logs**
1. In MongoDB Express
2. Select collection: `audit_logs`
3. You should see processing logs

### **Test 4: Check n8n Execution**
1. In n8n dashboard
2. Click **"Executions"** in left sidebar
3. You should see successful executions

---

## 🔧 **QUICK FIX COMMANDS**

### **Restart Everything**
```powershell
docker-compose down
docker-compose up -d
```

### **View Logs**
```powershell
# All services
docker-compose logs -f

# Just n8n
docker-compose logs -f n8n

# Just MongoDB
docker-compose logs -f mongodb
```

### **Reset Database**
```powershell
docker-compose down -v
docker-compose up -d
node database/init_db.js
```

### **Rebuild Containers**
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 **WORKFLOW ENDPOINTS**

After setup, these endpoints will be available:

1. **WhatsApp Intake**:
   ```
   POST http://localhost:5678/webhook/whatsapp-intake
   ```

2. **n8n Dashboard**:
   ```
   http://localhost:5678
   ```

3. **MongoDB Express**:
   ```
   http://localhost:8081
   ```

4. **AI Service**:
   ```
   http://localhost:8000
   ```

---

## ✅ **SUCCESS CHECKLIST**

- [ ] Docker Desktop installed and running
- [ ] All 4 containers running (`docker ps`)
- [ ] n8n accessible at http://localhost:5678
- [ ] MongoDB credentials configured in n8n
- [ ] All 6 workflows imported
- [ ] All workflows activated (green toggle)
- [ ] AI service running at http://localhost:8000
- [ ] Test message processed successfully
- [ ] Message visible in MongoDB
- [ ] Execution visible in n8n

---

## 🆘 **STILL NOT WORKING?**

### **Option 1: Check Docker Desktop**
- Open Docker Desktop
- Ensure it's running (green icon in system tray)
- Check "Containers" tab for running containers

### **Option 2: Check Ports**
```powershell
netstat -ano | findstr "5678"
netstat -ano | findstr "27017"
netstat -ano | findstr "8000"
```

### **Option 3: Fresh Start**
```powershell
# Complete reset
docker-compose down -v
docker system prune -a
docker-compose up -d

# Wait 30 seconds
timeout /t 30

# Initialize database
node database/init_db.js

# Import workflows manually in n8n UI
```

---

## 📞 **COMMON ERRORS & FIXES**

| Error | Cause | Fix |
|-------|-------|-----|
| `Docker not found` | Docker not installed | Install Docker Desktop |
| `Port already in use` | Port conflict | Change port in docker-compose.yml |
| `Connection refused` | Service not running | Check `docker ps` |
| `Webhook 404` | Workflow not active | Activate workflow in n8n |
| `MongoDB error` | Wrong credentials | Update credentials in n8n |
| `AI service timeout` | Service not running | Start AI service |

---

## 🎯 **NEXT STEPS**

Once n8n is working:

1. ✅ Test all 6 workflows
2. ✅ Configure production webhooks
3. ✅ Set up monitoring
4. ✅ Configure alerts
5. ✅ Test end-to-end flow
6. ✅ Load synthetic data
7. ✅ Verify dashboard integration

---

**n8n Workflows Status**: Ready to configure

**Action Required**: Install Docker Desktop and follow setup steps

**Estimated Setup Time**: 15-20 minutes

---

**Government of Andhra Pradesh**  
**AI Personal Assistant - n8n Setup Guide** 🔧
