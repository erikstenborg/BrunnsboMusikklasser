"""
Pytest configuration for database isolation
"""
import pytest
import tempfile
import os
from app import app, db
from models import Group

@pytest.fixture(scope="function")
def test_app():
    """Create a test Flask app with isolated database"""
    # Save original configuration
    original_config = {}
    for key in ['SQLALCHEMY_DATABASE_URI', 'TESTING', 'WTF_CSRF_ENABLED', 'SESSION_SECRET']:
        original_config[key] = app.config.get(key)
    
    # Configure test environment
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SESSION_SECRET'] = 'test-secret-key'
    
    with app.app_context():
        # Recreate the database with new configuration
        db.drop_all()
        db.create_all()
        
        # Create test groups
        for group_name in ['admin', 'event_manager', 'parent', 'applications_manager']:
            group = Group(name=group_name, description=f'Test {group_name} group')
            db.session.add(group)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating test groups: {e}")
        
        yield app
    
    # Restore original configuration
    for key, value in original_config.items():
        if value is not None:
            app.config[key] = value

@pytest.fixture
def client(test_app):
    """Create test client"""
    return test_app.test_client()