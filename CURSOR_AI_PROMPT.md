# 🚀 CURSOR AI PROMPT - Government AI Assistant Project

## Complete Prompt for Cursor AI to Build This Entire Project

Copy and paste this prompt into Cursor AI to recreate the entire Government of Andhra Pradesh AI Personal Assistant system:

---

## 📋 MASTER PROMPT FOR CURSOR AI

```
Create a complete Government of Andhra Pradesh AI Personal Assistant system with the following specifications:

## PROJECT OVERVIEW
Build an end-to-end AI-powered personal assistant for government officers that processes WhatsApp messages in English and Telugu, with a real-time dashboard, bilingual chatbot, and ultra-human-like voice assistant.

## CORE REQUIREMENTS

### 1. AI SERVICE (Python FastAPI)
Create a FastAPI-based AI service in `ai-service/` folder:

**Files to create:**
- `ai-service/app/main.py` - FastAPI application with endpoints:
  - GET /health - Health check
  - POST /analyze - Analyze message (accepts text, returns NLP analysis)
  - GET /stats - Get statistics
  
- `ai-service/app/nlp_engine.py` - Main NLP pipeline orchestrator
- `ai-service/app/language_detector.py` - Detect English, Telugu, or mixed languages using langdetect and Unicode patterns (U+0C00-U+0C7F for Telugu)
- `ai-service/app/spell_corrector.py` - Dictionary-based spell correction for government entities
- `ai-service/app/intent_classifier.py` - Rule-based intent classification (7 categories: disaster_alert, meeting, instruction, query, complaint, information, general)
- `ai-service/app/priority_classifier.py` - Priority detection (high, medium, low) based on keywords
- `ai-service/app/ner_engine.py` - Named Entity Recognition using spaCy to extract: districts, mandals, villages, departments, dates, times, people
- `ai-service/app/models.py` - Pydantic models for request/response validation

**Dictionaries (JSON files in `ai-service/dictionaries/`):**
- `districts.json` - 13 districts of Andhra Pradesh (Visakhapatnam, Vijayawada, Guntur, Tirupati, etc.)
- `mandals.json` - 100+ mandals
- `villages.json` - 200+ villages
- `departments.json` - 30+ government departments (Revenue, Health, Education, Police, etc.)

**Dependencies (`ai-service/requirements.txt`):**
```
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
pydantic==2.5.0
spacy==3.7.2
langdetect==1.0.9
```

**Use spaCy model:** en_core_web_sm

**Design principle:** Rule-based NLP (no deep learning) for explainability and government compliance

---

### 2. DASHBOARD (HTML/CSS/JavaScript)
Create a professional government-style dashboard in `dashboard/` folder:

**Files to create:**
- `dashboard/index.html` - Main HTML with:
  - Modern SVG government emblem (golden star in circle, not emoji)
  - Professional header: "Government of Andhra Pradesh - AI Personal Assistant Dashboard"
  - Navigation: Dashboard, Messages, Tasks, Calendar, Departments, Reports
  - 7 different views with breadcrumb navigation
  - Statistics cards (Total Messages, Pending Tasks, Upcoming Events, Active Departments)
  - Priority distribution chart
  - Intent classification breakdown
  - Department workload grid
  - Modal system for detailed views

- `dashboard/style.css` - Professional government styling:
  - Color scheme: Deep blue (#1A237E), Indigo (#3949AB), Gold (#FFB300), Orange (#FF6F00)
  - Responsive grid layouts
  - Card-based design with hover effects
  - Smooth animations (fade-in, slide-in)
  - Mobile-responsive breakpoints
  - Modern SVG icon styles
  - ~1200 lines of CSS

- `dashboard/app.js` - Interactive JavaScript:
  - View navigation system
  - Mock data generation (42 messages, 17 tasks, 14 events, 12 departments)
  - Filtering and search functionality
  - Modal system for detailed views
  - Real-time clock
  - Click handlers for all interactive elements
  - Department drill-down functionality

- `dashboard/chatbot.js` - Bilingual chatbot:
  - BilingualChatbot class
  - English + Telugu support
  - Intent detection (7+ categories)
  - Quick action buttons (Show Statistics, High Priority Messages, Pending Tasks, Department Info)
  - Language switching (EN/TE toggle)
  - Real-time data integration
  - Modern SVG icons (bot avatar, user avatar, send button, chat bubble)
  - Contextual responses with data from dashboardData
  - Message history
  - Markdown formatting support

- `dashboard/voice-assistant.js` - Ultra-human-like voice assistant:
  - VoiceAssistant class
  - Auto-greeting on page load (2 seconds delay)
  - Speech recognition (Web Speech API) - English (en-US) and Telugu (te-IN)
  - Text-to-speech with ULTRA-HUMAN parameters:
    * Rate: 0.88 (conversational pace)
    * Pitch: 1.08 (natural female)
    * Volume: 0.82 (soft, intimate)
    * Phrase-by-phrase speech (split by commas, periods, semicolons)
    * Natural pauses: 400ms after sentences, 250ms after phrases, 200ms after commas
  - Prioritize FEMALE voices: Samantha, Karen, Google US English Female, Microsoft Zira, etc.
  - 3-pass voice selection algorithm
  - Modern SVG microphone icon with pulse animation
  - Visual feedback (listening indicator, speaking indicator, notifications)
  - Error handling
  - Follow-up questions
  - Console logging for debugging

**Voice greeting:**
- English: "Hello! Welcome to the Government of Andhra Pradesh AI Assistant. I'm here to help you. How may I assist you today?"
- Telugu: "నమస్కారం! ఆంధ్ర ప్రదేశ్ ప్రభుత్వ AI సహాయకుడికి స్వాగతం. నేను మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను. నేను మీకు ఎలా సహాయం చేయగలను?"

**Chatbot welcome:**
- "Hi there! I'm your personal assistant. I can help you check messages and tasks, get department information, view event schedules, and see system statistics. Just let me know what you need!"

**Modern SVG Icons (no emojis):**
- Government emblem: Golden star in circle
- Chat button: Modern chat bubble with dots
- Bot avatar: Friendly robot face
- User avatar: Professional silhouette
- Microphone: Professional mic with stand
- Send button: Paper plane

---

### 3. N8N WORKFLOWS (JSON)
Create 6 n8n workflow files in `n8n-workflows/` folder:

- `01-whatsapp-intake.json` - Webhook receiver, calls AI service, stores in MongoDB
- `02-ai-processing.json` - Batch processing of messages
- `03-rule-routing.json` - Department assignment and routing
- `04-task-creation.json` - Task creation from instruction messages
- `05-calendar-management.json` - Event creation with conflict detection
- `06-weekly-digest.json` - Weekly report generation

---

### 4. DATABASE SCHEMAS (MongoDB)
Create JSON schema files in `database/schemas/`:

- `messages.json` - Message collection schema (sender, text, timestamp, language, intent, priority, entities, department, status)
- `tasks.json` - Task collection schema (title, description, department, assignee, deadline, status, priority)
- `calendar_events.json` - Event collection schema (title, description, start_time, end_time, location, attendees, department)
- `audit_logs.json` - Audit log schema (action, user, timestamp, details, ai_decision)
- `weekly_reports.json` - Report schema (week_start, week_end, summary, statistics, generated_at)

Create `database/init_db.js` - MongoDB initialization script with indexes and sample data

---

### 5. DOCKER SETUP
Create `docker-compose.yml` with services:
- MongoDB 7.0 (port 27017)
- PostgreSQL 15 (port 5432, for n8n)
- n8n (port 5678)
- MongoDB Express (port 8081)

Create `ai-service/Dockerfile`:
- Base: python:3.10
- Install system dependencies
- Install Python packages
- Download spaCy model: python -m spacy download en_core_web_sm
- Health check
- Non-root user

---

### 6. SYNTHETIC DATA
Create `synthetic-data/generator.py`:
- Generate 100+ realistic WhatsApp messages
- Categories: disaster, meeting, instruction, query, complaint
- Bilingual: English and Telugu
- Common typos and variations
- Realistic timestamps
- Output: synthetic_messages.json

Create `synthetic-data/seed_mongodb.py`:
- Load synthetic data into MongoDB
- Connect to MongoDB
- Insert documents
- Verify insertion

---

### 7. DOCUMENTATION
Create comprehensive markdown files:

- `README.md` - Project overview, features, setup instructions
- `SETUP_GUIDE.md` - Step-by-step installation guide
- `TECHNICAL_DOCUMENTATION.md` - Architecture, APIs, database schemas
- `PROJECT_SUMMARY.md` - Deliverables, features, verification checklist
- `SYSTEM_FLOW.md` - ASCII flow diagrams
- `DASHBOARD_FEATURES.md` - Interactive elements guide
- `CHATBOT_DOCUMENTATION.md` - Chatbot features and usage
- `VOICE_ASSISTANT_GUIDE.md` - Voice features and commands
- `COMPLETE_PROJECT_SUMMARY.md` - All tasks performed
- `TECH_STACK_REFERENCE.md` - Technology stack reference
- `VOICE_AND_ICON_IMPROVEMENTS.md` - Voice and icon enhancements
- `FEMALE_VOICE_ENHANCEMENT.md` - Ultra-human voice details

---

### 8. TESTING & VALIDATION
Create `test_integration.py`:
- Test AI service health
- Test message analysis
- Test MongoDB connection
- Test n8n webhooks
- End-to-end flow testing

Create `validate_system.py`:
- Check file existence
- Verify directory structure
- Validate configurations
- Check dependencies
- Data integrity checks
- Generate validation report

---

### 9. AUTOMATION
Create `quick_start.bat` (Windows):
- Check Docker installation
- Start Docker containers
- Wait for services
- Initialize database
- Health checks
- Display URLs

---

## DESIGN PRINCIPLES

1. **Government-Style UI:**
   - Professional, authoritative design
   - Official color scheme (deep blue, gold)
   - Modern SVG icons (NO emojis)
   - Responsive and accessible
   - Clean, organized layout

2. **Ultra-Human Voice:**
   - Female voice prioritization
   - Rate: 0.88 (very slow, conversational)
   - Pitch: 1.08 (natural female)
   - Volume: 0.82 (soft, intimate)
   - Phrase-by-phrase with natural pauses (250-400ms)
   - Conversational, not robotic tone

3. **Bilingual Support:**
   - English and Telugu throughout
   - Language detection and switching
   - Unicode support for Telugu (U+0C00-U+0C7F)
   - Bilingual voice recognition and synthesis

4. **Explainable AI:**
   - Rule-based NLP (no black-box models)
   - Auditable decisions
   - Government compliance
   - Transparent logic

5. **Interactive Dashboard:**
   - All elements clickable
   - Drill-down capabilities
   - Real-time updates
   - Search and filter
   - Modal system

---

## TECHNICAL SPECIFICATIONS

**Languages:**
- Python 3.10 (backend)
- JavaScript ES6+ (frontend)
- HTML5 (structure)
- CSS3 (styling)
- JSON (data/config)
- Markdown (documentation)

**Frameworks:**
- FastAPI (REST API)
- spaCy (NLP)
- n8n (workflow automation)
- Docker (containerization)

**Databases:**
- MongoDB 7.0 (main database)
- PostgreSQL 15 (n8n metadata)

**APIs:**
- Web Speech API (voice recognition)
- SpeechSynthesis API (text-to-speech)
- DOM API (UI manipulation)

**Browser Support:**
- Chrome (recommended)
- Edge
- Safari
- Opera

---

## FILE STRUCTURE
```
d:/AI Assist/
├── ai-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── nlp_engine.py
│   │   ├── language_detector.py
│   │   ├── spell_corrector.py
│   │   ├── intent_classifier.py
│   │   ├── priority_classifier.py
│   │   ├── ner_engine.py
│   │   └── models.py
│   ├── dictionaries/
│   │   ├── districts.json
│   │   ├── mandals.json
│   │   ├── villages.json
│   │   └── departments.json
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── chatbot.js
│   └── voice-assistant.js
├── n8n-workflows/
│   ├── 01-whatsapp-intake.json
│   ├── 02-ai-processing.json
│   ├── 03-rule-routing.json
│   ├── 04-task-creation.json
│   ├── 05-calendar-management.json
│   └── 06-weekly-digest.json
├── database/
│   ├── schemas/
│   │   ├── messages.json
│   │   ├── tasks.json
│   │   ├── calendar_events.json
│   │   ├── audit_logs.json
│   │   └── weekly_reports.json
│   └── init_db.js
├── synthetic-data/
│   ├── generator.py
│   └── seed_mongodb.py
├── docker-compose.yml
├── test_integration.py
├── validate_system.py
├── quick_start.bat
├── README.md
├── SETUP_GUIDE.md
├── TECHNICAL_DOCUMENTATION.md
├── PROJECT_SUMMARY.md
├── SYSTEM_FLOW.md
├── DASHBOARD_FEATURES.md
├── CHATBOT_DOCUMENTATION.md
├── VOICE_ASSISTANT_GUIDE.md
├── COMPLETE_PROJECT_SUMMARY.md
├── TECH_STACK_REFERENCE.md
├── VOICE_AND_ICON_IMPROVEMENTS.md
└── FEMALE_VOICE_ENHANCEMENT.md
```

---

## KEY FEATURES TO IMPLEMENT

1. ✅ AI-powered message processing (English + Telugu)
2. ✅ Real-time monitoring dashboard
3. ✅ Bilingual chatbot with quick actions
4. ✅ Ultra-human-like voice assistant (female, conversational)
5. ✅ Modern SVG icons (no emojis)
6. ✅ Interactive statistics and drill-down
7. ✅ Department-specific views
8. ✅ Search and filter functionality
9. ✅ Modal system for details
10. ✅ Automated workflows (n8n)
11. ✅ Docker containerization
12. ✅ Comprehensive documentation
13. ✅ Testing and validation scripts
14. ✅ Synthetic data generation

---

## VOICE ASSISTANT CRITICAL SPECS

**Must sound like a REAL PERSON, not a bot:**

1. **Speech Parameters:**
   - Rate: 0.88 (very slow, conversational)
   - Pitch: 1.08 (natural female variation)
   - Volume: 0.82 (soft, intimate)

2. **Natural Pauses:**
   - 400ms after sentences (. ! ?)
   - 250ms after phrases
   - 200ms after commas

3. **Phrase Splitting:**
   - Split by: periods, commas, semicolons
   - Speak phrase-by-phrase
   - Skip punctuation-only phrases

4. **Voice Selection Priority:**
   - Samantha (macOS - best)
   - Karen (macOS)
   - Microsoft Zira (Windows)
   - Google US English Female
   - Any female voice
   - Fallback to any voice

5. **Conversational Tone:**
   - "Hi there! I'm your personal assistant"
   - NOT: "I am your AI Assistant"
   - Friendly, warm, human-like

---

## QUALITY STANDARDS

- Code: Clean, well-commented, professional
- UI: Modern, responsive, government-grade
- Voice: Ultra-human, not robotic
- Icons: SVG only, no emojis
- Documentation: Comprehensive, detailed
- Testing: Validated, verified
- Performance: Fast, optimized
- Security: Government compliance

---

## DELIVERABLES

- 50+ source files
- ~13,000 lines of code
- 10+ documentation files
- 6 n8n workflows
- 5 database schemas
- Complete Docker setup
- Testing suite
- Validation scripts

---

## SUCCESS CRITERIA

The system should:
1. Process messages in English and Telugu
2. Classify intent and priority accurately
3. Display real-time dashboard
4. Respond to chatbot queries
5. Speak with ultra-human female voice
6. Use modern SVG icons throughout
7. Be fully interactive and clickable
8. Run in Docker containers
9. Have comprehensive documentation
10. Pass all validation tests

---

START BUILDING THIS COMPLETE SYSTEM NOW.

Create all files, implement all features, and ensure the voice sounds like a REAL HUMAN PERSON having a conversation, not a robotic assistant.

The voice must be slow (0.88 rate), soft (0.82 volume), with natural pauses (250-400ms), and conversational tone.

All icons must be modern SVG graphics, no emojis allowed.

The dashboard must be professional, government-grade quality with full interactivity.

Build the complete end-to-end system as specified above.
```

