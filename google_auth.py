"""
Google OAuth authentication blueprint for Brunnsbo Musikklasser
Handles Google Sign-In, account linking, and user creation
"""

import os
import json
import requests
from flask import Blueprint, redirect, request, url_for, flash, session
from flask_login import login_user, current_user, login_required
from oauthlib.oauth2 import WebApplicationClient
from app import db
from models import User, OAuthConnection, Group
from datetime import datetime
import logging

# Get environment variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    logging.error("Google OAuth credentials not found in environment variables")

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Create blueprint
google_auth = Blueprint('google_auth', __name__)

def get_google_provider_cfg():
    """Get Google's provider configuration"""
    try:
        return requests.get(GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        logging.error(f"Failed to get Google provider config: {e}")
        return None

@google_auth.route("/google_login")
def google_login():
    """Initiate Google OAuth login"""
    if not GOOGLE_CLIENT_ID:
        flash('Google authentication är inte korrekt konfigurerad', 'error')
        return redirect(url_for('login'))
    
    # Get Google's provider configuration
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        flash('Google authentication är inte tillgänglig just nu', 'error')
        return redirect(url_for('login'))
    
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use the request URL to construct the redirect URI
    # This ensures it works with Replit's dynamic domains
    redirect_uri = request.url_root.rstrip('/') + url_for('google_auth.google_callback')
    
    # Store the redirect URI in session for callback
    session['oauth_redirect_uri'] = redirect_uri
    
    # Debug logging
    logging.info(f"Google OAuth redirect_uri: {redirect_uri}")
    logging.info(f"Request URL root: {request.url_root}")
    logging.info(f"Generated callback URL: {url_for('google_auth.google_callback')}")
    logging.info(f"Client ID being used: {GOOGLE_CLIENT_ID[:20]}...")
    
    # Request the user's profile information
    # Note: For test mode apps, ensure minimal scopes and proper parameters
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"],
        access_type="offline",  # This can help with test mode
        prompt="select_account"  # Allow user to select account
    )
    
    # Debug logging for test mode troubleshooting
    logging.info(f"Full OAuth request URL: {request_uri}")
    logging.info(f"OAuth scopes requested: openid, email, profile")
    logging.info(f"Test mode note: Ensure your email is in Google Console test users list")
    
    return redirect(request_uri)

@google_auth.route("/google_callback")
def google_callback():
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID:
        flash('Google authentication är inte korrekt konfigurerad', 'error')
        return redirect(url_for('login'))
    
    # Get authorization code from request
    code = request.args.get("code")
    if not code:
        flash('Google authentication misslyckades', 'error')
        return redirect(url_for('login'))
    
    # Get Google's provider configuration
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        flash('Google authentication är inte tillgänglig just nu', 'error')
        return redirect(url_for('login'))
    
    token_endpoint = google_provider_cfg["token_endpoint"]
    redirect_uri = session.get('oauth_redirect_uri', request.url_root.rstrip('/') + url_for('google_auth.google_callback'))

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=redirect_uri,
        code=code,
    )
    
    try:
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
            timeout=10
        )
        
        if token_response.status_code != 200:
            logging.error(f"Token request failed: {token_response.status_code} - {token_response.text}")
            flash('Google authentication misslyckades', 'error')
            return redirect(url_for('login'))
        
        # Parse the tokens
        client.parse_request_body_response(json.dumps(token_response.json()))
        
    except Exception as e:
        logging.error(f"Token request error: {e}")
        flash('Google authentication misslyckades', 'error')
        return redirect(url_for('login'))

    # Get user info from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    
    try:
        userinfo_response = requests.get(uri, headers=headers, data=body, timeout=10)
        
        if userinfo_response.status_code != 200:
            logging.error(f"Userinfo request failed: {userinfo_response.status_code}")
            flash('Kunde inte hämta användarinformation från Google', 'error')
            return redirect(url_for('login'))
            
        userinfo = userinfo_response.json()
        
    except Exception as e:
        logging.error(f"Userinfo request error: {e}")
        flash('Kunde inte hämta användarinformation från Google', 'error')
        return redirect(url_for('login'))

    # Ensure we have required information
    if not userinfo.get("email_verified"):
        flash('Din Google-e-postadress är inte verifierad', 'error')
        return redirect(url_for('login'))

    google_id = userinfo["sub"]
    email = userinfo["email"]
    name = userinfo.get("name", "")
    given_name = userinfo.get("given_name", "")
    family_name = userinfo.get("family_name", "")
    picture = userinfo.get("picture")

    # Split the name if given_name or family_name are missing
    if not given_name or not family_name:
        name_parts = name.split(' ', 1)
        if not given_name:
            given_name = name_parts[0] if name_parts else "Okänt"
        if not family_name:
            family_name = name_parts[1] if len(name_parts) > 1 else "Efternamn"

    # Handle the OAuth login/registration
    return handle_google_oauth(google_id, email, given_name, family_name, picture, userinfo)

