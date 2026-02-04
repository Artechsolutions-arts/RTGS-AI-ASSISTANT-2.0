from pymongo import MongoClient
import json
import re

def migrate_malformed():
    uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
    client = MongoClient(uri)
    db = client.gov_ai_assistant
    
    print("Searching for malformed appointment documents...")
    malformed = list(db.appointments.find({}))
    
    fixed_count = 0
    for doc in malformed:
        # Check if the document has a key that looks like a JSON fragment
        is_malformed = any('{' in key or '"' in key for key in doc.keys() if key != '_id')
        
        if is_malformed:
            print(f"Fixing document {doc['_id']}...")
            # Reconstruct the JSON string from keys
            # The keys are: '{"appointment_id":"..."', '"citizen_name":"..."', etc.
            # But wait, n8n might have put the whole thing in one key if it was just one string.
            
            # Let's try to extract data from all keys
            new_doc = {"_id": doc['_id']}
            all_text = "".join([k for k in doc.keys() if k != '_id'])
            
            # Use regex to find key-value pairs in the mess
            # Example: "citizen_name":"revanth"
            pairs = re.findall(r'"([^"]+)":"([^"]*)"', all_text)
            for k, v in pairs:
                new_doc[k] = v
            
            if len(new_doc) > 1:
                # Replace the doc
                db.appointments.replace_one({"_id": doc['_id']}, new_doc)
                fixed_count += 1
                print(f"  Fixed: {new_doc.get('citizen_name')} for {new_doc.get('start_time')}")
            else:
                print("  Failed to extract data from keys.")

    print(f"\nMigration complete. Fixed {fixed_count} documents.")

if __name__ == "__main__":
    migrate_malformed()
