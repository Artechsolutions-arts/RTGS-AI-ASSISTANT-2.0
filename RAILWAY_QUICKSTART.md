# 🚀 Quick Railway Deployment Guide

## ⚡ 5-Minute Deployment

### Step 1: Prepare GitHub Repository

```bash
# If not already a git repository
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Railway deployment"

# Create repository on GitHub, then push
git remote add origin https://github.com/YOUR_USERNAME/rtgs-ai-assistant.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Go to** https://railway.app
2. **Sign in** with GitHub
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your rtgs-ai-assistant repository

### Step 3: Add Services

Railway will create one service initially. You need to add 3 more:

#### Service 1: Dashboard (Next.js)

- **Root Directory:** `dashboard`
- **Build Command:** `npm install && npm run build`
- **Start Command:** `npm run start`
- **Port:** 3000

**Environment Variables:**

```
NEXT_PUBLIC_N8N_BASE_URL=https://n8n-production.up.railway.app/webhook
```

#### Service 2: n8n

- **Click** "New Service" → "Docker Image"
- **Image:** `n8nio/n8n:latest`
- **Port:** 5678

**Environment Variables:**

```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-secure-password
WEBHOOK_URL=https://n8n-production.up.railway.app
N8N_HOST=0.0.0.0
N8N_PORT=5678
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=${{Postgres.RAILWAY_PRIVATE_DOMAIN}}
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=${{Postgres.PGDATABASE}}
DB_POSTGRESDB_USER=${{Postgres.PGUSER}}
DB_POSTGRESDB_PASSWORD=${{Postgres.PGPASSWORD}}
MONGODB_URI=mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/
```

#### Service 3: AI Service

- **Root Directory:** `ai-service`
- **Dockerfile Path:** `ai-service/Dockerfile`
- **Port:** 8000

**Environment Variables:**

```
MONGODB_URI=mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/
PORT=8000
```

#### Service 4: PostgreSQL

- **Click** "New" → "Database" → "PostgreSQL"
- Railway will auto-configure this

### Step 4: Configure MongoDB Atlas

1. Go to https://cloud.mongodb.com
2. Navigate to your cluster
3. Click "Network Access"
4. Click "Add IP Address"
5. Add `0.0.0.0/0` (Allow from anywhere)
6. Click "Confirm"

### Step 5: Get Your URLs

After deployment, Railway will give you URLs like:

- Dashboard: `https://dashboard-production.up.railway.app`
- n8n: `https://n8n-production.up.railway.app`
- AI Service: `https://ai-service-production.up.railway.app`

### Step 6: Update Telegram Webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://n8n-production.up.railway.app/webhook/telegram-intake"
```

### Step 7: Import n8n Workflows

1. Go to your n8n URL
2. Login (admin / your-password)
3. Click "Workflows" → "Import"
4. Upload files from `n8n-workflows/shared/` folder
5. Activate all workflows

---

## ✅ Verification

- [ ] Dashboard loads at Railway URL
- [ ] n8n accessible and workflows active
- [ ] AI Service `/health` endpoint responds
- [ ] Send test Telegram message
- [ ] Message appears in dashboard

---

## 💰 Cost

**Railway Free Tier:**

- $5 credit/month
- Good for testing

**Estimated Production Cost:**

- ~$20-30/month for all services

---

## 🆘 Need Help?

Check `RAILWAY_DEPLOYMENT.md` for detailed instructions and troubleshooting.

---

**That's it! Your app should be live in ~10 minutes! 🎉**
