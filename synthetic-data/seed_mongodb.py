"""
Seed MongoDB with synthetic data
"""

import json
import sys
from pymongo import MongoClient
from datetime import datetime


def seed_mongodb():
    """Seed MongoDB with synthetic messages"""
    
    print("🔄 Connecting to MongoDB...")
    
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['gov_ai_assistant']
        
        print("✅ Connected to MongoDB")
        
        # Load synthetic messages
        print("📂 Loading synthetic messages...")
        with open('messages.json', 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        print(f"📊 Loaded {len(messages)} messages")
        
        # Transform messages for MongoDB
        print("🔄 Transforming messages...")
        mongo_messages = []
        for msg in messages:
            mongo_msg = {
                'message_id': msg['message_id'],
                'message_text': msg['message_text'],
                'timestamp': datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')),
                'forwarded_from': msg['forwarded_from'],
                'sender_role': msg['sender_role'],
                'attachments': msg.get('attachments', []),
                'status': 'new',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            mongo_messages.append(mongo_msg)
        
        # Insert messages
        print("💾 Inserting messages into MongoDB...")
        result = db.messages.insert_many(mongo_messages)
        print(f"✅ Inserted {len(result.inserted_ids)} messages")
        
        # Create indexes if not exists
        print("🔍 Creating indexes...")
        db.messages.create_index('message_id', unique=True)
        db.messages.create_index('timestamp')
        db.messages.create_index('status')
        print("✅ Indexes created")
        
        # Print statistics
        print("\n📊 Database Statistics:")
        print(f"Total messages: {db.messages.count_documents({})}")
        print(f"New messages: {db.messages.count_documents({'status': 'new'})}")
        
        # Print sample messages by category
        print("\n📋 Sample Messages by Category:")
        categories = ['disaster_alert', 'meeting', 'instruction', 'status_update', 'fyi']
        for category in categories:
            # Find messages with category keyword in text
            count = 0
            for msg in messages:
                if msg.get('category') == category:
                    count += 1
            print(f"  {category}: {count} messages")
        
        print("\n✅ MongoDB seeding complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    seed_mongodb()
