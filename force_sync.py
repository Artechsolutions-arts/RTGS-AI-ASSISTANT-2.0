import os
import json
import datetime
from pymongo import MongoClient

# MongoDB Config
MONGO_URI = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.gov_ai_assistant
collection = db.calendar_events

# Today's date
today = datetime.datetime.now().strftime("%Y-%m-%d")
print(f"Force-syncing events for today: {today}")

# Clear and re-insert 3 high-quality government meetings for today
collection.delete_many({"district": "ntr-district"})

meetings = [
    {
        "event_id": "strategic-001",
        "title": "NTR District Strategic Review Meeting",
        "start_time": f"{today}T10:00:00Z",
        "end_time": f"{today}T11:30:00Z",
        "location": "VMC Council Hall, Vijayawada",
        "district": "ntr-district",
        "status": "confirmed",
        "updated_at": datetime.datetime.now().isoformat()
    },
    {
        "event_id": "emergency-002",
        "title": "Emergency Response Team - Flood Preparedness",
        "start_time": f"{today}T14:30:00Z",
        "end_time": f"{today}T15:30:00Z",
        "location": "Disaster Control Room",
        "district": "ntr-district",
        "status": "urgent",
        "updated_at": datetime.datetime.now().isoformat()
    },
    {
        "event_id": "public-003",
        "title": "Public Grievance Redressal (Spandana)",
        "start_time": f"{today}T16:00:00Z",
        "end_time": f"{today}T18:00:00Z",
        "location": "Collectorate Hub",
        "district": "ntr-district",
        "status": "confirmed",
        "updated_at": datetime.datetime.now().isoformat()
    }
]

for m in meetings:
    collection.insert_one(m)
    print(f"Inserted: {m['title']}")

print("Sync Complete. 3 meetings are now live for today.")
