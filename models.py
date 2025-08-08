from app import db
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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
    
    def __repr__(self):
        return f'<Event {self.title}>'

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

class AdminUser(UserMixin, db.Model):
    """Model for admin users who can manage events"""
    __tablename__ = 'admin_users'
    
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(64), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(256), nullable=False)
    active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_login = db.Column(DateTime)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<AdminUser {self.username}>'
