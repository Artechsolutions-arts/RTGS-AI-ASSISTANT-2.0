from pymongo import MongoClient
import json

def check_db():
    uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
    client = MongoClient(uri)
    db = client.gov_ai_assistant
    
    print("--- APPOINTMENTS (Approved) ---")
    appts = list(db.appointments.find({"status": "approved"}))
    for a in appts:
        print(f"ID: {a.get('_id')} | Name: {a.get('citizen_name')} | Start: {a.get('start_time')} | Reason: {a.get('reason')}")
        
    print("\n--- CALENDAR EVENTS ---")
    events = list(db.calendar_events.find({}))
    for e in events:
        print(f"ID: {e.get('_id')} | Title: {e.get('title')} | Start: {e.get('start_time')} | Reason: {e.get('description')}")

if __name__ == "__main__":
    check_db()
