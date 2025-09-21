import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
def get_db():
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client.eirene

# Initialize collections with indexes
def init_db():
    db = get_db()
    
    # Users collection
    users = db.users
    users.create_index("email", unique=True)
    
    # Mood entries collection
    mood_entries = db.mood_entries
    mood_entries.create_index([("user_id", 1), ("timestamp", -1)])
    
    print("Database initialized successfully")
