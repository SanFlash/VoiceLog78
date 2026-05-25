import os
import threading
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from database import db
from models.recording import Recording
from models.session import Session
from services.audio_service import convert_to_wav
from services.transcription_service import transcribe_audio
from services.speaker_service import detect_speakers

recording_bp = Blueprint('record', __name__)

def process_recording_async(app, recording_id, wav_path):
    with app.app_context():
        recording = Recording.query.get(recording_id)
        session = Session.query.get(recording.session_id)
        try:
            # Update status to In Progress
            recording.status = 'In Progress'
            session.status = 'In Progress'
            db.session.commit()

            # Transcribe
            segments = transcribe_audio(wav_path)

            # Detect speakers
            transcript_data = detect_speakers(wav_path, segments)
            recording.speaker_count = transcript_data['speaker_count']
            recording.transcript = transcript_data['transcript_json']
            recording.status = 'Completed'
            session.status = 'Completed'
            db.session.commit()
        except Exception as e:
            recording.status = 'Error'
            recording.transcript = f'[Error processing: {str(e)}]'
            db.session.commit()
            print(f"Error processing recording {recording_id}: {e}")

@recording_bp.route('/upload', methods=['POST'])
@login_required
def upload_recording():
    session_id = request.form.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400

    session = Session.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()

    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({'error': 'No audio file'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    recordings_folder = current_app.config['RECORDINGS_FOLDER']

    webm_filename = f"session_{session_id}_{current_user.id}.webm"
    wav_filename = f"session_{session_id}_{current_user.id}.wav"
    webm_path = os.path.join(upload_folder, webm_filename)
    wav_path = os.path.join(recordings_folder, wav_filename)

    audio_file.save(webm_path)

    # Convert to WAV
    success = convert_to_wav(webm_path, wav_path)
    if not success:
        wav_path = webm_path  # fallback

    # Create recording record
    recording = Recording(
        session_id=session.id,
        file_path=wav_path,
        status='Uploaded'
    )
    session.status = 'Uploaded'
    db.session.add(recording)
    db.session.commit()

    # Process async
    app = current_app._get_current_object()
    thread = threading.Thread(target=process_recording_async, args=(app, recording.id, wav_path))
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'recording_id': recording.id})

@recording_bp.route('/status/<int:recording_id>', methods=['GET'])
@login_required
def get_status(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    session = Session.query.get(recording.session_id)
    return jsonify({
        'recording_status': recording.status,
        'session_status': session.status if session else 'Unknown'
    })

@recording_bp.route('/transcript/<int:recording_id>', methods=['GET'])
@login_required
def get_transcript(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    import json
    transcript = []
    if recording.transcript:
        try:
            transcript = json.loads(recording.transcript)
        except:
            transcript = [{'speaker': 'Person 1', 'text': recording.transcript, 'start': 0}]
    return jsonify({
        'recording': recording.to_dict(),
        'transcript': transcript
    })
