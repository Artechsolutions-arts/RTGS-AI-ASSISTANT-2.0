import pymongo
from datetime import datetime, timedelta
import uuid
import random

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/gov_ai_assistant"
client = pymongo.MongoClient(MONGO_URI)
db = client.gov_ai_assistant

def seed_mock_dashboard_data():
    print("Starting Seeding Mock Data for Vijayawada (NTR District)...")
    
    # 1. Messages
    db.messages.delete_many({"district": "ntr-district"})
    
    messages = []
    departments = ["Health", "Electricity", "Infrastructure", "Disaster Management"]
    intents = ["disaster_alert", "meeting", "instruction", "query"]
    priorities = ["high", "medium", "low"]
    
    scenarios = [
        {"text": "Severe water logging reported at Benz Circle after heavy rains.", "intent": "disaster_alert", "dept": "Disaster Management", "prio": "high"},
        {"text": "Request for urgent medical supplies at Vijayawada General Hospital.", "intent": "instruction", "dept": "Health", "prio": "high"},
        {"text": "Street lights not working in Patamata area for 3 days.", "intent": "complaint", "dept": "Electricity", "prio": "medium"},
        {"text": "Review meeting on road widening project at 4 PM today.", "intent": "meeting", "dept": "Infrastructure", "prio": "medium"},
        {"text": "Maintenance work scheduled for substation-4 tomorrow morning.", "intent": "fyi", "dept": "Electricity", "prio": "low"}
    ]

    for i in range(20):
        scenario = random.choice(scenarios)
        msg = {
            "message_id": str(uuid.uuid4()),
            "message_text": scenario["text"],
            "sender_name": f"Officer {random.randint(100, 999)}",
            "sender_role": "Mandal Revenue Officer",
            "district": "ntr-district",
            "ai_analysis": {
                "intent": scenario["intent"],
                "priority": scenario["prio"]
            },
            "status": "routed",
            "department": scenario["dept"],
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat(),
            "created_at": datetime.now().isoformat()
        }
        messages.append(msg)
    
    db.messages.insert_many(messages)
    print(f"Success: Inserted {len(messages)} mock messages.")

    # 2. Calendar Events
    db.calendar_events.delete_many({"district": "ntr-district"})
    
    events = [
        {
            "event_id": str(uuid.uuid4()),
            "title": "NTR District Collectorate - Weekly Review",
            "start_time": datetime.now().replace(hour=10, minute=0).isoformat(),
            "end_time": datetime.now().replace(hour=11, minute=0).isoformat(),
            "location": "Conference Hall, Vijayawada",
            "district": "ntr-district",
            "status": "scheduled"
        },
        {
            "event_id": str(uuid.uuid4()),
            "title": "Emergency Response Team Briefing",
            "start_time": datetime.now().replace(hour=14, minute=30).isoformat(),
            "end_time": datetime.now().replace(hour=15, minute=30).isoformat(),
            "location": "Situation Room",
            "district": "ntr-district",
            "status": "scheduled"
        }
    ]
    db.calendar_events.insert_many(events)
    print(f"Success: Inserted {len(events)} mock calendar events.")

if __name__ == "__main__":
    seed_mock_dashboard_data()
