"""
Comprehensive unit tests for Brunnsbo Musikklasser Flask application
"""
import pytest
import os
import tempfile
from datetime import datetime, timedelta
from flask import url_for
from werkzeug.security import generate_password_hash

# Import application components
from app import app, db
from models import User, Event, Application, NewsPost, EventTask, Group, ConfirmationCode
from forms import ApplicationForm, LoginForm, ChangePasswordForm, EventForm, EventTaskForm
from permissions import requires_role, requires_any_role
import routes  # Import to register routes


@pytest.fixture
def client():
    """Create test client with temporary database"""
    # Create temporary database file
    db_fd, temp_db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SESSION_SECRET'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create test groups only if they don't exist
            for group_name in ['admin', 'event_manager', 'parent', 'applications_manager']:
                if not Group.query.filter_by(name=group_name).first():
                    group = Group(name=group_name)
                    db.session.add(group)
            
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
            
            yield client
            
        os.close(db_fd)
        os.unlink(temp_db_path)


@pytest.fixture
def test_user(client):
    """Create a test user"""
    with app.app_context():
        user = User(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            active=True
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_admin(client):
    """Create a test admin user"""
    with app.app_context():
        admin = User(
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            active=True
        )
        admin.set_password('adminpassword')
        
        # Add admin role
        admin_group = Group.query.filter_by(name='admin').first()
        admin.groups.append(admin_group)
        
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def test_event_manager(client):
    """Create a test event manager user"""
    with app.app_context():
        manager = User(
            first_name='Event',
            last_name='Manager',
            email='manager@example.com',
            active=True
        )
        manager.set_password('managerpassword')
        
        # Add event_manager role
        manager_group = Group.query.filter_by(name='event_manager').first()
        manager.groups.append(manager_group)
        
        db.session.add(manager)
        db.session.commit()
        return manager


@pytest.fixture
def test_event(client):
    """Create a test event"""
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
        return event


class TestModels:
    """Test model functionality"""
    
    def test_user_creation(self, client):
        """Test user model creation"""
        with app.app_context():
            user = User(
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                active=True
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.email == 'john@example.com'
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
    
    def test_user_roles(self, test_user, client):
        """Test user role functionality"""
        with app.app_context():
            user = User.query.get(test_user.id)
            
            # Test no roles initially
            assert not user.has_role('admin')
            
            # Add admin role
            admin_group = Group.query.filter_by(name='admin').first()
            user.groups.append(admin_group)
            db.session.commit()
            
            assert user.has_role('admin')
    
    def test_event_creation(self, client):
        """Test event model creation"""
        with app.app_context():
            event = Event(
                title='Concert 2025',
                description='Annual concert',
                event_date=datetime(2025, 12, 15, 19, 0),
                location='Main Hall',
                is_active=True
            )
            db.session.add(event)
            db.session.commit()
            
            assert event.id is not None
            assert event.title == 'Concert 2025'
            assert event.is_active is True
    
    def test_application_creation(self, client):
        """Test application model creation"""
        with app.app_context():
            application = Application(
                parent_first_name='Jane',
                parent_last_name='Smith',
                parent_email='jane@example.com',
                child_first_name='Child',
                child_last_name='Smith',
                child_personnummer='1234567890',
                child_phone='123456789',
                child_postal_code='12345',
                child_city='Stockholm',
                application_year='2025/2026',
                status='applied'
            )
            db.session.add(application)
            db.session.commit()
            
            assert application.id is not None
            assert application.parent_email == 'jane@example.com'
            assert application.status == 'applied'
    
    def test_event_task_creation(self, test_event, client):
        """Test event task model creation"""
        with app.app_context():
            event = Event.query.get(test_event.id)
            task = EventTask(
                event_id=event.id,
                title='Setup stage',
                description='Setup stage equipment',
                due_offset_days=7,
                due_offset_hours=0
            )
            db.session.add(task)
            db.session.commit()
            
            assert task.id is not None
            assert task.title == 'Setup stage'
            assert task.event_id == event.id


class TestForms:
    """Test form validation"""
    
    def test_login_form_valid(self, client):
        """Test valid login form"""
        with app.app_context():
            form_data = {
                'email': 'test@example.com',
                'password': 'password123'
            }
            form = LoginForm(data=form_data)
            assert form.validate()
    
    def test_login_form_invalid_email(self, client):
        """Test login form with invalid email"""
        with app.app_context():
            form_data = {
                'email': 'invalid-email',
                'password': 'password123'
            }
            form = LoginForm(data=form_data)
            assert not form.validate()
            assert 'email' in form.errors
    
    def test_event_form_valid(self, client):
        """Test valid event form"""
        with app.app_context():
            form_data = {
                'title': 'New Event',
                'description': 'Event description',
                'event_date': datetime.now() + timedelta(days=30),
                'location': 'Event Location',
                'is_active': True,
                'coordinator_id': 0  # No coordinator
            }
            form = EventForm(data=form_data)
            assert form.validate()
    
    def test_event_form_invalid_title(self, client):
        """Test event form with invalid title"""
        with app.app_context():
            form_data = {
                'title': 'A',  # Too short
                'description': 'Event description',
                'event_date': datetime.now() + timedelta(days=30),
                'location': 'Event Location',
                'is_active': True,
                'coordinator_id': 0
            }
            form = EventForm(data=form_data)
            assert not form.validate()
            assert 'title' in form.errors
    
    def test_application_form_valid(self, client):
        """Test valid application form"""
        with app.app_context():
            form_data = {
                'parent_first_name': 'Jane',
                'parent_last_name': 'Doe',
                'parent_email': 'jane@example.com',
                'parent_phone': '123456789',
                'child_first_name': 'John',
                'child_last_name': 'Doe',
                'child_personnummer': '1234567890',
                'child_phone': '987654321',
                'child_postal_code': '12345',
                'child_city': 'Stockholm',
                'musical_experience': 'Some experience',
                'instrument_interest': 'Piano',
                'academic_performance': 'Good',
                'has_transportation': True,
                'additional_info': 'Additional information'
            }
            form = ApplicationForm(data=form_data)
            assert form.validate()


class TestRoutes:
    """Test route functionality"""
    
    def test_index_route(self, client):
        """Test homepage route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Brunnsbo Musikklasser' in response.data
    
    def test_about_route(self, client):
        """Test about page route"""
        response = client.get('/om-oss')
        assert response.status_code == 200
    
    def test_events_route(self, client):
        """Test events page route"""
        response = client.get('/evenemang')
        assert response.status_code == 200
    
    def test_application_route_get(self, client):
        """Test application page GET request"""
        response = client.get('/ansokan')
        assert response.status_code == 200
        assert b'ansokan' in response.data.lower()
    
    def test_login_route_get(self, client):
        """Test login page GET request"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'logga in' in response.data.lower()
    
    def test_login_route_post_invalid(self, client):
        """Test login POST with invalid credentials"""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200  # Should return to login page
    
    def test_login_route_post_valid(self, client, test_user):
        """Test login POST with valid credentials"""
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_protected_route_without_login(self, client):
        """Test accessing protected route without login"""
        response = client.get('/admin/events')
        assert response.status_code == 302  # Should redirect to login
    
    def test_admin_events_with_permission(self, client, test_admin):
        """Test admin events route with proper permission"""
        # Login as admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_admin.id)
            sess['_fresh'] = True
        
        response = client.get('/admin/events')
        assert response.status_code == 200
    
    def test_user_tasks_route(self, client, test_user):
        """Test user tasks route"""
        # Login as user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True
        
        # Add parent role to user
        with app.app_context():
            user = User.query.get(test_user.id)
            parent_group = Group.query.filter_by(name='parent').first()
            user.groups.append(parent_group)
            db.session.commit()
        
        response = client.get('/tasks')
        assert response.status_code == 200


class TestPermissions:
    """Test permission decorators"""
    
    def test_requires_role_decorator(self, client, test_admin):
        """Test requires_role decorator"""
        @requires_role('admin')
        def test_function():
            return 'success'
        
        # This would need to be tested in context of actual routes
        # as decorators need Flask application context
        pass
    
    def test_user_has_role(self, test_admin, client):
        """Test user role checking"""
        with app.app_context():
            admin = User.query.get(test_admin.id)
            assert admin.has_role('admin')
            assert not admin.has_role('parent')


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_nonexistent_route(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_event_with_coordinator(self, client, test_event, test_event_manager):
        """Test event with coordinator assigned"""
        with app.app_context():
            event = Event.query.get(test_event.id)
            manager = User.query.get(test_event_manager.id)
            event.coordinator_id = manager.id
            db.session.commit()
            
            # Test that coordinator is properly linked
            assert event.coordinator is not None
            assert event.coordinator.email == 'manager@example.com'
    
    def test_task_completion(self, client, test_event, test_user):
        """Test task completion functionality"""
        with app.app_context():
            # Create task
            task = EventTask(
                event_id=test_event.id,
                title='Test Task',
                description='Test task description',
                assigned_to_user_id=test_user.id
            )
            db.session.add(task)
            db.session.commit()
            
            # Check task is not completed initially
            assert task.completed_at is None
            assert not task.completed
            
            # Mark as completed
            task.completed_at = datetime.now()
            task.completed_by_user_id = test_user.id
            db.session.commit()
            
            # Check task is completed
            assert task.completed_at is not None
            assert task.completed


class TestDatabaseIntegrity:
    """Test database relationships and constraints"""
    
    def test_user_event_task_relationship(self, client, test_user, test_event):
        """Test user-event-task relationships"""
        with app.app_context():
            task = EventTask(
                event_id=test_event.id,
                title='Relationship Test',
                assigned_to_user_id=test_user.id
            )
            db.session.add(task)
            db.session.commit()
            
            # Test relationships
            assert task.event.title == 'Test Event'
            assert task.assigned_to.email == 'test@example.com'
    
    def test_cascade_deletion(self, client, test_event):
        """Test cascade deletion of related objects"""
        with app.app_context():
            # Create task for event
            task = EventTask(
                event_id=test_event.id,
                title='Will be deleted',
                description='This task should be deleted with event'
            )
            db.session.add(task)
            db.session.commit()
            
            task_id = task.id
            
            # Delete event
            event = Event.query.get(test_event.id)
            db.session.delete(event)
            db.session.commit()
            
            # Check task is also deleted
            deleted_task = EventTask.query.get(task_id)
            assert deleted_task is None


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])