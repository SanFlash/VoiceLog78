from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() or request.form
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        if request.is_json:
            return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
        return redirect(url_for('main.dashboard'))
    
    if request.is_json:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    return render_template('login.html', error='Invalid credentials')

@auth_bp.route('/login-app', methods=['POST'])
def login_app():
    data = request.get_json() or request.form
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
