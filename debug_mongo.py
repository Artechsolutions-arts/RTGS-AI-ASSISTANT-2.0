from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.calendar_events

print("Full dump of calendar_events:")
for doc in collection.find():
    print(doc)
