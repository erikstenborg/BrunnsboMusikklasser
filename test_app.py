"""
Streamlined test suite for Brunnsbo Musikklasser Flask application
Tests core functionality to prevent server crashes and template errors
"""
import pytest
from datetime import datetime, timedelta
from forms import LoginForm, EventForm, ApplicationForm

# Test client is now provided by conftest.py


@pytest.fixture
def test_user(test_app):
    """Create a test user"""
    with test_app.app_context():
        User = test_app.User  # Get User model from test app
        # Generate unique email to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User(first_name='Test',
                    last_name='User',
                    email=f'test_{unique_id}@example.com',
                    active=True)
        user.set_password('testpassword')
        test_app.db.session.add(user)
        test_app.db.session.commit()
        test_app.db.session.refresh(user)  # Refresh to get the ID
        return user


@pytest.fixture
def test_admin(test_app):
    """Create a test admin user"""
    with test_app.app_context():
        User = test_app.User  # Get models from test app
        Group = test_app.Group
        # Generate unique email to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        admin = User(first_name='Admin',
                     last_name='User',
                     email=f'admin_{unique_id}@example.com',
                     active=True)
        admin.set_password('adminpassword')

        # Add admin role
        admin_group = Group.query.filter_by(name='admin').first()
        if admin_group:
            admin.groups.append(admin_group)

        test_app.db.session.add(admin)
        test_app.db.session.commit()
        test_app.db.session.refresh(admin)  # Refresh to get the ID
        return admin


@pytest.fixture
def test_event_manager(client):
    """Create a test event manager user"""
    with test_app.app_context():
        # Using test app models instead of imports User, Group
        # Generate unique email to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        manager = User(first_name='Event',
                       last_name='Manager',
                       email=f'manager_{unique_id}@example.com',
                       active=True)
        manager.set_password('managerpassword')

        # Add event_manager role
        manager_group = Group.query.filter_by(name='event_manager').first()
        if manager_group:
            manager.groups.append(manager_group)

        test_app.db.session.add(manager)
        test_app.db.session.commit()
        test_app.db.session.refresh(manager)  # Refresh to get the ID
        return manager


@pytest.fixture
def test_event(client):
    """Create a test event"""
    with test_app.app_context():
        # Using test app models instead of imports Event
        event = Event(title='Test Event',
                      description='Test event description',
                      event_date=datetime.now() + timedelta(days=30),
                      location='Test Location',
                      is_active=True)
        test_app.db.session.add(event)
        test_app.db.session.commit()
        test_app.db.session.refresh(event)  # Refresh to get the ID
        return event


