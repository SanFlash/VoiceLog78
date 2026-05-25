from database import db
from datetime import datetime

class Recording(db.Model):
    __tablename__ = 'recordings'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)
    transcript = db.Column(db.Text, nullable=True)
    speaker_count = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='Uploaded')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'file_path': self.file_path,
            'transcript': self.transcript,
            'speaker_count': self.speaker_count,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
