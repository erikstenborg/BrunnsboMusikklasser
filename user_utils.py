"""
Utility functions for user role management and selection
"""
from models import Group

def get_assignable_users():
    """
    Get all users who can be assigned tasks (parent, event_manager, or admin)
    Returns a list of unique active users sorted by name
    """
    assignable_users = []
    for group_name in ['parent', 'event_manager', 'admin']:
        group = Group.query.filter_by(name=group_name).first()
        if group:
            assignable_users.extend([user for user in group.users if user.active])
    
    # Remove duplicates (users might have multiple roles)
    seen_users = set()
    unique_users = []
    for user in assignable_users:
        if user.id not in seen_users:
            unique_users.append(user)
            seen_users.add(user.id)
    
    return sorted(unique_users, key=lambda u: (u.first_name, u.last_name))

def can_manage_tasks(user):
    """
    Check if user can manage tasks (event_manager or admin)
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_role('event_manager') or user.has_role('admin')

def can_access_tasks(user):
    """
    Check if user can access task functionality (parent, event_manager, or admin)
    """
    if not user or not user.is_authenticated:
        return False
    return (user.has_role('parent') or 
            user.has_role('event_manager') or 
            user.has_role('admin'))

def get_user_choices_for_forms():
    """
    Get formatted choices list for form dropdowns
    Returns list of (id, display_name) tuples
    """
    users = get_assignable_users()
    choices = [('', 'Ingen tilldelning')]
    choices.extend([
        (str(user.id), f"{user.first_name} {user.last_name} ({user.email})") 
        for user in users
    ])
    return choices