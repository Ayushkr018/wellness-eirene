from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests
import os
from auth_middleware import verify_token

app = Flask(__name__)
CORS(app)

# Service URLs
AUTH_SERVICE_URL = 'http://auth-service:5001'
MOOD_SERVICE_URL = 'http://mood-service:5002'

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'API Gateway running', 'version': '1.0.0'}), 200

# Auth endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        response = requests.post(f'{AUTH_SERVICE_URL}/register', 
                               json=request.get_json(),
                               timeout=10)
        return response.json(), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Auth service unavailable'}), 503

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        response = requests.post(f'{AUTH_SERVICE_URL}/login', 
                               json=request.get_json(),
                               timeout=10)
        return response.json(), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Auth service unavailable'}), 503

# Mood endpoints
@app.route('/api/mood/analyze', methods=['POST'])
@verify_token
def analyze_mood():
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.post(f'{MOOD_SERVICE_URL}/analyze-mood',
                               json=request.get_json(),
                               headers=headers,
                               timeout=15)
        return response.json(), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Mood service unavailable'}), 503

@app.route('/api/mood/history', methods=['GET'])
@verify_token
def mood_history():
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f'{MOOD_SERVICE_URL}/mood-history',
                              headers=headers,
                              timeout=10)
        return response.json(), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': 'Mood service unavailable'}), 503

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Welcome to Eirene AI Mental Wellness Platform',
        'version': '1.0.0',
        'phase': '1',
        'endpoints': [
            'POST /api/auth/register',
            'POST /api/auth/login', 
            'POST /api/mood/analyze',
            'GET /api/mood/history'
        ]
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

