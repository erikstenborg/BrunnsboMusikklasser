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
    
    # Create completely fresh Base class for each test to avoid metadata conflicts
    from sqlalchemy.orm import DeclarativeBase
    
    class TestBase(DeclarativeBase):
        pass

    # Initialize extensions for test app
    db = SQLAlchemy(app, model_class=TestBase)
    mail = Mail(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    
    with app.app_context():
        # Create models directly to avoid circular import
        from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
        from sqlalchemy.orm import relationship
        from datetime import datetime
        from werkzeug.security import generate_password_hash, check_password_hash
        from flask_login import UserMixin
        
        # User-Group association table
        user_groups = Table('user_groups', db.metadata,
            Column('user_id', Integer, ForeignKey('users.id')),
            Column('group_id', Integer, ForeignKey('groups.id'))
        )
        
        # Define models directly in test context
        class User(UserMixin, db.Model):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True)
            first_name = Column(String(50), nullable=False)
            last_name = Column(String(50), nullable=False)
            email = Column(String(120), unique=True, nullable=False)
            password_hash = Column(String(256))
            active = Column(Boolean, default=True)
            created_at = Column(DateTime, default=datetime.utcnow)
            last_login = Column(DateTime)
            groups = relationship('Group', secondary=user_groups, back_populates='users')
            
            def set_password(self, password):
                self.password_hash = generate_password_hash(password)
            
            def check_password(self, password):
                return check_password_hash(self.password_hash, password)
                
            def has_role(self, role_name):
                return any(group.name == role_name for group in self.groups)
            
            @property
            def full_name(self):
                return f"{self.first_name} {self.last_name}"
        
        class Group(db.Model):
            __tablename__ = 'groups'
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique=True, nullable=False)
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.utcnow)
            users = relationship('User', secondary=user_groups, back_populates='groups')
        
        class Event(db.Model):
            __tablename__ = 'events'
            id = Column(Integer, primary_key=True)
            title = Column(String(100), nullable=False)
            description = Column(Text)
            event_date = Column(DateTime, nullable=False)
            location = Column(String(200))
            is_active = Column(Boolean, default=True)
            created_at = Column(DateTime, default=datetime.utcnow)
        
        class Application(db.Model):
            __tablename__ = 'applications'
            id = Column(Integer, primary_key=True)
            student_name = Column(String(100), nullable=False)
            parent_email = Column(String(120), nullable=False)
            status = Column(String(20), default='pending')
            created_at = Column(DateTime, default=datetime.utcnow)

        class EventTask(db.Model):
            __tablename__ = 'event_tasks'
            id = Column(Integer, primary_key=True)
            event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
            title = Column(String(200), nullable=False)
            description = Column(Text)
            due_offset_days = Column(Integer, default=0)
            due_offset_hours = Column(Integer, default=0)
            assigned_to_user_id = Column(Integer, ForeignKey('users.id'))
            completed_at = Column(DateTime)
            completed_by_user_id = Column(Integer, ForeignKey('users.id'))
            created_at = Column(DateTime, default=datetime.utcnow)
            
            # Relationships
            event = relationship('Event', backref='tasks')
            assigned_to = relationship('User', foreign_keys=[assigned_to_user_id])
            completed_by = relationship('User', foreign_keys=[completed_by_user_id])
            
            @property
            def completed(self):
                return self.completed_at is not None
            
        # Make models available to test app
        app.User = User
        app.Group = Group
        app.Event = Event
        app.Application = Application
        app.EventTask = EventTask
        
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
        
        # Create test groups
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