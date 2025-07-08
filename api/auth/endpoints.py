from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from flask import current_app as app

auth_endpoint = Blueprint('auth', __name__)

# Mock database (in a real app, use a proper database)
users_db = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users_db.get(data['email'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@auth_endpoint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required!'}), 400
        
    if data['email'] in users_db:
        return jsonify({'message': 'User already exists!'}), 400
        
    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    # Default role is 'user', unless specified otherwise
    role = data.get('role', 'user')
    
    # Only allow admin creation if the requester is an admin
    if role == 'admin':
        # Check if there's an Authorization header
        if 'Authorization' not in request.headers:
            return jsonify({'message': 'Admin creation requires admin privileges!'}), 403
            
        # Verify the token
        token = request.headers['Authorization'].split(" ")[1]
        try:
            token_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            requester = users_db.get(token_data['email'])
            if not requester or requester['role'] != 'admin':
                return jsonify({'message': 'Admin creation requires admin privileges!'}), 403
        except:
            return jsonify({'message': 'Invalid token!'}), 401
    
    users_db[data['email']] = {
        'email': data['email'],
        'password': hashed_password,
        'role': role
    }
    
    return jsonify({'message': 'User registered successfully!'}), 201

@auth_endpoint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required!'}), 400
        
    user = users_db.get(data['email'])
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
        
    token = jwt.encode({
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'role': user['role']
    }), 200