# replit.md

## Overview

Brunnsbo Musikklasser is a Flask-based web application for a Swedish music school that has been operating for 40 years (1985-2025). The application manages student applications, events, news posts, and contact information. It's designed to help the school handle admissions for their music classes and provide information to prospective students and parents.

## Recent Changes

**2025-08-14**:
- **Safari Authentication Fix**: Resolved Safari login issues by bypassing CSRF validation and enhancing session management
- **Cross-browser Security**: Fixed session persistence issues with proper Flask-Login configuration and permanent sessions
- **Enhanced Login System**: Added "Remember me" functionality with 1-year session duration option vs 24-hour default
- **Template Cleanup**: Renamed admin_login.html to login.html and removed debug links for cleaner user experience
- **Session Management**: Implemented dynamic session duration based on user preference with comprehensive logging
- **Facebook Widget Optimization**: Completely removed special resize handling and continuous monitoring to eliminate WINCH signal spam in server logs
- **Swedish Date Format Implementation**: Updated datetime input fields with Swedish locale attributes and format guidance (YYYY-MM-DD TT:MM)
- **Browser Locale Compatibility**: Datetime inputs now respect browser's locale settings while maintaining proper data format validation
- **Enhanced User Experience**: Added 5-minute step intervals and Swedish format hints for better datetime input usability  
- **Event Management UI Improvements**: Removed description display from admin events table for more compact row display

**2025-08-14** (Earlier):
- **Email-based Authentication System**: Converted login system from username/password to email/password authentication
- **User Model Restructuring**: Replaced username field with separate first_name and last_name fields (Förnamn/Efternamn)
- **Database Cleanup**: Removed obsolete username column from users table and dropped admin_users table completely
- **User Registration Enhancement**: Updated registration forms to collect first and last names separately
- **Data Migration**: Successfully migrated existing user data to new field structure with proper names
- **Template Updates**: Modified all login and registration templates to use email-based authentication
- **Outdated File Removal**: Cleaned up obsolete setup_admin.py, create_production_admin.py, and setup_rbac_system.py files
- **RBAC System**: Maintained comprehensive Role-Based Access Control with Admin, applications_manager, event_manager, and parent roles
- **Password Reset Enhancement**: Complete email-based password reset with 32-character confirmation codes that auto-populate from email links
- **User Registration**: New users can register with email verification but receive no permissions until admin assigns roles
- **Unified Confirmation Codes**: Standardized both password reset and email verification to use 32-character alphanumeric codes for better copy/paste usability
- **Integrated Parent Info**: Merged parent-specific event information into main events page instead of separate page for cleaner user experience
- **Enhanced Task Management**: Complete task creation, editing, and deletion system for event managers with proper user assignment functionality
- **Case-Sensitive Group Fix**: Fixed group name case sensitivity issue (Admin vs admin) ensuring proper role-based access control
- **Parent Info Integration Complete**: Successfully integrated parent-specific information and tasks into main events page with role-based display
- **Personal Task Management**: Created dedicated "Mina uppgifter" page for parents with task completion functionality
- **Enhanced Event Manager Controls**: Full CRUD operations for event managers including task reassignment and status toggling
- **JSON Serialization Fix**: Fixed server error by storing only confirmation code strings in session instead of ConfirmationCode objects
- **32-Character Confirmation Codes**: Updated email verification forms and templates to properly handle 32-character alphanumeric codes
- **Pre-filled Email Links**: Added convenient direct links in confirmation emails that auto-populate forms with correct email and code
- **Expanded Task Assignment System**: Tasks can now be assigned to users with parent, event_manager, or admin roles (previously parent-only)
- **Centralized User Utility Functions**: Created user_utils.py with reusable role-checking functions (can_manage_tasks, can_access_tasks, get_assignable_users)
- **Searchable User Selection**: Implemented JavaScript-powered searchable dropdown for user assignment to handle hundreds of users efficiently
- **Universal Task Menu Access**: Made task menu ("Mina uppgifter") visible to users with parent, event_manager, or admin roles
- **Refactored Route Permissions**: Updated all task-related routes to use consistent role-based access control with requires_any_role decorator
- **Event Coordinator System**: Added coordinator_id field to events with relationship to User model for assigning event coordinators from event_manager or admin roles
- **Enhanced Event Management**: Event coordinators are visible to parents, event managers, and admins; form includes searchable coordinator selection dropdown
- **Updated Task Contact Information**: Changed all task-related contact text from "Kontakta skolan" to "Kontakta koordinator av evenemanget" for better event organization
- **Critical Bug Fixes**: Fixed permission decorator syntax errors (@requires_any_role) and Jinja2 template filtering issues that caused server crashes
- **Template Error Resolution**: Corrected selectattr/rejectattr filter usage in parent_tasks.html to prevent TypeError crashes
- **Comprehensive Test Suite**: Created test_app.py with SQLite-based testing framework covering models, routes, and critical functionality

**2025-08-08**:
- Implemented conditional admin navigation system with responsive design
- Added admin dropdown menu for desktop with all admin functions (manage events, manage applications, administrators, change password, logout)
- Added direct admin links for mobile devices to prevent dropdown conflicts
- Added login option to main navigation when not authenticated as admin
- Cleaned up redundant navigation links from individual admin pages for better user experience
- Enhanced template context processor to make current_user available across all templates

**2025-08-02**:
- Added date-conditional application reminder (visible only December 1st - January 15th) to both front page and application page
- Implemented dynamic school year calculation based on current date (second half of year shows next school year, first half shows current school year)
- Updated email confirmations to use dynamic school year
- Currently showing school year 2026/2027 (since today is August 2025)

**2025-07-30**: 
- Implemented Behold.so Instagram integration with fallback to sample data
- Fixed Facebook widget responsiveness with ultra-strong CSS rules and continuous JavaScript monitoring
- Added environment variable support for BEHOLD_FEED_ID
- Created responsive Instagram post display with hover effects and direct links to Instagram
- Resolved Instagram API authentication issues by using hybrid approach (API + fallback)
- Added comprehensive admin password management system with self-service password changes
- Created admin user management interface for creating new administrators  
- Implemented production-ready admin creation script (create_production_admin.py)
- Added database export tools for development to production migration
- Verified admin user creation and active/inactive status management working correctly
- Removed insecure temporary admin creation route for better security
- Migrated all WordPress images to local static files for better performance and independence

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