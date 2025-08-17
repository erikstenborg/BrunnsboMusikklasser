import os
import logging
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
mail = Mail()
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "brunnsbo-musikklasser-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# CSRF and Session Configuration for Safari compatibility
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP for development
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow JavaScript access for debugging
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allow cross-site requests with proper referrer
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow CSRF over HTTP for development
app.config['SESSION_PERMANENT'] = True  # Make sessions permanent
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Default 24 hour session lifetime
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable default CSRF for debugging
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365)  # Remember me duration: 1 year

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/brunnsbo_musikklasser")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Mail configuration - configured for external SMTP (Gmail/SendGrid)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# Swish m-commerce payment configuration
app.config['SWISH_TEST_MODE'] = os.environ.get('SWISH_TEST_MODE', 'true').lower() == 'true'
app.config['SWISH_PAYEE_ALIAS'] = os.environ.get('SWISH_PAYEE_ALIAS', '123268258')  # Brunnsbo Musikklasser Swish number
app.config['SWISH_CERT_PATH'] = os.environ.get('SWISH_CERT_PATH')
app.config['SWISH_CERT_PASSWORD'] = os.environ.get('SWISH_CERT_PASSWORD')
app.config['SWISH_CA_CERT_PATH'] = os.environ.get('SWISH_CA_CERT_PATH')

# initialize the app with extensions
db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Du måste logga in för att komma åt denna sida.'

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Set up user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = models.User.query.get(int(user_id))
            logging.debug(f"Loading user {user_id}: {user is not None}")
            if user:
                logging.debug(f"User {user_id} active: {user.active}")
            return user
        except Exception as e:
            logging.error(f"Error loading user {user_id}: {e}")
            return None
    
    # Create all tables
    db.create_all()

# Enable debug mode for development
app.debug = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