---

## 📝 USAGE INSTRUCTIONS

1. **Open Cursor AI**
2. **Create new project folder**: `d:/AI Assist/`
3. **Open Cursor Chat** (Ctrl+L or Cmd+L)
4. **Paste the entire prompt above**
5. **Press Enter**
6. **Let Cursor build the entire project**

Cursor will create all 50+ files, implement all features, and build the complete system!

---

## 🎯 EXPECTED RESULT

After Cursor completes, you will have:
- ✅ Complete AI service (Python FastAPI)
- ✅ Professional dashboard (HTML/CSS/JS)
- ✅ Bilingual chatbot
- ✅ Ultra-human voice assistant
- ✅ Modern SVG icons
- ✅ 6 n8n workflows
- ✅ MongoDB schemas
- ✅ Docker setup
- ✅ Synthetic data generator
- ✅ Testing suite
- ✅ Complete documentation

**Total**: ~13,000 lines of code across 50+ files

---

## 🚀 QUICK START AFTER BUILD

1. Run `docker-compose up -d`
2. Wait for services to start
3. Run `python synthetic-data/generator.py`
4. Run `python synthetic-data/seed_mongodb.py`
5. Open `dashboard/index.html` in Chrome
6. Experience the ultra-human voice!

---

**Government of Andhra Pradesh**  
**AI Personal Assistant v1.0**  
**Complete Cursor AI Build Prompt** 🏛️🤖🎤✨
