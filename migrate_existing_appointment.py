from pymongo import MongoClient
from datetime import datetime

def add_existing_appointment():
    mongo_uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client['gov_ai_assistant']
        
        # Add the existing appointment from Feb 4
        appointment = {
            "appointment_id": "appt_existing_feb4_2026",
            "citizen_telegram_id": "unknown",
            "citizen_name": "Citizen",
            "reason": "Approved via Telegram Intake",
            "start_time": "2026-02-04T14:00:00+05:30",  # 2:00 PM
            "end_time": "2026-02-04T15:00:00+05:30",    # 3:00 PM
            "status": "approved",
            "approved_by": "Collector",
            "approved_at": datetime.utcnow().isoformat(),
            "district": "ntr-district",
            "created_via": "manual_migration",
            "google_calendar_event_id": "existing_event"
        }
        
        result = db['appointments'].insert_one(appointment)
        print(f"Successfully added appointment with ID: {result.inserted_id}")
        
        # Verify
        count = db['appointments'].count_documents({"status": "approved"})
        print(f"Total approved appointments in database: {count}")
        
    except Exception as ex:
        print(f"Error: {ex}")

if __name__ == "__main__":
    add_existing_appointment()
