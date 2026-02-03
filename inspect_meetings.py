from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.messages

print("Dumping one 'today meetings' message:")
# Search for messages that might be calendar requests
msg = collection.find_one({"message_text": "today meetings"})
print(msg)
