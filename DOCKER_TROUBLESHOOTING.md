# 🔧 DOCKER TROUBLESHOOTING & ALTERNATIVE SETUP

## ❌ ISSUE: Docker Engine Not Responding

**Error**: `500 Internal Server Error for API route`

This means Docker Desktop is installed but the Docker Engine isn't fully started yet.

---

## ✅ SOLUTION 1: Restart Docker Desktop (Recommended)

### **Step 1: Restart Docker Desktop**
1. Open **Docker Desktop** application
2. Click the **Docker icon** in system tray (bottom-right)
3. Select **"Quit Docker Desktop"**
4. Wait 10 seconds
5. Open **Docker Desktop** again
6. Wait for "Docker Desktop is running" message

### **Step 2: Verify Docker is Running**
```powershell
# Open PowerShell and run:
docker ps

# Should show empty list or running containers
# NOT an error
```

### **Step 3: Start Services**
```powershell
cd "d:\AI Assist"
docker-compose up -d
```

### **Step 4: Wait for Services**
```powershell
# Wait 30 seconds
timeout /t 30

# Check running containers
docker ps
```

You should see 4 containers:
- mongodb
- postgres
- n8n
- mongo-express

---

## ✅ SOLUTION 2: Use Alternative Setup (Without Docker)

If Docker continues to have issues, you can run the services locally:

### **Option A: Run AI Service Only**

1. **Install Python dependencies**:
```powershell
cd "d:\AI Assist\ai-service"
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Start AI Service**:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Test**:
```powershell
curl http://localhost:8000/health
```

### **Option B: Use Cloud MongoDB (Free)**

Instead of local MongoDB, use MongoDB Atlas (free tier):

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Create free account
3. Create free cluster
4. Get connection string
5. Update n8n credentials with cloud MongoDB

### **Option C: Use Dashboard Only (No Backend)**

The dashboard works perfectly without Docker:

1. **Open Dashboard**:
```
d:\AI Assist\dashboard\index.html
```

2. **Features Available**:
   - ✅ Full UI with all views
   - ✅ Bilingual chatbot (mock data)
   - ✅ Ultra-human voice assistant
   - ✅ Modern SVG icons
   - ✅ Interactive features
   - ✅ Statistics display

3. **What Won't Work**:
   - ❌ Real-time data from MongoDB
   - ❌ n8n workflow automation
   - ❌ AI service API calls

---

## 🔍 TROUBLESHOOTING DOCKER ISSUES

### **Issue 1: Docker Desktop Not Starting**

**Symptoms**: Docker icon shows "Docker Desktop starting..." forever

**Solutions**:
1. **Restart Computer**: Often fixes startup issues
2. **Check WSL 2**: Docker needs WSL 2 on Windows
   ```powershell
   wsl --update
   wsl --set-default-version 2
   ```
3. **Reinstall Docker**: Uninstall and reinstall Docker Desktop

### **Issue 2: WSL 2 Not Installed**

**Error**: "WSL 2 installation is incomplete"

**Solution**:
```powershell
# Install WSL 2
wsl --install

# Restart computer
# Start Docker Desktop again
```

### **Issue 3: Hyper-V Not Enabled**

**Error**: "Hardware assisted virtualization and data execution protection must be enabled"

**Solution**:
1. Open PowerShell as Administrator
2. Run:
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```
3. Restart computer

### **Issue 4: Port Already in Use**

**Error**: "Port 5678 is already allocated"

**Solution**:
```powershell
# Find process using port
netstat -ano | findstr :5678

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### **Issue 5: Images Won't Download**

**Error**: "unable to get image"

**Solution**:
1. **Check Internet**: Ensure stable connection
2. **Pull Manually**:
```powershell
docker pull mongo:7.0
docker pull postgres:15-alpine
docker pull n8nio/n8n:latest
docker pull mongo-express:latest
```
3. **Try Again**:
```powershell
docker-compose up -d
```

---

## 🚀 QUICK FIX COMMANDS

### **Restart Everything**:
```powershell
# Stop all containers
docker-compose down

