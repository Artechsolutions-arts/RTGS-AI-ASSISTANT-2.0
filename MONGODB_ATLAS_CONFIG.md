# MongoDB Atlas Configuration

## Connection Details

**Connection String:**
```
mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/
```

**Database Name:** `gov_ai_assistant`

**Username:** `artechnical707_db_user`

**Password:** `NiGA7hwIIUjgXWiD`

**Cluster:** `rtgsai.pjyqjep.mongodb.net`

---

## Configuration Updates

### 1. n8n Workflow Credentials

For all MongoDB nodes in n8n workflows, use:

**Connection Type:** Connection String

**Connection String:**
```
mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant
```

### 2. Python Scripts

For any Python scripts using MongoDB (e.g., `seed_mongodb.py`):

```python
from pymongo import MongoClient

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
DATABASE_NAME = "gov_ai_assistant"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
```

### 3. Environment Variables

Create `.env` file:

```env
MONGODB_URI=mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/
MONGODB_DATABASE=gov_ai_assistant
```

---

## Benefits of MongoDB Atlas

✅ **Cloud-hosted** - No need for local MongoDB container  
✅ **Automatic backups** - Data is backed up automatically  
✅ **Scalable** - Easy to scale as data grows  
✅ **Accessible anywhere** - Access from any machine  
✅ **Free tier available** - Good for development/testing  

---

## Docker Compose Changes

Since we're using MongoDB Atlas, you can **remove the local MongoDB container** from docker-compose.yml:

**Before:** 4 containers (MongoDB, PostgreSQL, n8n, Mongo Express)  
**After:** 2 containers (PostgreSQL, n8n)

The MongoDB and Mongo Express containers are no longer needed.

---

## Setup Steps

### 1. Update n8n MongoDB Credentials

1. Open n8n: http://localhost:5678
2. Go to **Credentials** → **MongoDB**
3. Edit existing or create new:
   - **Name:** MongoDB Atlas - Gov AI Assistant
   - **Connection Type:** Connection String
   - **Connection String:** `mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant`
4. **Test** the connection
5. **Save**

### 2. Update All Workflows

Update MongoDB credentials in these workflows:
- 01-whatsapp-intake.json
- 03-rule-routing.json
- 04-task-creation.json
- 05-calendar-management.json
- 06-weekly-digest.json
- 07-whatsapp-group-router.json

### 3. Initialize Database

Run the initialization script to create collections:

```bash
# Using mongosh (MongoDB Shell)
mongosh "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant"

# Then run the init commands
use gov_ai_assistant

# Create collections
db.createCollection("messages")
db.createCollection("tasks")
db.createCollection("calendar_events")
db.createCollection("audit_logs")
db.createCollection("weekly_reports")

# Create indexes
db.messages.createIndex({ "message_id": 1 }, { unique: true })
db.tasks.createIndex({ "task_id": 1 }, { unique: true })
db.calendar_events.createIndex({ "event_id": 1 }, { unique: true })
```

### 4. Test Connection

```bash
# Test with Python
python -c "from pymongo import MongoClient; client = MongoClient('mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/'); print('Connected:', client.server_info()['version'])"
```

---

## Security Notes

> [!WARNING]
> **Credentials Exposed**
> 
> The MongoDB credentials are now in configuration files. For production:
> - Use environment variables instead of hardcoded credentials
> - Rotate passwords regularly
> - Use IP whitelisting in MongoDB Atlas
> - Enable 2FA for MongoDB Atlas account

---

## Troubleshooting

**Issue:** Connection timeout
- **Fix:** Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for testing)

**Issue:** Authentication failed
- **Fix:** Verify username and password are correct

**Issue:** Database not found
- **Fix:** Ensure database name is `gov_ai_assistant`

**Issue:** n8n can't connect
- **Fix:** Ensure connection string includes database name at the end
