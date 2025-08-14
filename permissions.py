"""
Role-based permission decorators for the Brunnsbo Musikklasser application
"""

from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user, login_required

def requires_role(role_name):
    """
    Decorator that requires a user to have a specific role
    Usage: @requires_role('Admin')
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if not current_user.has_role(role_name):
                flash(f'Du saknar behörighet för denna sida. Krävs: {role_name}', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def requires_any_role(*role_names):
    """
    Decorator that requires a user to have at least one of the specified roles
    Usage: @requires_any_role('Admin', 'applications_manager')
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            if not any(current_user.has_role(role) for role in role_names):
                roles_str = ', '.join(role_names)
                flash(f'Du saknar behörighet för denna sida. Krävs en av: {roles_str}', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator for admin-only routes"""
    return requires_role('Admin')(f)

def applications_manager_required(f):
    """Decorator for application management routes"""
    return requires_any_role('Admin', 'applications_manager')(f)

def event_manager_required(f):
    """Decorator for event management routes"""
    return requires_any_role('Admin', 'event_manager')(f)

def parent_access_required(f):
    """Decorator for parent-only features"""
    return requires_any_role('Admin', 'parent')(f)

def authenticated_required(f):
    """Decorator for any authenticated user (regardless of role)"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function