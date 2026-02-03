from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.messages

print("Cleaning up junk messages...")

# Define criteria for junk:
# 1. No message text or empty text
# 2. No AI analysis intent (indicates it wasn't a real message or processing failed)
# 3. Calendar requests
# 4. 'general' intent if text is short (optional, let's stick to the obvious first)

result = collection.delete_many({
    "$or": [
        {"message_text": {"$exists": False}},
        {"message_text": None},
        {"message_text": ""},
        {"message_text": {"$regex": "^\\s*$"}},
        {"ai_analysis.intent": "view_calendar"},
        {"ai_analysis": {"$exists": False}} # Messages that didn't get through AI service
    ]
})

print(f"Deleted {result.deleted_count} junk records.")
