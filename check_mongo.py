from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.calendar_events

count = collection.count_documents({})
print(f"Total calendar events: {count}")

events = list(collection.find().limit(5))
for e in events:
    print(e)