def handle_google_oauth(google_id, email, first_name, last_name, picture_url, full_userinfo):
    """Handle Google OAuth login/registration logic"""
    
    # Check if user is currently logged in (account linking)
    if current_user.is_authenticated:
        return handle_account_linking(google_id, email, first_name, last_name, picture_url, full_userinfo)
    
    # Check if an OAuth connection already exists
    oauth_connection = OAuthConnection.query.filter_by(
        provider='google',
        provider_user_id=google_id
    ).first()
    
    if oauth_connection:
        # Existing Google account - log them in
        user = oauth_connection.user
        if not user.active:
            flash('Ditt konto är inaktiverat', 'error')
            return redirect(url_for('login'))
        
        # Update OAuth connection info
        oauth_connection.provider_email = email
        oauth_connection.provider_name = f"{first_name} {last_name}"
        oauth_connection.provider_picture_url = picture_url
        oauth_connection.updated_at = datetime.utcnow()
        
        # Update user's last login
        user.last_login = datetime.utcnow()
        
        db.session.commit()
        login_user(user)
        
        flash(f'Välkommen tillbaka, {user.first_name}!', 'success')
        return redirect(url_for('index'))
    
    # Check if a user with this email already exists (password-based account)
    existing_user = User.query.filter_by(email=email).first()
    
    if existing_user:
        # Link Google account to existing user
        return link_google_to_existing_user(existing_user, google_id, email, first_name, last_name, picture_url)
    
    # New user - create account
    return create_new_google_user(google_id, email, first_name, last_name, picture_url)

def handle_account_linking(google_id, email, first_name, last_name, picture_url, full_userinfo):
    """Handle linking Google account to current logged-in user"""
    
    # Check if this Google account is already linked to another user
    existing_oauth = OAuthConnection.query.filter_by(
        provider='google',
        provider_user_id=google_id
    ).first()
    
    if existing_oauth and existing_oauth.user_id != current_user.id:
        flash('Detta Google-konto är redan kopplat till en annan användare', 'error')
        return redirect(url_for('user_profile'))
    
    # Check if current user already has a Google connection
    current_oauth = current_user.get_oauth_connection('google')
    if current_oauth:
        flash('Du har redan kopplat ett Google-konto till ditt konto', 'error')
        return redirect(url_for('user_profile'))
    
    # Check if the email matches
    if current_user.email != email:
        flash(f'Google-kontots e-postadress ({email}) matchar inte ditt kontos e-postadress ({current_user.email})', 'error')
        return redirect(url_for('user_profile'))
    
    # Create the OAuth connection
    oauth_connection = OAuthConnection(
        user_id=current_user.id,
        provider='google',
        provider_user_id=google_id,
        provider_email=email,
        provider_name=f"{first_name} {last_name}",
        provider_picture_url=picture_url
    )
    
    db.session.add(oauth_connection)
    db.session.commit()
    
    flash('Google-konto har kopplats till ditt konto!', 'success')
    return redirect(url_for('user_profile'))

def link_google_to_existing_user(user, google_id, email, first_name, last_name, picture_url):
    """Link Google account to existing password-based user"""
    
    # Create OAuth connection
    oauth_connection = OAuthConnection(
        user_id=user.id,
        provider='google',
        provider_user_id=google_id,
        provider_email=email,
        provider_name=f"{first_name} {last_name}",
        provider_picture_url=picture_url
    )
    
    db.session.add(oauth_connection)
    
    # Update user's last login
    user.last_login = datetime.utcnow()
    
    db.session.commit()
    login_user(user)
    
    flash(f'Google-konto kopplat! Välkommen tillbaka, {user.first_name}!', 'success')
    return redirect(url_for('index'))

def create_new_google_user(google_id, email, first_name, last_name, picture_url):
    """Create new user from Google OAuth"""
    
    # Create new user
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=None,  # No password for OAuth-only users
        active=True,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    
    db.session.add(user)
    db.session.flush()  # Get the user ID
    
    # Create OAuth connection
    oauth_connection = OAuthConnection(
        user_id=user.id,
        provider='google',
        provider_user_id=google_id,
        provider_email=email,
        provider_name=f"{first_name} {last_name}",
        provider_picture_url=picture_url
    )
    
    db.session.add(oauth_connection)
    
    # Note: New users should not have any groups assigned by default
    # Administrators will assign appropriate roles manually
    
    db.session.commit()
    login_user(user)
    
    flash(f'Välkommen till Brunnsbo Musikklasser, {first_name}! Ditt konto har skapats.', 'success')
    return redirect(url_for('index'))

@google_auth.route("/disconnect_google")
@login_required
def disconnect_google():
    """Disconnect Google account from current user"""
    
    oauth_connection = current_user.get_oauth_connection('google')
    if not oauth_connection:
        flash('Du har inget kopplat Google-konto', 'error')
        return redirect(url_for('user_profile'))
    
    # Check if user has a password - don't allow disconnection if it's their only auth method
    if not current_user.password_hash:
        flash('Du kan inte koppla bort Google-kontot eftersom du inte har något lösenord inställt. Skapa först ett lösenord via "Glömt lösenord".', 'error')
        return redirect(url_for('user_profile'))
    
    db.session.delete(oauth_connection)
    db.session.commit()
    
    flash('Google-konto har kopplats bort från ditt konto', 'success')
    return redirect(url_for('user_profile'))