"""
MongoDB Atlas Initialization Script (Python)
Alternative to mongosh for initializing the database
"""

from pymongo import MongoClient
from datetime import datetime
import sys

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
DATABASE_NAME = "gov_ai_assistant"

print("=" * 50)
print("MongoDB Atlas Initialization")
print("=" * 50)
print(f"Database: {DATABASE_NAME}")
print(f"Cluster: rtgsai.pjyqjep.mongodb.net")
print()

try:
    # Connect to MongoDB Atlas
    print("[1/5] Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    
    # Test connection
    client.admin.command('ping')
    print("✓ Connected successfully")
    print()
    
    # Select database
    db = client[DATABASE_NAME]
    
    # Create collections
    print("[2/5] Creating collections...")
    collections = ["messages", "tasks", "calendar_events", "audit_logs", "weekly_reports"]
    
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"  ✓ Created: {collection}")
        else:
            print(f"  - Already exists: {collection}")
    
    print()
    
    # Create indexes
    print("[3/5] Creating indexes...")
    
    # Messages indexes
    db.messages.create_index([("message_id", 1)], unique=True)
    db.messages.create_index([("status", 1)])
    db.messages.create_index([("created_at", -1)])
    db.messages.create_index([("sender_info.department", 1)])
    
    # Tasks indexes
    db.tasks.create_index([("task_id", 1)], unique=True)
    db.tasks.create_index([("status", 1)])
    db.tasks.create_index([("priority", 1)])
    db.tasks.create_index([("deadline", 1)])
    
    # Calendar events indexes
    db.calendar_events.create_index([("event_id", 1)], unique=True)
    db.calendar_events.create_index([("start_time", 1)])
    
    # Audit logs indexes
    db.audit_logs.create_index([("timestamp", -1)])
    
    # Weekly reports indexes
    db.weekly_reports.create_index([("week_start", -1)])
    
    print("✓ Indexes created")
    print()
    
    # Insert sample data
    print("[4/5] Inserting sample data...")
    
    sample_message = {
        "message_id": "sample-001",
        "message_text": "Sample message for testing MongoDB Atlas connection",
        "timestamp": datetime.utcnow(),
        "forwarded_from": "+919876543210",
        "sender_role": "System Test",
        "sender_info": {
            "name": "System",
            "role": "Test",
            "department": "testing",
            "phone": "+919876543210"
        },
        "attachments": [],
        "ai_analysis": {
            "language": "english",
            "intent": "test",
            "priority": "low",
            "confidence": 0.95,
            "entities": {}
        },
        "routing": {
            "department": "testing",
            "whatsapp_group": "test_group",
            "sent_to_group": False,
            "sent_to_collector": False
        },
        "status": "new",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if sample already exists
    if db.messages.count_documents({"message_id": "sample-001"}) == 0:
        db.messages.insert_one(sample_message)
        print("✓ Sample data inserted")
    else:
        print("- Sample data already exists")
    
    print()
    
    # Verify setup
    print("[5/5] Verifying setup...")
    print("\nCollections:")
    for collection in db.list_collection_names():
        count = db[collection].count_documents({})
        print(f"  - {collection}: {count} documents")
    
    print()
    print("=" * 50)
    print("✓ MongoDB Atlas Setup Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Start n8n: docker-compose up -d")
    print("2. Update n8n MongoDB credentials with Atlas connection string")
    print("3. Import and activate workflows")
    print("4. Run test_department_routing.bat")
    print()
    
    client.close()
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print()
    print("Possible issues:")
    print("- Network connectivity")
    print("- IP not whitelisted in MongoDB Atlas")
    print("- Invalid credentials")
    print()
    print("Please check MongoDB Atlas dashboard:")
    print("1. Go to https://cloud.mongodb.com")
    print("2. Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)")
    print("3. Database Access → Verify user credentials")
    print()
    sys.exit(1)
