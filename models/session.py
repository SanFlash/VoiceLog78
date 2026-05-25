from database import db
from datetime import datetime

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(200), nullable=False)
    interviewer = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Created')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recordings = db.relationship('Recording', backref='session', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'session_name': self.session_name,
            'interviewer': self.interviewer,
            'time': self.time,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
        }
