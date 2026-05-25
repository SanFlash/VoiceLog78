import os
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from database import db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database config
    database_url = os.environ.get('DATABASE_URL', None)
    if not database_url:
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
        database_url = f'sqlite:///{db_path.replace(chr(92), "/")}'  # Convert backslashes to forward slashes
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload config
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    app.config['RECORDINGS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'recordings')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RECORDINGS_FOLDER'], exist_ok=True)
    os.makedirs('database', exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    CORS(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.session_routes import session_bp
    from routes.recording_routes import recording_bp
    from routes.main_routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(session_bp, url_prefix='/sessions')
    app.register_blueprint(recording_bp, url_prefix='/record')

    with app.app_context():
        db.create_all()
        _seed_demo_user()

    return app

def _seed_demo_user():
    from models.user import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(email='demo@test.com').first():
        demo = User(
            email='demo@test.com',
            password=generate_password_hash('demo123'),
            name='Demo User'
        )
        db.session.add(demo)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
