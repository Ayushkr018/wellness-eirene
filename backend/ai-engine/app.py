from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
import logging
from predictor import WellnessPredictor
from personalized_counselor import PersonalizedCounselor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

predictor = WellnessPredictor()
counselor = PersonalizedCounselor()

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

@app.route('/predict-wellness', methods=['POST'])
def predict_wellness():
    """Predict wellness trends for user"""
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Train and predict
        prediction = predictor.train_and_predict(user_data['user_id'])
        
        if not prediction.get('success'):
            return jsonify(prediction), 400
        
        # Generate proactive suggestions
        suggestions = predictor.get_proactive_suggestions(prediction)
        prediction['suggestions'] = suggestions
        
        logger.info(f"Wellness prediction generated for user: {user_data['user_id']}")
        
        return jsonify(prediction), 200
        
    except Exception as e:
        logger.error(f"Wellness prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.route('/personalized-response', methods=['POST'])
def personalized_response():
    """Generate personalized AI response"""
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
        mood_text = data.get('mood_text', '')
        sentiment_data = data.get('sentiment_data', {})
        cultural_context = data.get('cultural_context')
        voice_emotion = data.get('voice_emotion')
        
        # Get user context
        user_context = counselor.get_user_context(user_data['user_id'])
        
        # Generate personalized response
        result = counselor.generate_personalized_response(
            mood_text,
            sentiment_data,
            cultural_context,
            user_context,
            voice_emotion
        )
        
        logger.info(f"Personalized response generated for user: {user_data['user_id']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Personalized response error: {str(e)}")
        return jsonify({'error': 'Response generation failed'}), 500

@app.route('/user-context', methods=['GET'])
def get_user_context():
    """Get user context/memory"""
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization token required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get context
        context = counselor.get_user_context(user_data['user_id'])
        
        return jsonify({'success': True, 'context': context}), 200
        
    except Exception as e:
        logger.error(f"Context retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve context'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'ai-engine',
        'version': os.getenv('APP_VERSION', '3.0.0'),
        'features': ['wellness_prediction', 'personalized_counselor', 'user_memory']
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