class TestModels:
    """Test model functionality"""

    def test_user_creation(self, test_app, client):
        """Test user model creation"""
        with test_app.app_context():
            User = test_app.User  # Get User model from test app
            user = User(first_name='John',
                        last_name='Doe',
                        email='john@example.com',
                        active=True)
            user.set_password('password123')
            test_app.db.session.add(user)
            test_app.db.session.commit()

            assert user.id is not None
            assert user.email == 'john@example.com'
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')

    def test_user_roles(self, test_user, test_app, client):
        """Test user role functionality"""
        with test_app.app_context():
            # Using test app models instead of imports User, Group
            user = User.query.get(test_user.id)

            # Test no roles initially
            assert not user.has_role('admin')

            # Add admin role
            admin_group = Group.query.filter_by(name='admin').first()
            if admin_group:
                user.groups.append(admin_group)
            test_app.db.session.commit()

            assert user.has_role('admin')

    def test_event_creation(self, test_app, client):
        """Test event model creation"""
        # Using test app models instead of imports Event
        with test_app.app_context():
            event = Event(title='Concert 2025',
                          description='Annual concert',
                          event_date=datetime(2025, 12, 15, 19, 0),
                          location='Main Hall',
                          is_active=True)
            test_app.db.session.add(event)
            test_app.db.session.commit()

            assert event.id is not None
            assert event.title == 'Concert 2025'
            assert event.is_active is True

    def test_application_creation(self, test_app, client):
        """Test application model creation"""
        # Using test app models instead of imports Application
        with test_app.app_context():
            application = Application(
                student_name='Child Smith',
                student_personnummer='20101201-1234',
                parent_name='Jane Smith',
                parent_email='jane@example.com',
                parent_phone='123456789',
                address='Test Street 123',
                postal_code='12345',
                city='Stockholm',
                grade_applying_for='5',
                musical_experience='Some experience',
                motivation='Love for music and wants to learn more about it',
                application_year='2025/2026',
                status='applied')
            test_app.db.session.add(application)
            test_app.db.session.commit()

            assert application.id is not None
            assert application.parent_email == 'jane@example.com'
            assert application.student_name == 'Child Smith'
            assert application.status == 'applied'

    def test_event_task_creation(self, test_event, client):
        """Test event task model creation"""
        # Using test app models instead of imports Event, EventTask
        with test_app.app_context():
            event = Event.query.get(test_event.id)
            task = EventTask(event_id=event.id,
                             title='Setup stage',
                             description='Setup stage equipment',
                             due_offset_days=7,
                             due_offset_hours=0)
            test_app.db.session.add(task)
            test_app.db.session.commit()

            assert task.id is not None
            assert task.title == 'Setup stage'
            assert task.event_id == event.id


class TestForms:
    """Test form validation"""

    def test_login_form_valid(self, test_app, client):
        """Test valid login form"""
        with test_app.test_request_context():
            form_data = {
                'email': 'test@example.com',
                'password': 'password123'
            }
            form = LoginForm(data=form_data)
            assert form.validate()

    def test_login_form_invalid_email(self, test_app, client):
        """Test login form with invalid email"""
        with test_app.test_request_context():
            form_data = {'email': 'invalid-email', 'password': 'password123'}
            form = LoginForm(data=form_data)
            assert not form.validate()
            assert 'email' in form.errors

    def test_event_form_valid(self, test_app, client):
        """Test valid event form"""
        with test_app.test_request_context():
            form_data = {
                'title': 'New Event',
                'description': 'Event description',
                'event_date': datetime.now() + timedelta(days=30),
                'location': 'Event Location',
                'is_active': True,
                'coordinator_id': 0  # No coordinator
            }
            form = EventForm(data=form_data)
            # Set choices for coordinator field
            form.coordinator_id.choices = [(0, 'Ingen koordinator')] + [
                (u.id, u.full_name) for u in User.query.all()
            ]
            assert form.validate()

    def test_event_form_invalid_title(self, test_app, client):
        """Test event form with invalid title"""
        with test_app.test_request_context():
            form_data = {
                'title': 'A',  # Too short
                'description': 'Event description',
                'event_date': datetime.now() + timedelta(days=30),
                'location': 'Event Location',
                'is_active': True,
                'coordinator_id': 0
            }
            form = EventForm(data=form_data)
            # Set choices for coordinator field
            form.coordinator_id.choices = [(0, 'Ingen koordinator')] + [
                (u.id, u.full_name) for u in User.query.all()
            ]
            assert not form.validate()
            assert 'title' in form.errors

    def test_application_form_valid(self, test_app, client):
        """Test valid application form"""
        with test_app.test_request_context():
            form_data = {
                'student_name': 'John Doe',
                'student_personnummer': '20101201-1234',
                'parent_name': 'Jane Doe',
                'parent_email': 'jane@example.com',
                'parent_phone': '123456789',
                'address': 'Test Street 123',
                'postal_code': '12345',
                'city': 'Stockholm',
                'current_school': 'Test School',
                'grade_applying_for': '5',
                'musical_experience': 'Some experience with piano',
                'motivation':
                'I love music and want to learn more about singing and instruments',
                'has_transportation': True,
                'additional_info': 'Additional information'
            }
            form = ApplicationForm(data=form_data)
            assert form.validate(), f"Form validation failed: {form.errors}"


