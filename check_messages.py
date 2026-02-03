from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.messages

count = collection.count_documents({})
print(f"Total messages: {count}")

recent = list(collection.find().sort("timestamp", -1).limit(5))
for r in recent:
    print(f"{r.get('timestamp')} - {r.get('message_text')}")
