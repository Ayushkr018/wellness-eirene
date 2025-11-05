import os
from pymongo import MongoClient
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    """Get MongoDB database connection"""
    try:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/eirene'))
        return client.eirene
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def init_db():
    """Initialize database collections with indexes"""
    try:
        db = get_db()
        
        # Users collection
        users = db.users
        users.create_index("email", unique=True)
        logger.info("Users collection initialized")
        
        # Mood entries collection
        mood_entries = db.mood_entries
        mood_entries.create_index([("user_id", 1), ("timestamp", -1)])
        logger.info("Mood entries collection initialized")
        
        # User actions collection (for analytics)
        user_actions = db.user_actions
        user_actions.create_index([("user_id", 1), ("timestamp", -1)])
        user_actions.create_index("action_type")
        logger.info("User actions collection initialized")
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False
