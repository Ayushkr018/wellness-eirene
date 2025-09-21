import bcrypt
from datetime import datetime
from shared.db_config import get_db

class User:
    def __init__(self, email, password):
        self.email = email
        self.password = self._hash_password(password)
        self.created_at = datetime.utcnow()
        self.mood_history = []
    
    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)
    
    def save(self):
        db = get_db()
        user_data = {
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at,
            'mood_history': self.mood_history
        }
        result = db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_email(email):
        db = get_db()
        user_data = db.users.find_one({'email': email})
        if user_data:
            user = User.__new__(User)
            user.email = user_data['email']
            user.password = user_data['password']
            user.created_at = user_data['created_at']
            user.mood_history = user_data.get('mood_history', [])
            user._id = str(user_data['_id'])
            return user
        return None
