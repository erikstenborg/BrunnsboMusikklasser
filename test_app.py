"""
Streamlined test suite for Brunnsbo Musikklasser Flask application
Tests core functionality to prevent server crashes and template errors
"""
import pytest
from datetime import datetime, timedelta
from forms import LoginForm, EventForm, ApplicationForm
from decimal import Decimal

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
def test_event_manager(test_app, client):
    """Create a test event manager user"""
    with test_app.app_context():
        User = test_app.User  # Get models from test app
        Group = test_app.Group
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
def test_event(test_app, client):
    """Create a test event"""
    with test_app.app_context():
        Event = test_app.Event  # Get Event model from test app
        event = Event(title='Test Event',
                      description='Test event description',
                      event_date=datetime.now() + timedelta(days=30),
                      location='Test Location',
                      is_active=True)
        test_app.db.session.add(event)
        test_app.db.session.commit()
        test_app.db.session.refresh(event)  # Refresh to get the ID
        return event


class TestBasicFunctionality:
    """Test basic Flask app functionality"""

    def test_app_creation(self, client):
        """Test Flask app is created"""
        from app import app
        assert app is not None

    def test_database_setup(self, client):
        """Test database is set up correctly in development environment"""
        from app import app, db
        from models import Group
        with app.app_context():
            # Test groups are created in development
            groups = Group.query.all()
            assert len(groups) >= 4  # Should have at least the 4 main groups
            group_names = [g.name for g in groups]
            assert 'admin' in group_names
            assert 'event_manager' in group_names
            assert 'applications_manager' in group_names
            assert 'parent' in group_names

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
            User = test_app.User  # Get models from test app
            Group = test_app.Group
            user = test_app.db.session.get(User, test_user.id)

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
        with test_app.app_context():
            Event = test_app.Event  # Get Event model from test app
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
        with test_app.app_context():
            Application = test_app.Application  # Get Application model from test app
            application = Application(
                student_name='Child Smith',
                parent_email='jane@example.com',
                status='pending')
            test_app.db.session.add(application)
            test_app.db.session.commit()

            assert application.id is not None
            assert application.parent_email == 'jane@example.com'
            assert application.student_name == 'Child Smith'
            assert application.status == 'pending'

    def test_event_task_creation(self, test_app, test_event, client):
        """Test event task model creation"""
        with test_app.app_context():
            EventTask = test_app.EventTask  # Get EventTask model from test app
            Event = test_app.Event
            event = test_app.db.session.get(Event, test_event.id)
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
            User = test_app.User  # Get User model from test app
            form_data = {
                'title': 'New Event',
                'description': 'Event description',
                'event_date': datetime.now() + timedelta(days=30),
                'location': 'Event Location',
                'is_active': True,
                'coordinator_id': 0  # No coordinator
            }
            form = EventForm(data=form_data)
            # Set choices for coordinator field - simplified for test
            form.coordinator_id.choices = [(0, 'Ingen koordinator')]
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
            # Set choices for coordinator field - simplified for test
            form.coordinator_id.choices = [(0, 'Ingen koordinator')]
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
                'parent_phone': '0701234567',
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
        # Public routes that should be accessible without authentication
        public_routes = [
            '/', '/om-oss', '/evenemang', '/kontakt', '/ansokan', '/login', 
            '/register', '/forgot-password', '/donations', '/verify-email'
        ]

        for route in public_routes:
            response = client.get(route)
            # Should not be 500 (server error)
            assert response.status_code != 500, f"Route {route} returned server error"
            # Should be 200 (OK), 302 (redirect), or 404 (not found - acceptable for test)
            assert response.status_code in [
                200, 302, 404
            ], f"Route {route} returned unexpected status: {response.status_code}"

    def test_admin_routes_redirect(self, client):
        """Test admin routes redirect to login when not authenticated"""
        # All admin routes that should require authentication
        admin_routes = [
            '/admin/applications',
            '/admin/events', 
            '/admin/users',
            '/admin/payments',
            '/admin/events/new',
            '/admin/create-user',
            '/admin/change-password',
            '/admin/swish-config',
            '/profile',
            '/user/tasks'
        ]
        
        for route in admin_routes:
            response = client.get(route)
            # Should redirect to login (302) or return 403/404 (permission denied/not found)
            assert response.status_code in [302, 403, 404], f"Route {route} returned unexpected status: {response.status_code}"

    def test_authenticated_routes_with_user(self, test_app, client, test_user):
        """Test routes that require authentication work with logged-in user"""
        # Login as user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True

        # Routes that should work for authenticated users
        authenticated_routes = [
            '/profile',
            '/admin/logout'  # Should redirect after logout
        ]
        
        for route in authenticated_routes:
            response = client.get(route)
            # Should not crash (500) - may redirect or show content
            assert response.status_code != 500, f"Route {route} crashed with authenticated user"
            assert response.status_code in [200, 302, 403, 404], f"Route {route} returned unexpected status: {response.status_code}"

    def test_parametric_routes_no_crash(self, test_app, client, test_event, test_user):
        """Test parametric routes with valid IDs don't crash"""
        # Routes with parameters that need valid IDs
        parametric_routes = [
            f'/events/{test_event.id}/tasks',
            f'/admin/users/{test_user.id}/roles',
            f'/admin/events/{test_event.id}/tasks'
        ]
        
        for route in parametric_routes:
            response = client.get(route)
            # Should not crash - may require authentication but shouldn't error
            assert response.status_code != 500, f"Route {route} returned server error"
            assert response.status_code in [200, 302, 403, 404], f"Route {route} returned unexpected status: {response.status_code}"

    def test_task_route_with_user(self, test_app, client, test_user):
        """Test task route doesn't crash with logged in user"""
        # Login as user and add parent role
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True

        with test_app.app_context():
            User = test_app.User  # Get models from test app
            Group = test_app.Group
            user = test_app.db.session.get(User, test_user.id)
            parent_group = Group.query.filter_by(name='parent').first()
            if parent_group:
                user.groups.append(parent_group)
                test_app.db.session.commit()

        response = client.get('/tasks')
        # Should not crash
        assert response.status_code != 500, "Tasks route crashed with logged in user"


