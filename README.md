# Government AI Personal Assistant - Andhra Pradesh

## 🎯 Overview

A government-grade AI Personal Assistant system designed for government officers to manage WhatsApp messages, tasks, calendar events, and automated follow-ups. Built for the Government of Andhra Pradesh hackathon.

> **📱 Demo Option**: While WhatsApp Business API verification is pending, you can use the **Telegram bot integration** to demonstrate the full system functionality. See [TELEGRAM_DEMO_GUIDE.md](./TELEGRAM_DEMO_GUIDE.md) for quick setup.

## 🏗️ Architecture

```
┌─────────────────┐
│  WhatsApp       │
│  (Forwarded)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   n8n Webhook   │
│   Orchestrator  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  FastAPI AI     │◄────►│   MongoDB    │
│  Service        │      │   Database   │
└─────────────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  Rule Engine    │
│  (n8n flows)    │
└─────────────────┘
```

## 🧱 Technology Stack

- **Backend AI**: Python 3.10 + FastAPI
- **NLP**: spaCy, Rule-based NER, Dictionary-based spell correction
- **Database**: MongoDB
- **Workflow Orchestration**: n8n
- **Languages**: English, Telugu, Mixed
- **Deployment**: Docker-ready

## 📁 Project Structure

```
AI-Assist/
├── ai-service/              # FastAPI AI/NLP service
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── nlp_engine.py
│   │   ├── intent_classifier.py
│   │   ├── priority_classifier.py
│   │   ├── ner_engine.py
│   │   ├── language_detector.py
│   │   └── spell_corrector.py
│   ├── dictionaries/
│   │   ├── districts.json
│   │   ├── mandals.json
│   │   ├── villages.json
│   │   └── departments.json
│   ├── requirements.txt
│   └── Dockerfile
├── database/
│   ├── schemas/
│   │   ├── messages.json
│   │   ├── tasks.json
│   │   ├── calendar_events.json
│   │   ├── audit_logs.json
│   │   └── weekly_reports.json
│   ├── seed_data.js
│   └── init_db.js
├── n8n-workflows/
│   ├── 01-whatsapp-intake.json
│   ├── 02-ai-processing.json
│   ├── 03-rule-routing.json
│   ├── 04-task-creation.json
│   ├── 05-calendar-management.json
│   └── 06-weekly-digest.json
├── synthetic-data/
│   ├── generator.py
│   ├── messages.csv
│   ├── messages.json
│   └── seed_mongodb.py
├── dashboard/               # Optional minimal dashboard
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start (5-Minute Setup)

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+ (for n8n)

### Step 1: Start Infrastructure

```bash
# Start MongoDB and n8n
docker-compose up -d
```

### Step 2: Initialize Database

```bash
# Wait for MongoDB to be ready (30 seconds)
timeout /t 30

# Initialize MongoDB with schemas and seed data
docker exec -i ai-assist-mongodb mongosh < database/init_db.js
```

### Step 3: Start AI Service

```bash
cd ai-service
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 4: Import n8n Workflows

1. Open n8n: http://localhost:5678
2. Go to Workflows → Import from File
3. Import all workflows from `n8n-workflows/` folder in order
4. Activate all workflows

### Step 5: Generate Synthetic Data

```bash
cd synthetic-data
python generator.py
python seed_mongodb.py
```

### Step 6: Test the System

```bash
# Send a test WhatsApp message
curl -X POST http://localhost:5678/webhook/whatsapp-intake \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "Urgent: Flood alert in Vijayawada. Immediate action required.",
    "timestamp": "2026-01-12T11:30:00Z",
    "forwarded_from": "+919876543210",
    "sender_role": "District Collector"
  }'
```

## 🧪 Demo Flow (5 Minutes)

### Scenario 1: Disaster Alert (High Priority)

```bash
curl -X POST http://localhost:5678/webhook/whatsapp-intake \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "URGENT: Cyclone warning for Visakhapatnam district. Evacuate coastal areas immediately.",
    "timestamp": "2026-01-12T11:30:00Z",
    "forwarded_from": "+919876543210",
    "sender_role": "Meteorological Officer"
  }'
```

**Expected Flow**:
1. n8n receives webhook
2. AI service detects: Intent=Disaster Alert, Priority=High, Entity=Visakhapatnam
3. Routes to Disaster Management department
4. Creates high-priority task
5. Sends instant alert (simulated WhatsApp)

### Scenario 2: Meeting Request

```bash
curl -X POST http://localhost:5678/webhook/whatsapp-intake \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "Meeting scheduled for 15th January 2026 at 3 PM to discuss budget allocation.",
    "timestamp": "2026-01-12T12:00:00Z",
    "forwarded_from": "+919876543211",
    "sender_role": "Finance Secretary"
  }'
```

**Expected Flow**:
1. AI detects: Intent=Meeting, Priority=Medium
2. Extracts date/time: 2026-01-15 15:00
3. Checks calendar for conflicts
4. Creates calendar event
5. Sends confirmation

### Scenario 3: Routine FYI (Low Priority)

```bash
curl -X POST http://localhost:5678/webhook/whatsapp-intake \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "FYI: New circular regarding office timings has been uploaded to portal.",
    "timestamp": "2026-01-12T14:00:00Z",
    "forwarded_from": "+919876543212",
    "sender_role": "Admin Officer"
  }'
```

**Expected Flow**:
1. AI detects: Intent=FYI, Priority=Low
2. Stores in database
3. Queued for weekly digest
4. No immediate action

## 📊 Database Schema

### Messages Collection

