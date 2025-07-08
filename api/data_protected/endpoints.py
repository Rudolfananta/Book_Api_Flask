from flask import Blueprint, jsonify
from api.auth.endpoints import token_required, admin_required
from api.auth.endpoints import get_connection
from api.database.database import get_connection
protected_data_endpoint = Blueprint('protected_data', __name__)

@protected_data_endpoint.route('/user', methods=['GET'])
@token_required
def user_data(current_user):
    return jsonify({
        'message': f'Hello {current_user["email"]}! This is protected user data.',
        'user': current_user
    }), 200

@protected_data_endpoint.route('/admin', methods=['GET'])
@token_required
@admin_required
def admin_data(current_user):
    return jsonify({
        'message': f'Hello admin {current_user["email"]}! This is protected admin data.',
        'users': list(get_connection.keys())  # In real app, don't expose all users like this
    }), 200