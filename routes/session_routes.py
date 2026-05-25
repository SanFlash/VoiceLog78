from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.session import Session

session_bp = Blueprint('sessions', __name__)

@session_bp.route('/', methods=['GET'])
@login_required
def get_sessions():
    sessions = Session.query.filter_by(user_id=current_user.id)\
        .order_by(Session.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions])

@session_bp.route('/create', methods=['POST'])
@login_required
def create_session():
    data = request.get_json() or request.form
    session = Session(
        session_name=data.get('session_name'),
        interviewer=data.get('interviewer'),
        time=data.get('time'),
        notes=data.get('notes', ''),
        status='Created',
        user_id=current_user.id
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'success': True, 'session': session.to_dict()}), 201

@session_bp.route('/<int:session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    session = Session.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    return jsonify(session.to_dict())

@session_bp.route('/<int:session_id>/status', methods=['PATCH'])
@login_required
def update_status(session_id):
    session = Session.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    session.status = data.get('status', session.status)
    db.session.commit()
    return jsonify(session.to_dict())