class TestCriticalRoutes:
    """Test critical routes that prevent server crashes"""

    def test_public_routes_no_crash(self, test_app, client):
        """Test all public routes don't crash"""
        public_routes = [
            '/', '/om-oss', '/evenemang', '/ansokan', '/login', '/register'
        ]

        for route in public_routes:
            response = client.get(route)
            # Should not be 500 (server error)
            assert response.status_code != 500, f"Route {route} returned server error"
            # Should be 200 or redirect
            assert response.status_code in [
                200, 302, 404
            ], f"Route {route} returned unexpected status: {response.status_code}"

    def test_task_route_with_user(self, client, test_user):
        """Test task route doesn't crash with logged in user"""
        # Login as user and add parent role
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True

        with test_app.app_context():
            # Using test app models instead of imports User, Group
            user = User.query.get(test_user.id)
            parent_group = Group.query.filter_by(name='parent').first()
            if parent_group:
                user.groups.append(parent_group)
                test_app.db.session.commit()

        response = client.get('/tasks')
        # Should not crash
        assert response.status_code != 500, "Tasks route crashed with logged in user"


class TestPermissions:
    """Test permission decorators"""

    def test_user_has_role(self, test_admin, client):
        """Test user role checking"""
        with test_app.app_context():
            # Using test app models instead of imports User
            admin = User.query.get(test_admin.id)
            assert admin.has_role('admin')
            assert not admin.has_role('parent')


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_nonexistent_route(self, test_app, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_event_with_coordinator(self, client, test_event,
                                    test_event_manager):
        """Test event with coordinator assigned"""
        with test_app.app_context():
            # Using test app models instead of imports User, Event
            event = Event.query.get(test_event.id)
            manager = User.query.get(test_event_manager.id)
            event.coordinator_id = manager.id
            test_app.db.session.commit()

            # Test that coordinator is properly linked
            assert event.coordinator is not None
            assert event.coordinator.email == 'manager@example.com'

    def test_task_completion(self, client, test_event, test_user):
        """Test task completion functionality"""
        with test_app.app_context():
            # Using test app models instead of imports EventTask
            # Create task
            task = EventTask(event_id=test_event.id,
                             title='Test Task',
                             description='Test task description',
                             assigned_to_user_id=test_user.id)
            test_app.db.session.add(task)
            test_app.db.session.commit()

            # Check task is not completed initially
            assert task.completed_at is None
            assert not task.completed

            # Mark as completed
            task.completed_at = datetime.now()
            task.completed_by_user_id = test_user.id
            test_app.db.session.commit()

            # Check task is completed
            assert task.completed_at is not None
            assert task.completed


class TestDatabaseIntegrity:
    """Test database relationships and constraints"""

    def test_user_event_task_relationship(self, client, test_user, test_event):
        """Test user-event-task relationships"""
        with test_app.app_context():
            # Using test app models instead of imports EventTask
            task = EventTask(event_id=test_event.id,
                             title='Relationship Test',
                             assigned_to_user_id=test_user.id)
            test_app.db.session.add(task)
            test_app.db.session.commit()

            # Test relationships
            assert task.event.title == 'Test Event'
            assert task.assigned_to.email == 'test@example.com'

    def test_cascade_deletion(self, client, test_event):
        """Test cascade deletion of related objects"""
        with test_app.app_context():
            # Using test app models instead of imports Event, EventTask
            # Create task for event
            task = EventTask(
                event_id=test_event.id,
                title='Will be deleted',
                description='This task should be deleted with event')
            test_app.db.session.add(task)
            test_app.db.session.commit()

            task_id = task.id

            # Delete event
            event = Event.query.get(test_event.id)
            test_app.db.session.delete(event)
            test_app.db.session.commit()

            # Check task is also deleted
            deleted_task = EventTask.query.get(task_id)
            assert deleted_task is None


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
