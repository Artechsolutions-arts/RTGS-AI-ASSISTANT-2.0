from pymongo import MongoClient

def inspect_all():
    uri = "mongodb+srv://artechnical707_db_user:NiGA7hwIIUjgXWiD@rtgsai.pjyqjep.mongodb.net/"
    client = MongoClient(uri)
    
    print("Listing all databases and collections:")
    for db_name in client.list_database_names():
        db = client[db_name]
        print(f"\nDatabase: {db_name}")
        for coll_name in db.list_collection_names():
            count = db[coll_name].count_documents({})
            print(f"  - {coll_name}: {count} documents")
            if coll_name == 'appointments' and count > 0:
                print("    [!] Found data in appointments!")
                for doc in db[coll_name].find().limit(5):
                    print(f"    - {doc}")

if __name__ == "__main__":
    inspect_all()
