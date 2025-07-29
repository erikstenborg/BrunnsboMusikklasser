# replit.md

## Overview

Brunnsbo Musikklasser is a Flask-based web application for a Swedish music school that has been operating for 40 years (1985-2025). The application manages student applications, events, news posts, and contact information. It's designed to help the school handle admissions for their music classes and provide information to prospective students and parents.

## Recent Changes

**2025-07-29**: 
- Added comprehensive event management system with public events page (/evenemang) and admin interface
- Created admin user authentication system with database table (AdminUser model)
- Implemented protected admin routes for event creation, editing, and deletion
- Added Flask-Login integration for session management
- Created admin login page (/admin/login) and event management dashboard (/admin/events)
- Set up initial admin user (username: admin, password: admin123) and sample events
- Added "Evenemang" navigation link to main menu

**2025-07-24**: 
- Replaced SVG logo with 40th anniversary GIF logo throughout the website
- Removed "Hedersuppdrag från Hans Majestät Konungen" and "Vi älskar att sjunga all sorts musik!" sections from homepage for cleaner layout
- Fixed footer text colors for better readability against dark background
- Resolved JavaScript errors and missing error templates (404.html, 500.html)
- Fixed SQLAlchemy model constructor issues for proper database handling

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional Flask web application architecture with server-side rendering and a PostgreSQL database. It uses SQLAlchemy for database operations and Flask-Mail for email functionality.

### Core Technologies
- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Server-side rendered HTML templates with Bootstrap 5
- **Email**: Flask-Mail for application notifications
- **Forms**: Flask-WTF with WTForms for form handling and validation

## Key Components

### Models (models.py)
- **Event**: Manages upcoming concerts and events with scheduling and ticketing information
- **Application**: Handles student applications with comprehensive form data including personal information, musical experience, and academic details
- **NewsPost**: Content management for school news and announcements
- **Contact**: Contact form submissions (referenced in routes but not fully implemented in provided code)

### Forms (forms.py)
- **ApplicationForm**: Comprehensive form for student applications with Swedish validation messages
- Includes validation for Swedish personal numbers (personnummer) and postal codes
- **ContactForm**: Referenced but not fully shown in provided files

### Routes (routes.py)
- **Homepage** (`/`): Displays latest news and upcoming events
- **About page** (`/om-oss`): Information about the school and teachers
- **Application page** (`/ansokan`): Student application form with email notifications
- **Contact page**: Contact information and form

### Templates
- **Base template** (`base.html`): Responsive layout with Bootstrap navigation
- **Page templates**: Swedish-language content with professional styling
- **Form templates**: Accessible forms with validation feedback

## Data Flow

1. **Student Applications**: 
   - Users fill out comprehensive application forms
   - Data is validated using WTForms validators
   - Applications are stored in PostgreSQL database
   - Email notifications are sent to administrators
   - Applications can be tracked by status (submitted, reviewed, accepted, rejected)

2. **Content Management**:
   - Events and news are managed through the database
   - Content is displayed on the homepage and dedicated pages
   - Events are filtered to show only upcoming and active items

3. **Contact Management**:
   - Contact information is displayed on dedicated contact page
   - Contact forms (when implemented) store inquiries in database

## External Dependencies

### Email Service
- Flask-Mail integration for sending application notifications
- Configurable SMTP settings via environment variables
- Default sender configured as info@brunnsbomusikklasser.nu

### Frontend Assets
- Bootstrap 5 CSS framework via CDN
- Font Awesome icons via CDN
- Google Fonts (Playfair Display and Source Sans Pro)
- Custom CSS for brand-specific styling with gold color scheme

### Database
- PostgreSQL as primary database solution
- SQLAlchemy ORM for database interactions
- Connection pooling and health checks configured

## Deployment Strategy

### Environment Configuration
- Database URL configurable via `DATABASE_URL` environment variable
- Mail server settings configurable via environment variables
- Session secret configurable via `SESSION_SECRET`
- Default fallbacks provided for development

### Production Considerations
- ProxyFix middleware for reverse proxy compatibility
- Database connection pooling with 300-second recycle time
- Pre-ping enabled for connection health checks
- Logging configured at DEBUG level

### Application Structure
- `main.py`: Entry point for development server
- `app.py`: Application factory and configuration
- Modular structure with separate files for models, routes, and forms
- Static assets organized in dedicated directories

The application is designed to be deployed on platforms that support Flask applications with PostgreSQL databases, with all sensitive configuration managed through environment variables.