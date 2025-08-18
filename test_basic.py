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


# Test client is now provided by conftest.py


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