# Remove all containers and volumes
docker-compose down -v

# Start fresh
docker-compose up -d
```

### **Check Docker Status**:
```powershell
# Check Docker version
docker --version

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Check Docker logs
docker-compose logs
```

### **Reset Docker Desktop**:
1. Open Docker Desktop
2. Click Settings (gear icon)
3. Go to "Troubleshoot"
4. Click "Reset to factory defaults"
5. Restart Docker Desktop

---

## 📋 STEP-BY-STEP: FRESH DOCKER START

### **1. Ensure Docker Desktop is Running**
- Open Docker Desktop app
- Wait for "Docker Desktop is running" in system tray
- Green icon = running
- Orange icon = starting
- Red icon = error

### **2. Open PowerShell in Project Folder**
```powershell
cd "d:\AI Assist"
```

### **3. Pull Images First** (Recommended)
```powershell
docker pull mongo:7.0
docker pull postgres:15-alpine
docker pull n8nio/n8n:latest
docker pull mongo-express:latest
```

### **4. Start Services**
```powershell
docker-compose up -d
```

### **5. Wait and Verify**
```powershell
# Wait 30 seconds
timeout /t 30

# Check containers
docker ps

# Should show 4 running containers
```

### **6. Access Services**
- n8n: http://localhost:5678
- MongoDB Express: http://localhost:8081
- AI Service: http://localhost:8000 (if running)

---

## ✅ VERIFICATION CHECKLIST

- [ ] Docker Desktop installed
- [ ] Docker Desktop running (green icon)
- [ ] WSL 2 installed and updated
- [ ] `docker --version` works
- [ ] `docker ps` works (no error)
- [ ] Images pulled successfully
- [ ] `docker-compose up -d` completes
- [ ] 4 containers running
- [ ] n8n accessible at http://localhost:5678
- [ ] MongoDB Express at http://localhost:8081

---

## 🆘 STILL NOT WORKING?

### **Option 1: Use Dashboard Only**
The dashboard is fully functional without Docker:
```
Open: d:\AI Assist\dashboard\index.html
```
All features work except real-time backend data.

### **Option 2: Manual Service Setup**
Run services individually without Docker:
1. Install MongoDB locally
2. Install PostgreSQL locally
3. Install n8n with npm: `npm install -g n8n`
4. Run AI service with Python

### **Option 3: Cloud Services**
Use cloud alternatives:
1. MongoDB Atlas (free)
2. n8n Cloud (free tier)
3. Deploy AI service to Heroku/Railway

---

## 📞 DOCKER DESKTOP SUPPORT

If Docker Desktop continues to fail:

1. **Check System Requirements**:
   - Windows 10/11 Pro, Enterprise, or Education
   - 64-bit processor with SLAT
   - 4GB RAM minimum
   - BIOS virtualization enabled

2. **Docker Documentation**:
   - https://docs.docker.com/desktop/troubleshoot/overview/

3. **Docker Forums**:
   - https://forums.docker.com/

---

## 🎯 RECOMMENDED APPROACH

**For Now**: Use the dashboard without Docker
- Fully functional UI
- Voice assistant works
- Chatbot works
- All features except backend

**For Production**: Fix Docker and run full stack
- Complete automation
- Real-time data
- Full workflow processing

---

## 📝 CURRENT STATUS

✅ **Docker Installed**: Yes  
⚠️ **Docker Engine**: Not responding  
✅ **Dashboard**: Works without Docker  
✅ **Voice**: Works without Docker  
✅ **Chatbot**: Works without Docker  
⚠️ **n8n**: Needs Docker Engine  
⚠️ **MongoDB**: Needs Docker Engine  

**Recommendation**: 
1. Restart Docker Desktop
2. Try `docker ps` again
3. If works, run `docker-compose up -d`
4. If not, use dashboard-only mode

---

**Next Step**: Restart Docker Desktop and try again!
