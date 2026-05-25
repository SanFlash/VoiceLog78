from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main_bp.route('/app-view')
def app_view():
    return render_template('app_view.html')

@main_bp.route('/session/<int:session_id>')
@login_required
def session_details(session_id):
    return render_template('session_details.html', session_id=session_id)

@main_bp.route('/transcript/<int:recording_id>')
@login_required
def transcript(recording_id):
    return render_template('transcript.html', recording_id=recording_id)
