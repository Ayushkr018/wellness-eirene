from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
import logging
from streak_tracker import StreakTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

tracker = StreakTracker()

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

@app.route('/update-streak', methods=['POST'])
def update_streak():
    """Update user streak after check-in"""
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Update streak
        progress = tracker.update_streak(user_data['user_id'])
        
        if not progress:
            return jsonify({'error': 'Failed to update streak'}), 500
        
        # Prepare response
        response = {
            'success': True,
            'current_streak': progress.get('current_streak', 0),
            'points_earned': progress.get('points_earned', 0),
            'total_points': progress.get('points', 0),
            'new_badges': progress.get('new_badges', [])
        }
        
        # Add motivational message
        streak = progress.get('current_streak', 0)
        if streak == 1:
            response['message'] = "Great start! [translate:Aur check-in karte raho]! 🌟"
        elif streak == 7:
            response['message'] = "[translate:Ek hafta ho gaya]! You're building a healthy habit! 🎉"
        elif streak == 30:
            response['message'] = "[translate:Ek mahina]! Incredible dedication! 🚀"
        elif streak % 10 == 0:
            response['message'] = f"{streak} days strong! [translate:Kya baat hai]! 💪"
        else:
            response['message'] = f"Day {streak} - [translate:Achha chal raha hai]! Keep it up! ✨"
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Streak update error: {str(e)}")
        return jsonify({'error': 'Failed to update streak'}), 500

@app.route('/progress', methods=['GET'])
def get_progress():
    """Get user progress and achievements"""
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get progress
        progress = tracker.get_progress(user_data['user_id'])
        
        if not progress:
            return jsonify({'error': 'Failed to fetch progress'}), 500
        
        return jsonify({
            'success': True,
            'progress': progress
        }), 200
        
    except Exception as e:
        logger.error(f"Progress fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch progress'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'gamification-service',
        'version': os.getenv('APP_VERSION', '4.0.0')
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
