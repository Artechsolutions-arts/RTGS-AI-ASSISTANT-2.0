from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.messages

print("Searching for messages with empty text or 'No Content' style data:")
# Use $or to find various forms of "empty"
empty_msgs = list(collection.find({
    "$or": [
        {"message_text": {"$exists": False}},
        {"message_text": None},
        {"message_text": ""},
        {"message_text": "No Content"}
    ]
}).sort("timestamp", -1).limit(10))

for m in empty_msgs:
    print(f"ID: {m.get('_id')} | Text: {m.get('message_text')} | TS: {m.get('timestamp')} | Full: {m}")
