from pymongo import MongoClient
import os

uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
client = MongoClient(uri)
db = client.gov_ai_assistant
collection = db.messages

junk_texts = ["today meetings", "tomorrow meetings", "upcoming meetings"]
result = collection.delete_many({"message_text": {"$in": junk_texts}})
print(f"Deleted {result.deleted_count} junk bot command messages from 'messages' collection.")
