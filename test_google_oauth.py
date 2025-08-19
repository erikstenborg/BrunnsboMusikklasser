#!/usr/bin/env python3
"""
Test script to verify Google OAuth configuration
"""
import os
import requests
from flask import Flask, url_for

# Create a test Flask app to generate URLs
app = Flask(__name__)
app.config['SERVER_NAME'] = os.environ.get('REPLIT_DEV_DOMAIN')

def test_google_oauth_config():
    """Test Google OAuth configuration"""
    print("🧪 GOOGLE OAUTH CONFIGURATION TEST")
    print("=" * 50)
    
    # Check environment variables
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    domain = os.environ.get('REPLIT_DEV_DOMAIN')
    
    print(f"✅ GOOGLE_OAUTH_CLIENT_ID: {'SET' if client_id else '❌ NOT SET'}")
    print(f"✅ GOOGLE_OAUTH_CLIENT_SECRET: {'SET' if client_secret else '❌ NOT SET'}")
    print(f"✅ REPLIT_DEV_DOMAIN: {domain}")
    print()
    
    # Generate the exact callback URL
    callback_url = f"https://{domain}/auth/google_callback"
    print("📍 EXACT CALLBACK URL FOR GOOGLE CONSOLE:")
    print(f"   {callback_url}")
    print()
    
    # Test Google's discovery endpoint
    try:
        print("🌐 Testing Google OAuth discovery endpoint...")
        response = requests.get("https://accounts.google.com/.well-known/openid-configuration", timeout=5)
        if response.status_code == 200:
            print("✅ Google OAuth discovery endpoint is accessible")
            config = response.json()
            print(f"   Authorization endpoint: {config.get('authorization_endpoint', 'Not found')}")
        else:
            print(f"❌ Google OAuth discovery failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Google: {e}")
    
    print()
    print("📋 GOOGLE CLOUD CONSOLE SETUP:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Select your OAuth 2.0 Client ID")
    print("3. In 'Authorized redirect URIs', add EXACTLY this URL:")
    print(f"   {callback_url}")
    print("4. Also add for production:")
    print("   https://brunnsbomusikklasser.replit.app/auth/google_callback")
    print("5. Save changes")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Do NOT add just the domain")
    print("   - Do NOT add 'https://replit.com'")
    print("   - The callback path '/auth/google_callback' is required")
    print("   - URLs must match EXACTLY (no trailing slashes)")

if __name__ == "__main__":
    test_google_oauth_config()