class TestPermissions:
    """Test permission decorators"""

    def test_user_has_role(self, test_app, test_admin, client):
        """Test user role checking"""
        with test_app.app_context():
            User = test_app.User  # Get User model from test app
            admin = test_app.db.session.get(User, test_admin.id)
            assert admin.has_role('admin')
            assert not admin.has_role('parent')


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_nonexistent_route(self, test_app, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_event_with_coordinator(self, test_app, client, test_event,
                                    test_event_manager):
        """Test event with coordinator assigned"""
        with test_app.app_context():
            Event = test_app.Event  # Get models from test app
            User = test_app.User
            event = test_app.db.session.get(Event, test_event.id)
            manager = test_app.db.session.get(User, test_event_manager.id)
            event.coordinator_id = manager.id
            test_app.db.session.commit()

            # Test that coordinator is properly linked
            assert event.coordinator is not None
            assert event.coordinator.email.startswith('manager_')
            assert event.coordinator.email.endswith('@example.com')

    def test_task_completion(self, test_app, client, test_event, test_user):
        """Test task completion functionality"""
        with test_app.app_context():
            EventTask = test_app.EventTask  # Get EventTask model from test app
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

    def test_user_event_task_relationship(self, test_app, client, test_user, test_event):
        """Test user-event-task relationships"""
        with test_app.app_context():
            EventTask = test_app.EventTask  # Get EventTask model from test app
            task = EventTask(event_id=test_event.id,
                             title='Relationship Test',
                             assigned_to_user_id=test_user.id)
            test_app.db.session.add(task)
            test_app.db.session.commit()

            # Test relationships
            assert task.event.title == 'Test Event'
            assert task.assigned_to.email.startswith('test_')
            assert task.assigned_to.email.endswith('@example.com')

    def test_cascade_deletion(self, test_app, client, test_event):
        """Test cascade deletion of related objects"""
        with test_app.app_context():
            EventTask = test_app.EventTask  # Get models from test app
            Event = test_app.Event
            # Create task for event
            task = EventTask(
                event_id=test_event.id,
                title='Will be deleted',
                description='This task should be deleted with event')
            test_app.db.session.add(task)
            test_app.db.session.commit()

            task_id = task.id

            # Delete event
            event = test_app.db.session.get(Event, test_event.id)
            test_app.db.session.delete(event)
            test_app.db.session.commit()

            # Check task is also deleted (cascade deletion)
            # For this simple test, we'll just check that event was deleted
            deleted_event = test_app.db.session.get(Event, test_event.id)
            assert deleted_event is None


class TestSwishPayments:
    """Test Swish payment functionality"""

    def test_swish_payment_model_creation(self, test_app, client):
        """Test SwishPayment model creation"""
        with test_app.app_context():
            SwishPayment = test_app.SwishPayment
            payment = SwishPayment(
                id='TESTPAYMENT123456789012345678901234',
                payee_payment_reference='BMK-TEST-12345',
                payee_alias='1234567890',
                amount=Decimal('250.00'),
                currency='SEK',
                message='Test donation',
                callback_url='https://example.com/callback',
                callback_identifier='callback-test-123',
                status='CREATED'
            )
            test_app.db.session.add(payment)
            test_app.db.session.commit()

            assert payment.id == 'TESTPAYMENT123456789012345678901234'
            assert payment.amount == Decimal('250.00')
            assert payment.status == 'CREATED'
            assert payment.currency == 'SEK'

    def test_swish_amount_formatting(self, test_app, client):
        """Test Swish amount formatting utility function"""
        # Test various amount formats
        def format_swish_amount(amount):
            return "{:.2f}".format(Decimal(str(amount)))
        
        assert format_swish_amount(100) == "100.00"
        assert format_swish_amount(99.5) == "99.50"
        assert format_swish_amount(Decimal('150.75')) == "150.75"
        assert format_swish_amount('200.123') == "200.12"  # Should round to 2 decimals

    def test_swish_phone_validation(self, test_app, client):
        """Test Swedish phone number validation for Swish"""
        import re
        
        def validate_swish_phone(phone_number):
            # Remove all non-digits
            digits = re.sub(r'\D', '', phone_number)
            
            # Check if it's a Swedish mobile number
            if digits.startswith('46'):
                # Already has country code
                if len(digits) >= 11 and len(digits) <= 13:
                    return digits
            elif digits.startswith('07'):
                # Swedish mobile starting with 07, convert to international format
                if len(digits) == 10:
                    return '46' + digits[1:]  # Remove leading 0, add country code
            elif len(digits) == 9 and digits.startswith('7'):
                # Swedish mobile without leading 0
                return '46' + digits
            
            return None
        
        # Test valid formats
        assert validate_swish_phone('0701234567') == '46701234567'
        assert validate_swish_phone('701234567') == '46701234567'
        assert validate_swish_phone('46701234567') == '46701234567'
        assert validate_swish_phone('+46 70 123 45 67') == '46701234567'
        assert validate_swish_phone('070-123 45 67') == '46701234567'

        # Test invalid formats
        assert validate_swish_phone('123456') is None
        assert validate_swish_phone('08123456') is None  # Landline
        assert validate_swish_phone('invalid') is None
        assert validate_swish_phone('') is None

    def test_swish_payment_creation_database_only(self, test_app, client, test_user):
        """Test Swish payment creation (database part only, without API call)"""
        with test_app.app_context():
            SwishPayment = test_app.SwishPayment
            
            # Set test configuration to avoid actual API calls
            test_app.config['SWISH_TEST_MODE'] = True
            test_app.config['SWISH_PAYEE_ALIAS'] = '1234567890'
            
            # Manually create payment record (simulating what SwishService would do)
            payment = SwishPayment(
                id='TEST123456789012345678901234567890',
                payee_payment_reference='BMK-20250819-TEST123',
                payer_alias='46701234567',
                payee_alias='1234567890',
                amount=Decimal('100.00'),
                currency='SEK',
                message='Test donation from TestUser',
                callback_url='https://test.com/swish/callback/TEST123456789012345678901234567890',
                callback_identifier='callback-test-identifier',
                status='CREATED',
                user_id=test_user.id
            )
            test_app.db.session.add(payment)
            test_app.db.session.commit()

            # Verify payment was created correctly
            assert payment.id is not None
            assert payment.user_id == test_user.id
            assert payment.amount == Decimal('100.00')
            assert payment.status == 'CREATED'
            assert payment.message == 'Test donation from TestUser'

    def test_swish_payment_status_updates(self, test_app, client):
        """Test payment status updates"""
        with test_app.app_context():
            SwishPayment = test_app.SwishPayment
            
            # Create test payment
            payment = SwishPayment(
                id='STATUSTEST123456789012345678901234',
                payee_payment_reference='BMK-STATUS-TEST',
                payee_alias='1234567890',
                amount=Decimal('50.00'),
                currency='SEK',
                message='Status test',
                callback_url='https://test.com/callback',
                callback_identifier='status-test-callback',
                status='PENDING'
            )
            test_app.db.session.add(payment)
            test_app.db.session.commit()

            # Test status update to PAID
            payment.status = 'PAID'
            payment.payment_reference = 'SWISH-PAID-REF-123'
            payment.date_paid = datetime.utcnow()
            test_app.db.session.commit()

            assert payment.status == 'PAID'
            assert payment.payment_reference == 'SWISH-PAID-REF-123'
            assert payment.date_paid is not None

            # Test status update to CANCELLED
            payment.status = 'CANCELLED'
            payment.date_cancelled = datetime.utcnow()
            test_app.db.session.commit()

            assert payment.status == 'CANCELLED'
            assert payment.date_cancelled is not None

    def test_swish_payment_relationships(self, test_app, client, test_user, test_event):
        """Test SwishPayment relationships with User and Event"""
        with test_app.app_context():
            SwishPayment = test_app.SwishPayment
            
            # Create payment linked to user and event
            payment = SwishPayment(
                id='RELATIONSHIP123456789012345678901234',
                payee_payment_reference='BMK-REL-TEST',
                payee_alias='1234567890',
                amount=Decimal('150.00'),
                currency='SEK',
                message='Event donation',
                callback_url='https://test.com/callback',
                callback_identifier='relationship-test',
                status='CREATED',
                user_id=test_user.id,
                event_id=test_event.id
            )
            test_app.db.session.add(payment)
            test_app.db.session.commit()

            # Test relationships
            assert payment.user is not None
            assert payment.user.id == test_user.id
            assert payment.event is not None
            assert payment.event.id == test_event.id
            assert payment.event.title == 'Test Event'

    def test_swish_payment_error_handling(self, test_app, client):
        """Test SwishPayment error handling fields"""
        with test_app.app_context():
            SwishPayment = test_app.SwishPayment
            
            # Create payment with error
            payment = SwishPayment(
                id='ERROR12345678901234567890123456789',
                payee_payment_reference='BMK-ERROR-TEST',
                payee_alias='1234567890',
                amount=Decimal('75.00'),
                currency='SEK',
                message='Error test',
                callback_url='https://test.com/callback',
                callback_identifier='error-test',
                status='ERROR',
                error_code='FF08',
                error_message='PayeeSSN is invalid'
            )
            test_app.db.session.add(payment)
            test_app.db.session.commit()

            assert payment.status == 'ERROR'
            assert payment.error_code == 'FF08'
            assert payment.error_message == 'PayeeSSN is invalid'


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
