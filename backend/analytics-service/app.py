from flask import Flask, request, jsonify
from flask_cors import CORS
from metrics_collector import MetricsCollector
import jwt
import os

app = Flask(__name__)
CORS(app)

metrics = MetricsCollector()

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except:
        return None

@app.route('/log-action', methods=['POST'])
def log_action():
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get action data
        data = request.get_json()
        action_type = data.get('action_type')
        metadata = data.get('metadata', {})
        
        if not action_type:
            return jsonify({'error': 'action_type is required'}), 400
        
        # Log the action
        metrics.log_user_action(user_data['user_id'], action_type, metadata)
        
        return jsonify({'message': 'Action logged successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user-metrics', methods=['GET'])
def get_user_metrics():
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get user metrics
        user_metrics = metrics.get_user_engagement_metrics(user_data['user_id'], days)
        
        if user_metrics is None:
            return jsonify({'error': 'Failed to retrieve metrics'}), 500
        
        return jsonify({'metrics': user_metrics}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/platform-analytics', methods=['GET'])
def get_platform_analytics():
    try:
        # This endpoint might be restricted to admin users in production
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get query parameters
        days = int(request.args.get('days', 30))
        
        # Get platform analytics
        analytics = metrics.get_platform_analytics(days)
        
        if analytics is None:
            return jsonify({'error': 'Failed to retrieve analytics'}), 500
        
        return jsonify({'analytics': analytics}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Analytics service running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
