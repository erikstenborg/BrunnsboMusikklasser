#!/usr/bin/env python3
"""
Production Admin User Creation Script
Run this script in production to create admin users with custom passwords
"""

import os
import sys
import getpass
from app import app, db
from models import AdminUser

def create_admin_user():
    """Create a new admin user for production"""
    
    print("=== Brunnsbo Musikklasser - Skapa Administratör ===")
    print()
    
    # Get user input
    username = input("Användarnamn: ").strip()
    if not username:
        print("Fel: Användarnamn är obligatoriskt")
        return False
    
    email = input("E-postadress: ").strip()
    if not email or '@' not in email:
        print("Fel: Giltig e-postadress är obligatorisk")
        return False
    
    # Get password securely
    while True:
        password = getpass.getpass("Lösenord (visas inte): ")
        if len(password) < 8:
            print("Fel: Lösenordet måste vara minst 8 tecken långt")
            continue
        
        confirm_password = getpass.getpass("Bekräfta lösenord: ")
        if password != confirm_password:
            print("Fel: Lösenorden matchar inte")
            continue
        break
    
    # Check if user already exists
    existing_user = AdminUser.query.filter(
        (AdminUser.username == username) | (AdminUser.email == email)
    ).first()
    
    if existing_user:
        print(f"Fel: Användare med användarnamn '{username}' eller e-post '{email}' finns redan")
        return False
    
    try:
        # Create new admin user
        new_user = AdminUser()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        new_user.active = True
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✓ Administratör '{username}' har skapats!")
        print(f"  E-post: {email}")
        print(f"  Status: Aktiv")
        print()
        print("Du kan nu logga in på /admin/login")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Fel: {str(e)}")
        return False

def list_admin_users():
    """List all existing admin users"""
    print("=== Befintliga Administratörer ===")
    users = AdminUser.query.all()
    
    if not users:
        print("Inga administratörer hittades.")
        return
    
    for user in users:
        status = "Aktiv" if user.active else "Inaktiv"
        last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Aldrig"
        print(f"- {user.username} ({user.email}) - {status} - Senast inloggad: {last_login}")

def main():
    with app.app_context():
        if len(sys.argv) > 1 and sys.argv[1] == 'list':
            list_admin_users()
        else:
            create_admin_user()

if __name__ == "__main__":
    main()