from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
import logging
from risk_detector import RiskDetector
from crisis_protocol import CrisisProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

detector = RiskDetector()
protocol = CrisisProtocol()

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

@app.route('/assess-risk', methods=['POST'])
def assess_risk():
    """Assess user risk level"""
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get request data
        data = request.get_json()
        mood_data = data.get('mood_data', {})
        user_history = data.get('user_history')
        
        # Calculate risk
        risk_assessment = detector.calculate_risk_score(mood_data, user_history)
        
        # Trigger crisis protocol if needed
        protocol_result = None
        if risk_assessment['risk_level'] in ['CRISIS', 'HIGH']:
            protocol_result = protocol.trigger_crisis_response(
                user_data['user_id'],
                risk_assessment,
                mood_data,
                token
            )
        
        logger.info(f"Risk assessed for user {user_data['user_id']}: {risk_assessment['risk_level']}")
        
        return jsonify({
            'success': True,
            'risk_assessment': risk_assessment,
            'protocol_triggered': protocol_result is not None,
            'crisis_response': protocol_result
        }), 200
        
    except Exception as e:
        logger.error(f"Risk assessment error: {str(e)}")
        return jsonify({'error': 'Risk assessment failed'}), 500

@app.route('/crisis-resources', methods=['GET'])
def get_crisis_resources():
    """Get emergency resources"""
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get fallback resources (always available)
        resources = protocol._get_fallback_resources()
        
        return jsonify({
            'success': True,
            'resources': resources
        }), 200
        
    except Exception as e:
        logger.error(f"Resource fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch resources'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'crisis-manager',
        'version': os.getenv('APP_VERSION', '4.0.0')
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
