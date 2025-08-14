from app import db
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Association table for many-to-many relationship between users and groups
user_groups = Table('user_groups', db.metadata,
    db.Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    db.Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
)

class Event(db.Model):
    """Model for storing upcoming events and concerts"""
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    event_date = db.Column(DateTime, nullable=False)
    location = db.Column(String(200))
    ticket_url = db.Column(String(500))
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Parent-specific fields
    info_to_parents = db.Column(Text)  # Information visible only to parents
    
    # Relationship with tasks
    tasks = relationship('EventTask', back_populates='event', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Evenemang {self.title}>'

class Application(db.Model):
    """Model for storing student applications"""
    id = db.Column(Integer, primary_key=True)
    student_name = db.Column(String(100), nullable=False)
    student_personnummer = db.Column(String(13), nullable=False)
    parent_name = db.Column(String(100), nullable=False)
    parent_email = db.Column(String(120), nullable=False)
    parent_phone = db.Column(String(20), nullable=False)
    address = db.Column(String(200), nullable=False)
    postal_code = db.Column(String(10), nullable=False)
    city = db.Column(String(50), nullable=False)
    current_school = db.Column(String(100))
    musical_experience = db.Column(Text)
    motivation = db.Column(Text)
    grade_applying_for = db.Column(String(10), nullable=False)
    has_transportation = db.Column(Boolean, default=False)
    additional_info = db.Column(Text)
    application_year = db.Column(String(9), nullable=False)  # e.g., "2025/2026"
    status = db.Column(String(30), default='applied')  # applied, email_confirmed, application_withdrawn, invited_for_audition, rejected, offered, accepted
    email_confirmed = db.Column(Boolean, default=False)  # Email confirmation status
    email_confirmed_at = db.Column(DateTime)  # When email was confirmed
    admin_notes = db.Column(Text)  # Admin notes for the application
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.student_name} - {self.application_year}>'

class NewsPost(db.Model):
    """Model for storing news and announcements"""
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(200), nullable=False)
    content = db.Column(Text, nullable=False)
    author = db.Column(String(100))
    published_date = db.Column(DateTime, default=datetime.utcnow)
    is_published = db.Column(Boolean, default=True)
    featured = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<NewsPost {self.title}>'

class Contact(db.Model):
    """Model for storing contact form submissions"""
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    email = db.Column(String(120), nullable=False)
    phone = db.Column(String(20))
    subject = db.Column(String(200), nullable=False)
    message = db.Column(Text, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    is_read = db.Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<Contact {self.name} - {self.subject}>'

class ConfirmationCode(db.Model):
    """Model for storing email confirmation codes"""
    __tablename__ = 'confirmation_codes'
    
    id = db.Column(Integer, primary_key=True)
    code = db.Column(String(64), nullable=False, unique=True, index=True)
    email = db.Column(String(120), nullable=False)
    purpose = db.Column(String(50), nullable=False)  # email_verification, password_reset, user_registration
    used = db.Column(Boolean, default=False)
    used_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    expires_at = db.Column(DateTime, nullable=False)
    
    def is_expired(self):
        """Check if the confirmation code is expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Check if the confirmation code is valid (not used and not expired)"""
        return not self.used and not self.is_expired()
    
    def __repr__(self):
        return f'<ConfirmationCode {self.code[:8]}... - {self.email}>'

class User(UserMixin, db.Model):
    """Model for all users in the system"""
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(256), nullable=False)
    active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_login = db.Column(DateTime)
    
    # Many-to-many relationship with groups
    groups = relationship('Group', secondary=user_groups, back_populates='users')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(group.name == role_name for group in self.groups)
    
    def get_roles(self):
        """Get list of role names for this user"""
        return [group.name for group in self.groups]
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.has_role('Admin')
    
    def is_applications_manager(self):
        """Check if user can manage applications"""
        return self.has_role('applications_manager')
    
    def is_event_manager(self):
        """Check if user can manage events"""
        return self.has_role('event_manager')
    
    def is_parent(self):
        """Check if user is a parent"""
        return self.has_role('parent')
    
    @property
    def full_name(self):
        """Get the user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property 
    def username(self):
        """Backwards compatibility property that returns full name"""
        return self.full_name
    
    def __repr__(self):
        return f'<User {self.email} - {self.full_name}>'

class Group(db.Model):
    """Model for user groups/roles"""
    __tablename__ = 'groups'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), unique=True, nullable=False)
    description = db.Column(String(200))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship with users
    users = relationship('User', secondary=user_groups, back_populates='groups')
    
    def __repr__(self):
        return f'<Group {self.name}>'

class EventTask(db.Model):
    """Model for tasks associated with events that parents can manage"""
    __tablename__ = 'event_tasks'
    
    id = db.Column(Integer, primary_key=True)
    event_id = db.Column(Integer, ForeignKey('event.id'), nullable=False)
    title = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    assigned_to_user_id = db.Column(Integer, ForeignKey('users.id'))
    completed = db.Column(Boolean, default=False)
    completed_at = db.Column(DateTime)
    completed_by_user_id = db.Column(Integer, ForeignKey('users.id'))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship('Event', back_populates='tasks')
    assigned_to = relationship('User', foreign_keys=[assigned_to_user_id])
    completed_by = relationship('User', foreign_keys=[completed_by_user_id])
    
    def __repr__(self):
        return f'<EventTask {self.title}>'
