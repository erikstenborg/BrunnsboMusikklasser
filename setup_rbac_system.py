#!/usr/bin/env python3
"""
Script to set up the new Role-Based Access Control (RBAC) system
This script will:
1. Create the new tables (users, groups, user_groups, event_tasks)
2. Migrate existing admin_users data to the new users table
3. Create the default groups/roles
4. Assign appropriate roles to migrated users
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Group, Event, EventTask
from sqlalchemy import text

def create_default_groups():
    """Create the default user groups/roles"""
    groups_data = [
        {
            'name': 'Admin',
            'description': 'Full system access - can manage users, assign roles, and access all administrative functions'
        },
        {
            'name': 'applications_manager',
            'description': 'Can view and edit student applications'
        },
        {
            'name': 'event_manager',
            'description': 'Can create, edit, and delete events'
        },
        {
            'name': 'parent',
            'description': 'Can view parent-specific event information and manage event tasks'
        }
    ]
    
    created_groups = []
    for group_data in groups_data:
        # Check if group already exists
        existing_group = Group.query.filter_by(name=group_data['name']).first()
        if not existing_group:
            group = Group(
                name=group_data['name'],
                description=group_data['description']
            )
            db.session.add(group)
            created_groups.append(group)
            print(f"Created group: {group_data['name']}")
        else:
            created_groups.append(existing_group)
            print(f"Group already exists: {group_data['name']}")
    
    return created_groups

def migrate_admin_users():
    """Migrate existing admin_users to the new users table with Admin role"""
    try:
        # Check if admin_users table exists (PostgreSQL)
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name='admin_users'"))
        if not result.fetchone():
            print("No admin_users table found - skipping migration")
            return []
        
        # Get existing admin users
        admin_users_data = db.session.execute(text("""
            SELECT id, username, email, password_hash, active, created_at, last_login 
            FROM admin_users
        """)).fetchall()
        
        migrated_users = []
        admin_group = Group.query.filter_by(name='Admin').first()
        
        for admin_data in admin_users_data:
            # Check if user already exists in new users table
            existing_user = User.query.filter_by(username=admin_data.username).first()
            if not existing_user:
                # Create new user
                user = User(
                    username=admin_data.username,
                    email=admin_data.email,
                    password_hash=admin_data.password_hash,
                    active=admin_data.active,
                    created_at=admin_data.created_at,
                    last_login=admin_data.last_login
                )
                db.session.add(user)
                db.session.flush()  # Get the ID
                
                # Assign Admin role
                if admin_group:
                    user.groups.append(admin_group)
                
                migrated_users.append(user)
                print(f"Migrated admin user: {admin_data.username}")
            else:
                # Ensure existing user has Admin role
                if admin_group and admin_group not in existing_user.groups:
                    existing_user.groups.append(admin_group)
                migrated_users.append(existing_user)
                print(f"Updated existing user with Admin role: {admin_data.username}")
        
        return migrated_users
        
    except Exception as e:
        print(f"Error during admin user migration: {str(e)}")
        return []

def update_event_model():
    """Add new columns to the Event table if they don't exist"""
    try:
        # Check if info_to_parents column exists
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='event' AND column_name='info_to_parents'"))
        if not result.fetchone():
            # Add the column
            db.session.execute(text("ALTER TABLE event ADD COLUMN info_to_parents TEXT"))
            print("Added info_to_parents column to event table")
        else:
            print("info_to_parents column already exists")
            
    except Exception as e:
        print(f"Error updating event model: {str(e)}")

def setup_rbac_system():
    """Main function to set up the RBAC system"""
    print("Setting up Role-Based Access Control (RBAC) system...")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            
            # Create default groups
            print("\nCreating default user groups...")
            groups = create_default_groups()
            
            # Update event model
            print("\nUpdating event model...")
            update_event_model()
            
            # Migrate existing admin users
            print("\nMigrating existing admin users...")
            migrated_users = migrate_admin_users()
            
            # Commit all changes
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("RBAC system setup completed successfully!")
            print(f"Created {len(groups)} user groups")
            print(f"Migrated {len(migrated_users)} admin users")
            
            # Display summary
            print("\nAvailable roles:")
            for group in groups:
                print(f"  - {group.name}: {group.description}")
            
            print("\nMigrated users:")
            for user in migrated_users:
                roles = [group.name for group in user.groups]
                print(f"  - {user.username} ({user.email}): {', '.join(roles)}")
            
            print("\nNext steps:")
            print("1. Test the login system")
            print("2. Create additional users as needed")
            print("3. Assign appropriate roles to users")
            print("4. Optional: Drop the old admin_users table after verification")
            
        except Exception as e:
            print(f"Error setting up RBAC system: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    setup_rbac_system()