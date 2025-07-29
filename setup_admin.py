#!/usr/bin/env python3
"""
Setup script to create default admin user and sample events.
Run this once to initialize the admin system.
"""

from app import app, db
from models import AdminUser, Event
from datetime import datetime, timedelta

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    with app.app_context():
        # Check if admin user already exists
        existing_admin = AdminUser.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create new admin user
        admin = AdminUser()
        admin.username = 'admin'
        admin.email = 'admin@brunnsbomusikklasser.nu'
        admin.set_password('admin123')  # Change this password immediately!
        admin.active = True
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("IMPORTANT: Change this password immediately after first login!")

def create_sample_events():
    """Create some sample events"""
    with app.app_context():
        # Check if events already exist
        existing_events = Event.query.count()
        if existing_events > 0:
            print(f"Events already exist ({existing_events} events found)")
            return
        
        # Create sample events
        events_data = [
            {
                'title': 'Julkonsert 2025',
                'description': 'Vår traditionella julkonsert med alla våra musikklasser. Ett magiskt evenemang där eleverna får visa upp vad de lärt sig under terminen.',
                'event_date': datetime(2025, 12, 15, 18, 0),
                'location': 'Angered Arena',
                'ticket_url': 'https://example.com/tickets/julkonsert',
                'is_active': True
            },
            {
                'title': 'Vårkonsert 2026',
                'description': 'Avslutning på läsåret med en härlig vårkonsert där alla klasser medverkar.',
                'event_date': datetime(2026, 5, 20, 19, 0),
                'location': 'Brunnsbo Kulturhus',
                'ticket_url': None,
                'is_active': True
            },
            {
                'title': '40-årsjubileum Festkonsert',
                'description': 'En extra festlig konsert för att fira Brunnsbo Musikklassers 40-årsjubileum! Med tidigare elever, nuvarande elever och lärare.',
                'event_date': datetime(2025, 11, 10, 17, 0),
                'location': 'Göteborgs Konserthus',
                'ticket_url': 'https://example.com/tickets/jubileum',
                'is_active': True
            }
        ]
        
        for event_data in events_data:
            event = Event()
            event.title = event_data['title']
            event.description = event_data['description']
            event.event_date = event_data['event_date']
            event.location = event_data['location']
            event.ticket_url = event_data['ticket_url']
            event.is_active = event_data['is_active']
            
            db.session.add(event)
        
        db.session.commit()
        print(f"Created {len(events_data)} sample events!")

if __name__ == '__main__':
    print("Setting up Brunnsbo Musikklasser admin system...")
    create_admin_user()
    create_sample_events()
    print("Setup complete!")