from pymongo import MongoClient
import json

def check_calendar():
    mongo_uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client['gov_ai_assistant']
        
        # Get all events for Feb 4, 2026
        events = db['calendar_events'].find({
            "start_time": {"$regex": "2026-02-04"}
        })
        
        print("--- Events on Feb 4, 2026 ---")
        count = 0
        for e in events:
            count += 1
            print(f"\nEvent {count}:")
            print(f"  ID: {e.get('event_id')}")
            print(f"  Title: {e.get('title')}")
            print(f"  Description: '{e.get('description')}'")
            print(f"  Start: {e.get('start_time')}")
            print(f"  Has 'Approved via Telegram': {('Approved via Telegram Intake' in str(e.get('description', '')))}")
            
        print(f"\nTotal events on Feb 4: {count}")
        
        # Also check if there are ANY events with the description
        approved = db['calendar_events'].find({
            "description": {"$regex": "Approved via Telegram", "$options": "i"}
        })
        
        approved_count = 0
        print("\n--- All Approved Appointments ---")
        for e in approved:
            approved_count += 1
            print(f"  - {e.get('title')} on {e.get('start_time')}")
            
        print(f"\nTotal approved appointments: {approved_count}")
        
    except Exception as ex:
        print(f"Error connecting to MongoDB: {ex}")

if __name__ == "__main__":
    check_calendar()
