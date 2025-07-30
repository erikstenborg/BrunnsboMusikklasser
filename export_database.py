#!/usr/bin/env python3
"""
Database Export Script for Brunnsbo Musikklasser
Exports development data for import into production database
"""

import os
import psycopg2
from datetime import datetime

def export_data():
    # Connect to database using the same connection as your app
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        return
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    print(f"Database Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Export Admin Users
    print("\n-- Admin Users Export")
    cursor.execute("SELECT id, username, email, password_hash, active, created_at, last_login FROM admin_users")
    admin_users = cursor.fetchall()
    
    for row in admin_users:
        print(f"INSERT INTO admin_users (id, username, email, password_hash, active, created_at, last_login) VALUES")
        print(f"({row[0]}, '{row[1]}', '{row[2]}', '{row[3]}', {row[4]}, '{row[5]}', '{row[6]}')")
        print("ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username, email = EXCLUDED.email, password_hash = EXCLUDED.password_hash, active = EXCLUDED.active, created_at = EXCLUDED.created_at, last_login = EXCLUDED.last_login;")
    
    # Export Events
    print("\n-- Events Export")
    cursor.execute("SELECT id, title, description, event_date, location, ticket_url, is_active, created_at FROM event")
    events = cursor.fetchall()
    
    for row in events:
        title = row[1].replace("'", "''")  # Escape single quotes
        description = row[2].replace("'", "''") if row[2] else ''
        location = row[4].replace("'", "''") if row[4] else ''
        ticket_url = row[5] if row[5] else ''
        
        print(f"INSERT INTO event (id, title, description, event_date, location, ticket_url, is_active, created_at) VALUES")
        print(f"({row[0]}, '{title}', '{description}', '{row[3]}', '{location}', '{ticket_url}', {row[6]}, '{row[7]}')")
        print("ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, description = EXCLUDED.description, event_date = EXCLUDED.event_date, location = EXCLUDED.location, ticket_url = EXCLUDED.ticket_url, is_active = EXCLUDED.is_active, created_at = EXCLUDED.created_at;")
    
    # Update sequences
    print("\n-- Update sequences")
    print("SELECT setval('admin_users_id_seq', (SELECT MAX(id) FROM admin_users));")
    print("SELECT setval('event_id_seq', (SELECT MAX(id) FROM event));")
    
    # Summary
    print(f"\n-- Summary")
    print(f"-- Exported {len(admin_users)} admin users")
    print(f"-- Exported {len(events)} events")
    print(f"-- Total records: {len(admin_users) + len(events)}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        export_data()
    except Exception as e:
        print(f"Error: {e}")