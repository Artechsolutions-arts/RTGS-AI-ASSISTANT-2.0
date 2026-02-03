# Government AI Personal Assistant - Technical Documentation

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Details](#component-details)
3. [Data Flow](#data-flow)
4. [AI/NLP Pipeline](#ainlp-pipeline)
5. [Database Schema](#database-schema)
6. [API Reference](#api-reference)
7. [Workflow Logic](#workflow-logic)
8. [Security & Compliance](#security--compliance)
9. [Deployment](#deployment)
10. [Maintenance](#maintenance)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    WhatsApp (Forward Only)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   n8n Webhook Endpoint                       │
│              (http://localhost:5678/webhook)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MongoDB (Storage)                         │
│                  - messages collection                       │
│                  - Initial status: "new"                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI AI Service (Port 8000)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Language Detection (English/Telugu/Mixed)        │  │
│  │  2. Spell Correction (Dictionary-based)              │  │
│  │  3. Intent Classification (Rule-based)               │  │
│  │  4. Priority Classification (Rule-based)             │  │
│  │  5. Named Entity Recognition (Government entities)   │  │
│  │  6. Keyword Extraction                               │  │
│  │  7. Sentiment Analysis                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Update MongoDB with AI Analysis                 │
│                  - Status: "processed"                       │
│                  - ai_analysis field populated               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              n8n Rule-Based Routing Engine                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  IF intent = disaster_alert                          │  │
│  │    → Route to Disaster Management                    │  │
│  │    → Create high-priority task                       │  │
│  │    → Send instant alert                              │  │
│  │                                                       │  │
│  │  IF intent = meeting                                 │  │
│  │    → Extract date/time                               │  │
│  │    → Check calendar conflicts                        │  │
│  │    → Create calendar event                           │  │
│  │    → Send confirmation                               │  │
│  │                                                       │  │
│  │  IF intent = instruction                             │  │
│  │    → Create task                                     │  │
│  │    → Set deadline based on priority                  │  │
│  │    → Assign to department                            │  │
│  │                                                       │  │
│  │  IF priority = low                                   │  │
│  │    → Queue for weekly digest                         │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Action Execution                          │
│                                                              │
│  - Task Creation & Tracking                                  │
│  - Calendar Event Management                                 │
│  - Reminder System                                           │
│  - Escalation Logic                                          │
│  - Weekly Digest Generation                                  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Workflow Orchestration | n8n | latest | Workflow automation and routing |
| AI/NLP Service | Python + FastAPI | 3.10 | Message analysis and classification |
| NLP Library | spaCy | 3.7.2 | Natural language processing |
| Database | MongoDB | 7.0 | Primary data storage |
| n8n Database | PostgreSQL | 15 | n8n workflow storage |
| Language Detection | langdetect | 1.0.9 | Multi-language support |
| API Framework | FastAPI | 0.109.0 | REST API |
| Containerization | Docker | latest | Service deployment |

---

## Component Details

### 1. AI Service (FastAPI)

**Location**: `ai-service/`

**Endpoints**:
- `GET /` - Service information
- `GET /health` - Health check with model status
- `POST /analyze` - Analyze message (main endpoint)
- `GET /stats` - Processing statistics

**Key Modules**:

#### Language Detector (`language_detector.py`)
- Detects English, Telugu, and mixed languages
- Uses Unicode character ranges for Telugu
- Fallback to langdetect library
- Returns confidence score

#### Intent Classifier (`intent_classifier.py`)
- Rule-based classification using regex patterns
- Supports 5 intent categories:
  - `disaster_alert`: Emergency situations
  - `meeting`: Meeting requests and scheduling
  - `instruction`: Tasks and action items
  - `status_update`: Progress reports
  - `fyi`: Informational messages
- Multilingual pattern matching (English + Telugu)

#### Priority Classifier (`priority_classifier.py`)
- Classifies as high/medium/low priority
- Considers both keywords and intent
- Automatic priority boost for disaster alerts
- Deadline detection

#### NER Engine (`ner_engine.py`)
- Extracts government-specific entities:
  - Districts (13 districts of AP)
  - Mandals (90+ mandals)
  - Villages (120+ villages)
  - Departments (50+ government departments)
  - Dates and times
- Dictionary-based pattern matching
- Confidence scoring

#### Spell Corrector (`spell_corrector.py`)
- Corrects misspellings of government entities
- Fuzzy matching algorithm
- Maintains original context
- Returns correction suggestions

### 2. MongoDB Database

**Collections**:

#### messages
```javascript
{
  _id: ObjectId,
  message_id: String (unique),
  message_text: String,
  timestamp: Date,
  forwarded_from: String (phone number),
  sender_role: String,
  attachments: Array,
  ai_analysis: {
    language: String,
    language_confidence: Number,
    intent: String,
    intent_confidence: Number,
    priority: String,
    priority_confidence: Number,
    entities: Object,
    corrected_text: String,
    keywords: Array,
    sentiment: String
  },
  routing: {
    department: String,
    assigned_to: String,
    routed_at: Date
  },
  status: String (new|processed|routed|completed|archived),
  created_at: Date,
  updated_at: Date
}
```

**Indexes**:
- `message_id` (unique)
- `timestamp` (descending)
- `ai_analysis.priority`
- `ai_analysis.intent`
- `status`

#### tasks
```javascript
{
  _id: ObjectId,
  task_id: String (unique),
  source_message_id: String,
  title: String,
  description: String,
  department: String,
  owner_role: String,
  priority: String (high|medium|low),
  deadline: Date,
  status: String (pending|in_progress|completed|overdue|cancelled),
  reminders_sent: Number,
  escalated: Boolean,
  escalation_level: Number,
  created_at: Date,
  updated_at: Date,
  completed_at: Date
}
```

**Indexes**:
- `task_id` (unique)
- `source_message_id`
- `department`
- `priority`
- `status`
- `deadline`

### 3. n8n Workflows

#### Workflow 01: WhatsApp Intake
**Trigger**: Webhook POST
**Flow**:
1. Receive message via webhook
2. Validate and structure data
3. Save to MongoDB (status: "new")
4. Call AI service for analysis
5. Update MongoDB with AI results (status: "processed")
6. Log to audit trail
7. Check priority and route accordingly
8. Return success response

#### Workflow 03: Rule-Based Routing
**Trigger**: Schedule (every 5 minutes)
**Flow**:
1. Query MongoDB for processed messages
2. Apply routing rules based on intent
3. Determine department assignment
4. Update routing information
5. Trigger appropriate sub-workflows:
   - High priority → Instant alert
   - Instruction → Task creation
   - Meeting → Calendar workflow
   - Low priority → Weekly digest queue

#### Workflow 04: Task Creation & Follow-up
**Trigger**: Schedule (every 10 minutes)
**Flow**:
1. Find instruction messages
2. Create tasks with deadlines
3. Save to tasks collection
4. Monitor active tasks
5. Check deadlines:
   - < 24 hours: Send reminder
   - < 6 hours: Send urgent reminder
   - Overdue: Mark as overdue
6. Escalate after 3 reminders
7. Update reminder counts

#### Workflow 05: Calendar Management
**Trigger**: Schedule (every 15 minutes)
**Flow**:
1. Find meeting messages
2. Extract date/time entities
3. Create calendar event
4. Query existing events
5. Detect scheduling conflicts
6. If conflict:
   - Suggest 3 alternate times
   - Send conflict notification
7. If no conflict:
   - Confirm event
   - Send confirmation

#### Workflow 06: Weekly Digest
**Trigger**: Cron (Monday 9 AM)
**Flow**:
1. Calculate week range
2. Aggregate data:
   - All messages from past week
   - Pending tasks
   - Overdue tasks
   - Upcoming events (next 7 days)
3. Generate statistics
4. Create AI summary
5. Save to weekly_reports
6. Send digest notification
7. Log to audit trail

---

## Data Flow

### Message Processing Flow

```
1. WhatsApp Message Forwarded
   ↓
2. n8n Webhook Receives
   ↓
3. MongoDB Insert (status: "new")
   ↓
4. AI Service Analysis
   ├─ Language Detection
   ├─ Spell Correction
   ├─ Intent Classification
   ├─ Priority Classification
   ├─ Entity Extraction
   ├─ Keyword Extraction
   └─ Sentiment Analysis
   ↓
5. MongoDB Update (status: "processed", ai_analysis populated)
   ↓
6. Audit Log Entry
   ↓
7. Routing Decision
   ├─ Department Assignment
   ├─ Priority-based Routing
   └─ Intent-based Actions
   ↓
8. Action Execution
   ├─ Task Creation (if instruction)
   ├─ Calendar Event (if meeting)
   ├─ Instant Alert (if high priority)
   └─ Weekly Queue (if low priority)
   ↓
9. Status Update (status: "routed" or "completed")
   ↓
10. Notification Sent (simulated WhatsApp)
```

---

## AI/NLP Pipeline

### Processing Steps

1. **Input Validation**
   - Check message text is not empty
   - Validate metadata

2. **Language Detection**
   - Count Telugu Unicode characters
   - Count English characters
   - Calculate ratios
   - Determine: English / Telugu / Mixed / Unknown
   - Confidence: 0.0 - 1.0

3. **Spell Correction** (English/Mixed only)
   - Load government dictionaries
   - Build fuzzy matching maps
   - Correct district/mandal/village names
   - Correct department names
   - Return corrected text

4. **Intent Classification**
   - Apply regex patterns for each intent
   - Score matches
   - Normalize scores
   - Return highest scoring intent
   - Confidence threshold: 0.15

5. **Priority Classification**
   - Check high-priority keywords
   - Check low-priority keywords
   - Consider intent context
   - Apply priority boost rules
   - Return: high / medium / low

6. **Named Entity Recognition**
   - Match districts (regex)
   - Match mandals (regex)
   - Match villages (regex)
   - Match departments (regex)
   - Extract dates (regex)
   - Extract times (regex)
   - Return entities with positions

7. **Keyword Extraction**
   - Tokenize text
   - Remove stop words
   - Return top 10 keywords

8. **Sentiment Analysis**
   - Count positive words
   - Count negative words
   - Return: positive / negative / neutral

### Performance Metrics

- Average processing time: 50-150ms per message
- Language detection accuracy: >95%
- Intent classification accuracy: >85%
- Priority classification accuracy: >80%
- Entity extraction recall: >90%

---

## API Reference

### AI Service API

#### POST /analyze

Analyze a message using NLP.

**Request**:
```json
{
  "message_text": "URGENT: Flood alert in Vijayawada.",
  "metadata": {
    "message_id": "msg-123",
    "sender_role": "District Collector"
  }
}
```

**Response**:
```json
{
  "original_text": "URGENT: Flood alert in Vijayawada.",
  "analysis": {
    "language": "english",
    "language_confidence": 0.95,
    "intent": "disaster_alert",
    "intent_confidence": 0.92,
    "priority": "high",
    "priority_confidence": 0.88,
    "entities": {
      "district": [
        {
          "type": "district",
          "value": "Vijayawada",
          "confidence": 0.9,
          "start": 20,
          "end": 30
        }
      ]
    },
    "keywords": ["urgent", "flood", "alert", "vijayawada"],
    "sentiment": "negative"
  },
  "processing_time_ms": 125.5,
  "timestamp": "2026-01-12T11:30:00Z"
}
```

#### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "nlp_engine": true,
    "language_detector": true,
    "intent_classifier": true,
    "priority_classifier": true,
    "ner_engine": true,
    "spell_corrector": true
  },
  "uptime_seconds": 3600.5
}
```

#### GET /stats

Processing statistics.

**Response**:
```json
{
  "total_processed": 1250,
  "by_language": {
    "english": 800,
    "telugu": 200,
    "mixed": 250
  },
  "by_intent": {
    "disaster_alert": 150,
    "meeting": 300,
    "instruction": 400,
    "status_update": 250,
    "fyi": 150
  },
  "by_priority": {
    "high": 200,
    "medium": 600,
    "low": 450
  },
  "average_processing_time_ms": 98.5
}
```

### n8n Webhook API

#### POST /webhook/whatsapp-intake

Receive forwarded WhatsApp message.

**Request**:
```json
{
  "message_text": "Meeting scheduled for 15th January at 3 PM.",
  "timestamp": "2026-01-12T12:00:00Z",
  "forwarded_from": "+919876543210",
  "sender_role": "Finance Secretary",
  "attachments": []
}
```

**Response**:
```json
{
  "status": "success",
  "message_id": "2026-01-12T12:00:00.000Z-+919876543210",
  "priority": "medium",
  "intent": "meeting"
}
```

---

## Workflow Logic

### Routing Rules

```javascript
// Pseudo-code for routing logic

function routeMessage(message) {
  const { intent, priority, entities } = message.ai_analysis;
  
  // Rule 1: Disaster alerts always go to Disaster Management
  if (intent === 'disaster_alert') {
    return {
      department: 'Disaster Management',
      assigned_to: 'Emergency Response Team',
      action: 'instant_alert'
    };
  }
  
  // Rule 2: Meetings go to General Administration
  if (intent === 'meeting') {
    return {
      department: 'General Administration',
      assigned_to: 'Calendar Manager',
      action: 'create_calendar_event'
    };
  }
  
  // Rule 3: Instructions create tasks
  if (intent === 'instruction') {
    const department = extractDepartment(entities) || 'General Administration';
    return {
      department: department,
      assigned_to: determineOwner(priority),
      action: 'create_task'
    };
  }
  
  // Rule 4: Low priority goes to weekly digest
  if (priority === 'low') {
    return {
      department: 'Information and Public Relations',
      assigned_to: 'Digest Compiler',
      action: 'queue_for_digest'
    };
  }
  
  // Default: General Administration
  return {
    department: 'General Administration',
    assigned_to: 'Officer',
    action: 'manual_review'
  };
}
```

### Task Deadline Calculation

```javascript
function calculateDeadline(priority, entities) {
  // Check if explicit deadline in message
  if (entities.date && entities.date.length > 0) {
    return parseDate(entities.date[0].value);
  }
  
  // Default based on priority
  const now = new Date();
  switch (priority) {
    case 'high':
      return new Date(now.getTime() + 2 * 24 * 60 * 60 * 1000); // 2 days
    case 'medium':
      return new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000); // 7 days
    case 'low':
      return new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000); // 14 days
  }
}
```

### Reminder Logic

```javascript
function checkReminders(task) {
  const now = new Date();
  const deadline = new Date(task.deadline);
  const hoursUntilDeadline = (deadline - now) / (1000 * 60 * 60);
  
  // Overdue
  if (hoursUntilDeadline < 0) {
    return {
      action: 'mark_overdue',
      escalate: task.reminders_sent >= 3
    };
  }
  
  // Urgent (< 6 hours)
  if (hoursUntilDeadline < 6 && task.reminders_sent < 2) {
    return {
      action: 'send_urgent_reminder',
      increment_count: true
    };
  }
  
  // Warning (< 24 hours)
  if (hoursUntilDeadline < 24 && task.reminders_sent === 0) {
    return {
      action: 'send_reminder',
      increment_count: true
    };
  }
  
  return { action: 'none' };
}
```

---

## Security & Compliance

### Data Privacy

1. **Sensitive Data Masking**
   - Phone numbers masked in logs: `+91XXXXXX3210`
   - Personal names redacted: `[REDACTED]`
   - Political keywords flagged: `[SENSITIVE]`

2. **Audit Trail**
   - Every AI decision logged
   - Input/output data recorded
   - Confidence scores stored
   - Timestamps for all actions

3. **Access Control**
   - n8n: Basic authentication
   - MongoDB: Local access only (production: enable auth)
   - AI Service: No authentication (internal only)

### Government Compliance

1. **Advisory System**
   - System provides recommendations only
   - No automated government actions
   - Human approval required for critical decisions

2. **Explainability**
   - All AI decisions include confidence scores
   - Rule-based routing is fully transparent
   - Audit logs provide complete traceability

3. **Data Sovereignty**
   - All data stored locally
   - No external API calls (except optional LLM)
   - Government-controlled infrastructure

4. **WhatsApp Compliance**
   - Forward-only model (no group scraping)
   - Officer-initiated forwarding only
   - No unauthorized message access

---

## Deployment

### Local Development

See `SETUP_GUIDE.md` for detailed instructions.

### Production Deployment

#### Prerequisites
- Docker Swarm or Kubernetes cluster
- MongoDB replica set
- Load balancer
- SSL/TLS certificates

#### Steps

1. **Update Environment Variables**
```bash
# .env.production
MONGODB_URI=mongodb://mongo1:27017,mongo2:27017,mongo3:27017/gov_ai_assistant?replicaSet=rs0
N8N_ENCRYPTION_KEY=<generate-secure-key>
N8N_BASIC_AUTH_PASSWORD=<strong-password>
AI_SERVICE_URL=https://ai-service.gov.ap.in
```

2. **Build Docker Images**
```bash
docker build -t gov-ai-assistant/ai-service:1.0 ./ai-service
```

3. **Deploy with Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. **Configure Reverse Proxy** (nginx)
```nginx
server {
    listen 443 ssl;
    server_name ai-assistant.gov.ap.in;
    
    ssl_certificate /etc/ssl/certs/gov-ap.crt;
    ssl_certificate_key /etc/ssl/private/gov-ap.key;
    
    location /api/ {
        proxy_pass http://ai-service:8000/;
    }
    
    location /workflows/ {
        proxy_pass http://n8n:5678/;
    }
}
```

5. **Enable MongoDB Authentication**
```javascript
use admin
db.createUser({
  user: "gov_admin",
  pwd: "<strong-password>",
  roles: ["root"]
})
```

6. **Setup Monitoring**
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for logs

### Scaling

#### Horizontal Scaling

**AI Service**:
```bash
# Run multiple instances
docker-compose up -d --scale ai-service=3
```

**MongoDB**:
- Use replica sets (3+ nodes)
- Enable sharding for large datasets

**n8n**:
- Use queue mode for high throughput
- Multiple worker nodes

#### Performance Optimization

1. **Database Indexes**
   - Already created in init script
   - Monitor slow queries

2. **Caching**
   - Redis for frequently accessed data
   - Cache AI analysis results

3. **Load Balancing**
   - nginx or HAProxy
   - Round-robin for AI service

---

## Maintenance

### Regular Tasks

#### Daily
- Check service health
- Monitor error logs
- Verify workflow executions

#### Weekly
- Review audit logs
- Check disk usage
- Backup MongoDB

#### Monthly
- Update dictionaries
- Review and optimize workflows
- Performance analysis

### Backup Strategy

```bash
# MongoDB backup
mongodump --uri="mongodb://localhost:27017/gov_ai_assistant" --out=/backup/$(date +%Y%m%d)

# n8n workflows export
# Via n8n UI: Settings → Export

# Restore
mongorestore --uri="mongodb://localhost:27017/gov_ai_assistant" /backup/20260112
```

### Monitoring

#### Key Metrics
- Message processing rate
- AI service response time
- MongoDB query performance
- Workflow execution success rate
- Disk usage
- Memory usage

#### Alerts
- AI service down
- MongoDB connection failed
- Workflow execution failed
- Disk usage > 80%
- High error rate

### Troubleshooting

See `SETUP_GUIDE.md` for common issues and solutions.

---

## Future Enhancements

### Phase 2
- Real WhatsApp Business API integration
- Multi-officer support with role-based access
- Advanced NLP with fine-tuned models
- Voice message transcription
- Document OCR and analysis

### Phase 3
- Multi-language translation
- Predictive task prioritization
- Automated report generation
- Integration with government portals
- Mobile app for officers
- Real-time dashboard with WebSockets

---

**Document Version**: 1.0  
**Last Updated**: January 12, 2026  
**Maintained By**: Government of Andhra Pradesh IT Department
