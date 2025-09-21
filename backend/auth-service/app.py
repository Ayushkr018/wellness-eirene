from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime, timedelta
from models import User
from shared.db_config import init_db

app = Flask(__name__)
CORS(app)

# Initialize database on startup
init_db()

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user already exists
        if User.find_by_email(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(email, password)
        user_id = user.save()
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, os.getenv('JWT_SECRET'), algorithm='HS256')
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user._id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, os.getenv('JWT_SECRET'), algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user_id': user._id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'Auth service running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
