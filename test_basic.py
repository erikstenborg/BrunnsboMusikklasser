"""
Basic test suite for Brunnsbo Musikklasser Flask application
Tests core functionality to prevent crashes
"""
import pytest
import tempfile
import os
import uuid
from datetime import datetime, timedelta
from app import app, db
from models import User, Event, Group


@pytest.fixture
def client():
    """Create test client with isolated in-memory database"""
    # Use in-memory SQLite database for faster tests
    original_db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    
    # Configure test environment
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SESSION_SECRET'] = 'test-secret-key'
    
    # Force SQLAlchemy to use the new configuration
    with app.app_context():
        # Recreate the database engine with the new URI
        db.engine.dispose()  # Close existing connections
        
        with app.test_client() as client:
            # Drop all tables and recreate to ensure clean state
            db.drop_all()
            db.create_all()
            
            # Create test groups
            for group_name in ['admin', 'event_manager', 'parent', 'applications_manager']:
                group = Group(name=group_name)
                db.session.add(group)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error creating groups: {e}")
            
            yield client
    
    # Restore original database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = original_db_uri


class TestBasicFunctionality:
    """Test basic functionality"""
    
    def test_app_creation(self, client):
        """Test Flask app is created"""
        assert app is not None
    
    def test_database_setup(self, client):
        """Test database is set up correctly"""
        with app.app_context():
            # Test groups are created
            groups = Group.query.all()
            assert len(groups) == 4
            group_names = [g.name for g in groups]
            assert 'admin' in group_names
            assert 'event_manager' in group_names
    
    def test_user_creation(self, client):
        """Test user model creation"""
        with app.app_context():
            unique_id = str(uuid.uuid4())[:8]
            user = User(
                first_name='John',
                last_name='Doe',
                email=f'john_{unique_id}@example.com',
                active=True
            )
            user.set_password('testpassword123')
            db.session.add(user)
            db.session.commit()
            
            # Test user was created
            assert user.id is not None
            assert user.check_password('testpassword123')
            assert not user.check_password('wrongpassword')
    
    def test_event_creation(self, client):
        """Test event model creation"""
        with app.app_context():
            event = Event(
                title='Test Event',
                description='Test event description',
                event_date=datetime.now() + timedelta(days=30),
                location='Test Location',
                is_active=True
            )
            db.session.add(event)
            db.session.commit()
            
            # Test event was created
            assert event.id is not None
            assert event.title == 'Test Event'
    
    def test_public_routes(self, client):
        """Test public routes don't crash"""
        # Use actual Swedish route names from the app
        public_routes = ['/', '/evenemang', '/kontakt', '/donations', '/ansokan', '/login']
        
        for route in public_routes:
            response = client.get(route)
            # Should return 200 (OK) or 302 (redirect for login)  
            assert response.status_code in [200, 302], f"Route {route} returned {response.status_code}"
    
    def test_admin_routes_redirect(self, client):
        """Test admin routes redirect to login when not authenticated"""
        admin_routes = ['/admin/events', '/admin/users', '/admin/payments']
        
        for route in admin_routes:
            response = client.get(route)
            # Should redirect to login or return 302/403
            assert response.status_code in [302, 403]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])