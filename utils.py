"""
Utility functions for the application
"""
import secrets
import string
from datetime import datetime, timedelta
from app import db

def generate_confirmation_code(length=32, numeric_only=False):
    """
    Generate a secure random confirmation code.
    
    Args:
        length (int): Length of the confirmation code (default: 32)
        numeric_only (bool): If True, generate only numeric code (default: False)
        
    Returns:
        str: A secure random confirmation code
    """
    if numeric_only:
        # For numeric codes (like password reset), use digits only
        alphabet = string.digits
    else:
        # For other purposes, use alphanumeric
        alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_confirmation_code(email, purpose='email_verification', expires_in_hours=24):
    """
    Create a confirmation code and store it in the database.
    
    Args:
        email (str): Email address to create code for
        purpose (str): Purpose of the confirmation code
        expires_in_hours (int): Hours until the code expires
        
    Returns:
        ConfirmationCode: The created confirmation code object
    """
    from models import ConfirmationCode
    
    # Remove any existing codes for this email and purpose
    ConfirmationCode.query.filter_by(email=email, purpose=purpose, used=False).delete()
    
    # Create new confirmation code - use 32-character alphanumeric for all purposes
    code = generate_confirmation_code()
    
    confirmation = ConfirmationCode(
        code=code,
        email=email,
        purpose=purpose,
        expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
    )
    
    db.session.add(confirmation)
    db.session.commit()
    
    return confirmation

def verify_confirmation_code(email, code, purpose=None):
    """
    Verify a confirmation code and mark it as used if valid.
    
    Args:
        email (str): Email address associated with the code
        code (str): The confirmation code to verify
        purpose (str, optional): Purpose of the confirmation code
        
    Returns:
        ConfirmationCode or None: The confirmation object if valid, None otherwise
    """
    from models import ConfirmationCode
    
    # Build query filters
    filters = {
        'email': email,
        'code': code,
        'used': False
    }
    
    if purpose:
        filters['purpose'] = purpose
    
    confirmation = ConfirmationCode.query.filter_by(**filters).first()
    
    if not confirmation:
        return None
        
    if confirmation.is_expired():
        return None
    
    # Mark as used
    confirmation.used = True
    confirmation.used_at = datetime.utcnow()
    db.session.commit()
    
    return confirmation