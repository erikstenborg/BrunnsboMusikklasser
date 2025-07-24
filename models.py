from app import db
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer

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
    status = db.Column(String(20), default='submitted')  # submitted, reviewed, accepted, rejected
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
