from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.messages

print("Unique intents in the database:")
intents = collection.distinct("ai_analysis.intent")
print(intents)

print("\nRecent non-general messages:")
msgs = list(collection.find({"ai_analysis.intent": {"$nin": ["general", "view_calendar", None]}}).limit(5))
for m in msgs:
    print(f"Intent: {m.get('ai_analysis', {}).get('intent')} | Text: {m.get('message_text')}")
