from flask import Flask, request, jsonify
from flask_cors import CORS
from scheduler import NotificationScheduler
from email_sender import EmailSender
from shared.db_config import get_db
import jwt
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize services
scheduler = NotificationScheduler()
email_sender = EmailSender()

# Start scheduler on app startup
scheduler.start_scheduler()

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except:
        return None

@app.route('/notification-preferences', methods=['GET', 'POST'])
def notification_preferences():
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        db = get_db()
        
        if request.method == 'GET':
            # Get current preferences
            user = db.users.find_one({'_id': user_data['user_id']})
            preferences = user.get('notification_preferences', {
                'daily_reminders': True,
                'evening_reminders': False,
                'motivational_messages': True,
                'reminder_time': '09:00'
            })
            
            return jsonify({'preferences': preferences}), 200
        
        elif request.method == 'POST':
            # Update preferences
            data = request.get_json()
            preferences = data.get('preferences', {})
            
            db.users.update_one(
                {'_id': user_data['user_id']},
                {'$set': {
                    'notification_preferences': preferences,
                    'updated_at': datetime.utcnow()
                }}
            )
            
            return jsonify({
                'message': 'Notification preferences updated successfully',
                'preferences': preferences
            }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send-test-notification', methods=['POST'])
def send_test_notification():
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get user email
        db = get_db()
        user = db.users.find_one({'_id': user_data['user_id']})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Send test email
        success = email_sender.send_daily_reminder(user['email'], user.get('name', ''))
        
        if success:
            return jsonify({'message': 'Test notification sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send notification'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Notification service running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