```javascript
{
  _id: ObjectId,
  message_id: String,
  message_text: String,
  timestamp: ISODate,
  forwarded_from: String,
  sender_role: String,
  attachments: Array,
  ai_analysis: {
    language: String,
    intent: String,
    priority: String,
    entities: Object,
    confidence: Number
  },
  routing: {
    department: String,
    assigned_to: String,
    routed_at: ISODate
  },
  status: String,
  created_at: ISODate
}
```

### Tasks Collection

```javascript
{
  _id: ObjectId,
  task_id: String,
  source_message_id: String,
  title: String,
  description: String,
  department: String,
  owner_role: String,
  priority: String,
  deadline: ISODate,
  status: String,
  reminders_sent: Number,
  escalated: Boolean,
  created_at: ISODate,
  updated_at: ISODate
}
```

### Calendar Events Collection

```javascript
{
  _id: ObjectId,
  event_id: String,
  source_message_id: String,
  title: String,
  description: String,
  start_time: ISODate,
  end_time: ISODate,
  location: String,
  attendees: Array,
  conflict_detected: Boolean,
  status: String,
  created_at: ISODate
}
```

## 🔐 Security & Compliance

### Data Masking

Sensitive fields are automatically masked in logs:
- Phone numbers: +91XXXXXX3210
- Personal names: [REDACTED]
- Political keywords: [SENSITIVE]

### Audit Trail

Every AI decision and workflow action is logged:
- Timestamp
- Action type
- Input data (masked)
- Output/decision
- Confidence score
- User/system responsible

### Read-Only Advisory

The system is **advisory only**:
- ✅ Classifies and routes messages
- ✅ Creates task suggestions
- ✅ Detects calendar conflicts
- ❌ Does NOT execute government actions automatically
- ❌ Does NOT send official communications without approval

## 🌐 Language Support

### Supported Languages

1. **English**: Full NLP pipeline
2. **Telugu**: Dictionary-based + transliteration
3. **Mixed (Hinglish/Tenglish)**: Hybrid processing

### Example Messages

**English**:
```
"Urgent flood situation in Krishna district requires immediate attention."
```

**Telugu**:
```
"విజయవాడలో వరద హెచ్చరిక. తక్షణ చర్య అవసరం."
```

**Mixed**:
```
"Vijayawada lo flood alert undi. Immediate action teeskondi."
```

## 📈 Monitoring & Analytics

### Dashboard (Optional)

Access at: http://localhost:8080

Features:
- Real-time message intake
- Priority distribution
- Department workload
- Task completion rates
- Weekly digest preview

### API Endpoints

**AI Service** (http://localhost:8000):
- `POST /analyze` - Analyze message
- `GET /health` - Health check
- `GET /stats` - Processing statistics

**n8n Webhooks** (http://localhost:5678):
- `POST /webhook/whatsapp-intake` - Message intake
- `POST /webhook/task-reminder` - Manual task reminder
- `POST /webhook/weekly-digest` - Trigger weekly digest

## 🔧 Configuration

### AI Service Configuration

Edit `ai-service/app/config.py`:

```python
# NLP Settings
LANGUAGE_DETECTION_THRESHOLD = 0.7
INTENT_CONFIDENCE_THRESHOLD = 0.6
PRIORITY_CONFIDENCE_THRESHOLD = 0.5

# Entity Recognition
NER_ENABLED = True
SPELL_CORRECTION_ENABLED = True

# LLM Fallback (Optional)
USE_LLM_FALLBACK = False
LLM_API_KEY = "your-api-key"
```

### n8n Configuration

Environment variables in `docker-compose.yml`:

```yaml
N8N_BASIC_AUTH_ACTIVE: "true"
N8N_BASIC_AUTH_USER: "admin"
N8N_BASIC_AUTH_PASSWORD: "admin123"
WEBHOOK_URL: "http://localhost:5678"
```

## 🧪 Testing

### Unit Tests

```bash
cd ai-service
pytest tests/
```

### Integration Tests

```bash
# Test full pipeline
python tests/integration_test.py
```

### Load Testing

```bash
# Generate 1000 test messages
cd synthetic-data
python generator.py --count 1000
python load_test.py
```

## 📦 Deployment

### Production Deployment

1. **Update Environment Variables**:
   - Set production MongoDB URI
   - Configure n8n webhook URLs
   - Set secure passwords

2. **Build Docker Images**:
```bash
docker-compose -f docker-compose.prod.yml build
```

3. **Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling

- **AI Service**: Scale horizontally with load balancer
- **MongoDB**: Use replica sets
- **n8n**: Use queue mode for high throughput

## 🛣️ Future Roadmap

### Phase 1 (Current - Hackathon)
- ✅ WhatsApp forward simulation
- ✅ AI classification
- ✅ Task tracking
- ✅ Calendar management
- ✅ Weekly digests

### Phase 2 (Production)
- Real WhatsApp Business API integration
- Multi-officer support
- Advanced NLP with fine-tuned models
- Voice message transcription
- Document OCR and analysis

### Phase 3 (Advanced)
- Multi-language translation
- Predictive task prioritization
- Automated report generation
- Integration with government portals
- Mobile app for officers

## 🤝 Government Compliance

### Data Privacy
- No personal data leaves the system
- All data stored in government-controlled infrastructure
- Encryption at rest and in transit

### Explainability
- Every AI decision includes confidence scores
- Rule-based routing is fully transparent
- Audit logs for all actions

### No Automation of Critical Actions
- System provides recommendations only
- Human officer approval required for:
  - Official communications
  - Resource allocation
  - Policy decisions

### WhatsApp Compliance
- Forward-only model (no group scraping)
- No unauthorized message access
- Officer-initiated forwarding only

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review audit trail in MongoDB
- Contact: [Your Contact Information]

## 📄 License

Government of Andhra Pradesh - Internal Use Only

---

**Built for Government of Andhra Pradesh Hackathon 2026**
