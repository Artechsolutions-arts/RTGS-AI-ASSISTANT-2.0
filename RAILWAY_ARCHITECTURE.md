# 🏗️ Railway Deployment Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY PLATFORM                         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Your GitHub Repository                   │ │
│  │              github.com/YOUR_USERNAME/rtgs-ai              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                              │ Auto-Deploy                        │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Railway Project                           ││
│  │                                                              ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     ││
│  │  │  Dashboard   │  │     n8n      │  │  AI Service  │     ││
│  │  │  (Next.js)   │  │   (Docker)   │  │   (Docker)   │     ││
│  │  │              │  │              │  │              │     ││
│  │  │  Port: 3000  │  │  Port: 5678  │  │  Port: 8000  │     ││
│  │  │              │  │              │  │              │     ││
│  │  │ dashboard-   │  │  n8n-        │  │ ai-service-  │     ││
│  │  │ production   │  │  production  │  │ production   │     ││
│  │  │ .railway.app │  │ .railway.app │  │ .railway.app │     ││
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     ││
│  │         │                  │                  │             ││
│  │         │                  │                  │             ││
│  │         └──────────────────┼──────────────────┘             ││
│  │                            │                                ││
│  │                            ▼                                ││
│  │                  ┌──────────────────┐                       ││
│  │                  │   PostgreSQL     │                       ││
│  │                  │  (Railway DB)    │                       ││
│  │                  │                  │                       ││
│  │                  │  For n8n state   │                       ││
│  │                  └──────────────────┘                       ││
│  │                                                              ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Connects to
                              ▼
                   ┌──────────────────────┐
                   │   MongoDB Atlas      │
                   │   (Cloud Database)   │
                   │                      │
                   │  • Messages          │
                   │  • Calendar Events   │
                   │  • Appointments      │
                   └──────────────────────┘
                              │
                              │ Webhook
                              ▼
                   ┌──────────────────────┐
                   │   Telegram API       │
                   │                      │
                   │  Your Bot receives   │
                   │  messages here       │
                   └──────────────────────┘
```

---

## Data Flow

```
User sends Telegram message
        │
        ▼
Telegram API
        │
        ▼
n8n Webhook (Railway)
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
  AI Service        MongoDB Atlas
  (Analysis)        (Store message)
        │                 │
        └────────┬────────┘
                 │
                 ▼
          Dashboard (Railway)
                 │
                 ▼
          User sees message
```

---

## Service Communication

```
Dashboard ←──────────────→ n8n API
    │                         │
    │                         │
    ├─────────────────────────┤
    │                         │
    ▼                         ▼
MongoDB Atlas ←──────→ AI Service
```

---

## Environment Variables Flow

```
Railway Dashboard
    │
    ├─→ Dashboard Service
    │   └─→ NEXT_PUBLIC_N8N_BASE_URL
    │
    ├─→ n8n Service
    │   ├─→ N8N_BASIC_AUTH_USER
    │   ├─→ N8N_BASIC_AUTH_PASSWORD
    │   ├─→ WEBHOOK_URL
    │   ├─→ DB_POSTGRESDB_* (auto-injected)
    │   └─→ MONGODB_URI
    │
    ├─→ AI Service
    │   ├─→ MONGODB_URI
    │   └─→ PORT
    │
    └─→ PostgreSQL
        └─→ Auto-configured by Railway
```

---

## Deployment Flow

```
1. Push to GitHub
        │
        ▼
2. Railway detects changes
        │
        ▼
3. Railway builds each service
        │
        ├─→ Dashboard: npm install && npm run build
        ├─→ n8n: Pull Docker image
        └─→ AI Service: Build Dockerfile
        │
        ▼
4. Railway deploys services
        │
        ▼
5. Railway generates URLs
        │
        ├─→ dashboard-production.up.railway.app
        ├─→ n8n-production.up.railway.app
        └─→ ai-service-production.up.railway.app
        │
        ▼
6. Services are live! 🎉
```

---

## Cost Breakdown

```
Railway Free Tier: $5/month credit
├─→ Dashboard:     ~$5/month  (1GB RAM, 1 vCPU)
├─→ n8n:           ~$10/month (2GB RAM, 1 vCPU)
├─→ AI Service:    ~$5/month  (1GB RAM, 1 vCPU)
└─→ PostgreSQL:    ~$5/month  (1GB storage)
                   ──────────
Total Railway:     ~$25/month

MongoDB Atlas:
├─→ Free Tier (M0): $0/month (512MB)
└─→ Production (M10): $9/month (2GB)

TOTAL COST: $25-34/month
```

---

## Scaling Strategy

```
Low Traffic (Testing)
├─→ Railway Free Tier ($5 credit)
├─→ MongoDB Free Tier
└─→ Total: $0-5/month

Medium Traffic (Production)
├─→ Railway Hobby Plan ($25/month)
├─→ MongoDB M10 ($9/month)
└─→ Total: ~$34/month

High Traffic (Scale)
├─→ Railway Pro Plan ($50+/month)
├─→ MongoDB M20 ($25+/month)
├─→ Add CDN (Cloudflare Free)
└─→ Total: $75+/month
```

---

## Security Layers

```
Internet
    │
    ▼
Railway Edge (HTTPS)
    │
    ├─→ Dashboard (Public)
    │   └─→ Authenticated routes
    │
    ├─→ n8n (Basic Auth)
    │   └─→ admin:password
    │
    └─→ AI Service (Internal)
        └─→ Only accessible by n8n
    │
    ▼
MongoDB Atlas
    └─→ IP Whitelist
    └─→ Username/Password
```

---

## Monitoring & Logs

```
Railway Dashboard
    │
    ├─→ Metrics
    │   ├─→ CPU Usage
    │   ├─→ Memory Usage
    │   ├─→ Network Traffic
    │   └─→ Request Count
    │
    ├─→ Logs
    │   ├─→ Build Logs
    │   ├─→ Deploy Logs
    │   └─→ Runtime Logs
    │
    └─→ Alerts
        ├─→ Service Down
        ├─→ High CPU
        └─→ Memory Limit
```

---

## Backup Strategy

```
Automated Backups
    │
    ├─→ MongoDB Atlas
    │   └─→ Daily automatic backups
    │
    ├─→ PostgreSQL (Railway)
    │   └─→ Point-in-time recovery
    │
    └─→ Code (GitHub)
        └─→ Version controlled
```

---

This architecture ensures:
✅ High availability
✅ Auto-scaling
✅ Easy monitoring
✅ Secure connections
✅ Cost-effective
✅ Easy to maintain
