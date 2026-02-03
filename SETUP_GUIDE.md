# Government AI Personal Assistant - Setup Guide

## 🚀 Quick Start Guide

This guide will help you set up and run the complete Government AI Personal Assistant system in under 10 minutes.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (for Windows): [Download here](https://www.docker.com/products/docker-desktop)
- **Python 3.10+**: [Download here](https://www.python.org/downloads/)
- **Git** (optional): [Download here](https://git-scm.com/downloads)

## Step-by-Step Setup

### Step 1: Start Docker Infrastructure (2 minutes)

Open PowerShell or Command Prompt in the project directory and run:

```powershell
# Start MongoDB, n8n, and PostgreSQL
docker-compose up -d

# Wait for services to be ready (about 60 seconds)
timeout /t 60
```

Verify services are running:
```powershell
docker ps
```

You should see containers for:
- `ai-assist-mongodb`
- `ai-assist-n8n`
- `ai-assist-postgres`
- `ai-assist-mongo-express` (optional)

### Step 2: Initialize MongoDB (1 minute)

```powershell
# Initialize database with schemas and sample data
docker exec -i ai-assist-mongodb mongosh gov_ai_assistant < database/init_db.js
```

Expected output: "✅ Database initialization complete!"

### Step 3: Install AI Service Dependencies (2 minutes)

```powershell
cd ai-service

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm

cd ..
```

### Step 4: Generate Synthetic Data (1 minute)

```powershell
cd synthetic-data

# Generate 500 synthetic messages
python generator.py

# Seed MongoDB with synthetic data
python seed_mongodb.py

cd ..
```

Expected output: "✅ Inserted 500 messages"

### Step 5: Start AI Service (1 minute)

Open a new PowerShell window:

```powershell
cd ai-service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output: "Application startup complete"

Verify AI service is running:
```powershell
curl http://localhost:8000/health
```

### Step 6: Configure n8n Workflows (2 minutes)

1. Open n8n in your browser: http://localhost:5678
2. Login with credentials:
   - Username: `admin`
   - Password: `admin123`

3. Import workflows:
   - Click "Workflows" → "Import from File"
   - Import each workflow from `n8n-workflows/` folder in order:
     1. `01-whatsapp-intake.json`
     2. `03-rule-routing.json`
     3. `04-task-creation.json`
     4. `05-calendar-management.json`
     5. `06-weekly-digest.json`

4. Configure MongoDB credentials:
   - Go to "Credentials" → "Add Credential"
   - Select "MongoDB"
   - Name: `MongoDB - Gov AI Assistant`
   - Connection String: `mongodb://mongodb:27017/gov_ai_assistant`
   - Save

5. Activate all workflows:
   - Click on each workflow
   - Toggle "Active" switch to ON

### Step 7: Open Dashboard (30 seconds)

Simply open `dashboard/index.html` in your web browser:

```powershell
# Windows
start dashboard/index.html

# Or manually open in browser
# File path: d:\AI Assist\dashboard\index.html
```

## 🧪 Testing the System

### Test 1: Send a Disaster Alert

```powershell
curl -X POST http://localhost:5678/webhook/whatsapp-intake `
  -H "Content-Type: application/json" `
  -d '{
    \"message_text\": \"URGENT: Flood alert in Vijayawada. Immediate action required.\",
    \"timestamp\": \"2026-01-12T11:30:00Z\",
    \"forwarded_from\": \"+919876543210\",
    \"sender_role\": \"District Collector\"
  }'
```

**Expected Result:**
- Message saved to MongoDB
- AI analysis performed (Intent: disaster_alert, Priority: high)
- Routed to Disaster Management department
- High priority alert triggered

### Test 2: Send a Meeting Request

```powershell
curl -X POST http://localhost:5678/webhook/whatsapp-intake `
  -H "Content-Type: application/json" `
  -d '{
    \"message_text\": \"Meeting scheduled for 15th January 2026 at 3 PM to discuss budget allocation.\",
    \"timestamp\": \"2026-01-12T12:00:00Z\",
    \"forwarded_from\": \"+919876543211\",
    \"sender_role\": \"Finance Secretary\"
  }'
```

**Expected Result:**
- Message analyzed (Intent: meeting, Priority: medium)
- Calendar event created
- Conflict detection performed
- Confirmation sent

### Test 3: Send a Routine FYI

```powershell
curl -X POST http://localhost:5678/webhook/whatsapp-intake `
  -H "Content-Type: application/json" `
  -d '{
    \"message_text\": \"FYI: New circular regarding office timings has been uploaded to portal.\",
    \"timestamp\": \"2026-01-12T14:00:00Z\",
    \"forwarded_from\": \"+919876543212\",
    \"sender_role\": \"Admin Officer\"
  }'
```

**Expected Result:**
- Message analyzed (Intent: fyi, Priority: low)
- Queued for weekly digest
- No immediate action

## 📊 Monitoring the System

### Access Points

1. **Dashboard**: http://localhost:8080 (or open `dashboard/index.html`)
   - Real-time message statistics
   - Priority distribution
   - Active tasks and events

2. **n8n Workflows**: http://localhost:5678
   - Username: `admin`
   - Password: `admin123`
   - View workflow executions
   - Monitor processing

3. **AI Service API**: http://localhost:8000
   - `/health` - Health check
   - `/stats` - Processing statistics
   - `/analyze` - Analyze message (POST)

4. **MongoDB Express**: http://localhost:8081
   - Username: `admin`
   - Password: `admin123`
   - Browse database collections
   - View documents

### Check System Status

```powershell
# Check Docker containers
docker ps

# Check AI service logs
cd ai-service
# (Check the terminal where uvicorn is running)

# Check n8n logs
docker logs ai-assist-n8n

# Check MongoDB logs
docker logs ai-assist-mongodb
```

## 🔍 Verify Data in MongoDB

Using MongoDB Express (http://localhost:8081):

1. Navigate to `gov_ai_assistant` database
2. Check collections:
   - `messages` - All received messages with AI analysis
   - `tasks` - Created tasks from instructions
   - `calendar_events` - Scheduled meetings
   - `audit_logs` - All system actions
   - `weekly_reports` - Generated digests

## 🛠️ Troubleshooting

### Issue: Docker containers not starting

**Solution:**
```powershell
# Stop all containers
docker-compose down

# Remove volumes (WARNING: This deletes data)
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Issue: AI service fails to start

**Solution:**
```powershell
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
cd ai-service
pip install -r requirements.txt --force-reinstall

# Download spaCy model again
python -m spacy download en_core_web_sm
```

### Issue: n8n workflows not executing

**Solution:**
1. Check MongoDB credentials in n8n
2. Ensure all workflows are activated
3. Check n8n logs: `docker logs ai-assist-n8n`
4. Verify webhook URLs are correct

### Issue: MongoDB connection failed

**Solution:**
```powershell
# Check MongoDB is running
docker ps | findstr mongodb

# Restart MongoDB
docker restart ai-assist-mongodb

# Wait 30 seconds and try again
timeout /t 30
```

## 📈 Performance Tips

### For Better Performance:

1. **Increase Docker Resources**:
   - Open Docker Desktop
   - Settings → Resources
   - Increase Memory to 4GB+
   - Increase CPU to 2+ cores

2. **Optimize MongoDB**:
   - Indexes are created automatically
   - Monitor using MongoDB Express

3. **Scale AI Service**:
   ```powershell
   # Run multiple instances (advanced)
   uvicorn app.main:app --host 0.0.0.0 --port 8001
   uvicorn app.main:app --host 0.0.0.0 --port 8002
   ```

## 🔐 Security Notes

### Default Credentials (CHANGE IN PRODUCTION):

- **n8n**: admin / admin123
- **MongoDB Express**: admin / admin123
- **MongoDB**: No authentication (local only)

### For Production Deployment:

1. Enable MongoDB authentication
2. Use strong passwords
3. Enable HTTPS/TLS
4. Configure firewall rules
5. Use environment variables for secrets

## 📝 Next Steps

### After Setup:

1. **Customize Dictionaries**:
   - Edit `ai-service/dictionaries/*.json`
   - Add your specific districts, mandals, villages
   - Add department names

2. **Adjust Workflows**:
   - Modify routing rules in n8n
   - Customize notification templates
   - Adjust scheduling intervals

3. **Generate More Data**:
   ```powershell
   cd synthetic-data
   python generator.py --count 1000  # Generate 1000 messages
   python seed_mongodb.py
   ```

4. **Test Weekly Digest**:
   - Manually trigger in n8n
   - Or wait for Monday 9 AM

## 🎯 Demo Scenarios

### Scenario 1: Emergency Response (High Priority)

1. Send disaster alert message
2. Check dashboard - should show high priority
3. Verify in MongoDB - message routed to Disaster Management
4. Check audit logs - AI decision recorded

### Scenario 2: Meeting Scheduling

1. Send meeting request
2. Check calendar_events collection
3. Verify conflict detection
4. See confirmation message

### Scenario 3: Task Management

1. Send instruction message
2. Wait 10 minutes (or trigger workflow manually)
3. Check tasks collection - task created
4. Verify deadline and priority

### Scenario 4: Weekly Digest

1. Accumulate low-priority messages
2. Trigger weekly digest workflow in n8n
3. Check weekly_reports collection
4. View generated summary

## 📞 Support

For issues or questions:

1. Check logs in respective terminals
2. Review MongoDB data using MongoDB Express
3. Check n8n execution logs
4. Verify all services are running with `docker ps`

## 🎉 Success Checklist

- [ ] Docker containers running
- [ ] MongoDB initialized with schemas
- [ ] AI service responding to health checks
- [ ] Synthetic data generated and loaded
- [ ] n8n workflows imported and activated
- [ ] Dashboard displaying data
- [ ] Test message processed successfully
- [ ] Task created from instruction
- [ ] Calendar event created from meeting
- [ ] Audit logs recording actions

**Congratulations! Your Government AI Personal Assistant is now fully operational! 🚀**
