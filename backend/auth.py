"""
Authentication module for the Financial Goal Planner
Handles JWT token generation, validation, and password hashing
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import User, db

# JWT Configuration
JWT_SECRET_KEY = 'your-secret-key-change-in-production'  # Change this in production!
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id):
    """Generate a JWT token for a user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token):
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require authentication for API routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = verify_token(token)
            if payload is None:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
                
        except Exception as e:
            return jsonify({'error': 'Token verification failed'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def register_user(email, password, name, income=None, goal=None, risk_profile=None):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'error': 'User with this email already exists'}, 400
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create new user
        new_user = User(
            email=email,
            password=hashed_password,
            name=name,
            income=income,
            goal=goal,
            risk_profile=risk_profile
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user.id)
        
        return {
            'message': 'User registered successfully',
            'user_id': new_user.id,
            'token': token,
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'income': new_user.income,
                'goal': new_user.goal,
                'risk_profile': new_user.risk_profile
            }
        }, 201
        
    except Exception as e:
        db.session.rollback()
        return {'error': f'Registration failed: {str(e)}'}, 500

def login_user(email, password):
    """Authenticate a user and return token"""
    try:
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Invalid email or password'}, 401
        
        # Verify password
        if not verify_password(password, user.password):
            return {'error': 'Invalid email or password'}, 401
        
        # Generate token
        token = generate_token(user.id)
        
        return {
            'message': 'Login successful',
            'user_id': user.id,
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'income': user.income,
                'goal': user.goal,
                'risk_profile': user.risk_profile
            }
        }, 200
        
    except Exception as e:
        return {'error': f'Login failed: {str(e)}'}, 500

def get_current_user(token):
    """Get current user from token"""
    try:
        payload = verify_token(token)
        if not payload:
            return None
        
        user = User.query.get(payload['user_id'])
        return user
    except Exception:
        return None


