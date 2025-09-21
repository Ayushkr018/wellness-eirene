from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bson import ObjectId
import jwt
import os
from sentiment_analyzer import SentimentAnalyzer
from ai_counselor import AICounselor
from shared.db_config import get_db

app = Flask(__name__)
CORS(app)

analyzer = SentimentAnalyzer()
counselor = AICounselor()

def verify_token(token):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except:
        return None

@app.route('/analyze-mood', methods=['POST'])
def analyze_mood():
    try:
        # Get auth token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get mood text
        data = request.get_json()
        mood_text = data.get('mood_text', '').strip()
        
        if not mood_text:
            return jsonify({'error': 'Mood text is required'}), 400
        
        # Analyze sentiment
        sentiment_analysis = analyzer.analyze_text(mood_text)
        
        # Generate AI response
        ai_response = counselor.generate_response(mood_text, sentiment_analysis)
        
        # Save to database
        db = get_db()
        mood_entry = {
            'user_id': user_data['user_id'],
            'mood_text': mood_text,
            'sentiment_analysis': sentiment_analysis,
            'ai_response': ai_response,
            'timestamp': datetime.utcnow()
        }
        
        result = db.mood_entries.insert_one(mood_entry)
        
        return jsonify({
            'entry_id': str(result.inserted_id),
            'sentiment_analysis': sentiment_analysis,
            'ai_response': ai_response,
            'timestamp': mood_entry['timestamp'].isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mood-history', methods=['GET'])
def get_mood_history():
    try:
        # Get auth token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get user's mood history
        db = get_db()
        entries = list(db.mood_entries.find(
            {'user_id': user_data['user_id']}
        ).sort('timestamp', -1).limit(20))
        
        # Convert ObjectId to string
        for entry in entries:
            entry['_id'] = str(entry['_id'])
            entry['timestamp'] = entry['timestamp'].isoformat()
        
        return jsonify({'mood_history': entries}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Mood service running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
