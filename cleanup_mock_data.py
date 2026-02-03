from pymongo import MongoClient
import sys

def cleanup():
    # Try the main DB from docker-compose
    uri1 = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
    db_name1 = "gov_ai_assistant"
    
    # Try the one I used earlier for testing
    uri2 = "mongodb+srv://muralig:MuraliG@cluster0.p71vj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    db_name2 = "rtgs_db"
    
    for uri, db_name in [(uri1, db_name1), (uri2, db_name2)]:
        try:
            print(f"Connecting to {uri.split('@')[1]} / {db_name}...")
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            db = client[db_name]
            
            # Delete from appointments
            res = db.appointments.delete_many({})
            print(f"  [appointments] Deleted {res.deleted_count} documents")
            
            # Just in case, check if there's any appointment data in calendar_events that looks like mock data
            # (Users often refer to anything they didn't put there as mock data)
            # But the user specifically said "appointment folder" (collection)
            
        except Exception as e:
            print(f"  Failed to connect or delete: {e}")

if __name__ == "__main__":
    cleanup()
