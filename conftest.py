"""
Pytest configuration for complete database isolation
"""
import pytest
import tempfile
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


@pytest.fixture(scope="function")
def test_app():
    """Create completely isolated test Flask app"""
    # Create fresh Flask app instance
    app = Flask(__name__)
    app.secret_key = 'test-secret-key'
    
    # Configure test environment
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    app.config['SESSION_SECRET'] = 'test-secret-key'
    
    # Initialize extensions for test app
    db = SQLAlchemy(app, model_class=Base)
    mail = Mail(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    
    with app.app_context():
        # Import all models within app context to avoid circular imports
        import models  # This imports all models
        from models import Group, User
        
        # Set up user loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Register basic test routes to avoid 404s
        @app.route('/')
        def index():
            return 'Test Home'
        
        @app.route('/evenemang')
        def events():
            return 'Test Events'
            
        @app.route('/kontakt') 
        def contact():
            return 'Test Contact'
            
        @app.route('/donations')
        def donations():
            return 'Test Donations'
            
        @app.route('/ansokan')
        def application():
            return 'Test Application'
            
        @app.route('/login')
        def login():
            return 'Test Login'
        
        # Create all tables
        db.create_all()
        
        # Create test groups in logical order
        test_groups = [
            ('admin', 'Fullständig tillgång till alla administrativa funktioner och användarhantering'),
            ('applications_manager', 'Kan hantera och granska studentansökningar samt godkänna nya elever'),
            ('event_manager', 'Kan skapa, redigera och hantera evenemang samt tilldela uppgifter'),
            ('parent', 'Förälder med tillgång till barnspecifik information och uppgifter')
        ]
        for group_name, description in test_groups:
            group = Group(name=group_name, description=description)
            db.session.add(group)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating test groups: {e}")
        
        # Make db available to tests
        app.db = db
        yield app

@pytest.fixture
def client(test_app):
    """Create test client"""
    return test_app.test_client()