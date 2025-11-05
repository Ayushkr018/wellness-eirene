from flask import Flask, request, jsonify
from flask_cors import CORS
from therapy_generator import TherapyGenerator
import jwt
import os

app = Flask(__name__)
CORS(app)

therapy_gen = TherapyGenerator()

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except:
        return None

@app.route('/generate-art-prompt', methods=['POST'])
def generate_art_prompt():
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get request data
        data = request.get_json()
        mood_data = data.get('mood_data', {})
        cultural_context = data.get('cultural_context')
        
        # Generate art prompt
        art_prompt = therapy_gen.generate_art_prompt(mood_data, cultural_context)
        
        return jsonify({
            'success': True,
            'art_prompt': art_prompt
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-music-suggestion', methods=['POST'])
def generate_music_suggestion():
    try:
        # Verify auth
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        user_data = verify_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get request data
        data = request.get_json()
        mood_data = data.get('mood_data', {})
        cultural_context = data.get('cultural_context')
        
        # Generate music suggestion
        music_suggestion = therapy_gen.generate_music_suggestion(mood_data, cultural_context)
        
        return jsonify({
            'success': True,
            'music_suggestion': music_suggestion
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Creative therapy service running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
