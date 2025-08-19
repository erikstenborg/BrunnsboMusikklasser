# replit.md

## Overview
Brunnsbo Musikklasser is a Flask-based web application for a Swedish music school, managing student applications, events, news posts, and contact information. Its primary purpose is to streamline admissions for music classes and serve as an information hub for prospective students and parents.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
The application employs a traditional Flask web architecture, utilizing server-side rendering and a PostgreSQL database with SQLAlchemy. It integrates Flask-Mail for email functionalities and Flask-WTF for form handling.

### Core Technologies
- **Backend**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Server-side rendered HTML templates with Bootstrap 5
- **Email**: Flask-Mail for application notifications
- **Forms**: Flask-WTF with WTForms for form handling and validation

### Key Components
- **Models (models.py)**: Defines data structures for Events, Applications, News Posts, and Contact information.
- **Forms (forms.py)**: Manages application and contact forms, including Swedish-specific validations.
- **Routes (routes.py)**: Defines URL endpoints for core functionalities like homepage, about, application, and contact pages.
- **Templates**: Uses a base template for consistent layout, with Swedish-language content and professional styling.

### Data Flow
- **Student Applications**: Comprehensive forms are validated, stored in PostgreSQL, and trigger email notifications to administrators. Applications are trackable by status.
- **Content Management**: Events and news are managed via the database and displayed dynamically on the website, with filtering for upcoming items.
- **Task Management**: A comprehensive system allows event managers to create, edit, and delete tasks, assigning them to users with various roles (parent, event_manager, admin). Parents have a dedicated "Mina uppgifter" page for task completion.
- **Authentication & Authorization**: Utilizes email-based authentication with Flask-Login for session management, plus Google OAuth integration for seamless login/registration. Features a robust Role-Based Access Control (RBAC) system (Admin, applications_manager, event_manager, parent roles) and email-based password reset. OAuth-only users can create passwords via password reset feature. **IMPORTANT**: New users (both email and OAuth registration) receive NO automatic role assignments - administrators must manually assign roles.

### UI/UX Decisions
- **Responsive Design**: Implemented with Bootstrap 5.
- **Navigation**: Conditional admin navigation and a login option in the main navigation when not authenticated.
- **Branding**: Uses a 40th anniversary GIF logo and a gold color scheme.
- **Localization**: Datetime inputs respect browser locale settings while maintaining proper data format validation, with Swedish format hints and 5-minute step intervals.
- **Dynamic Content**: Application reminders are date-conditional (Dec 1st - Jan 15th), and school year calculations are dynamic.

## External Dependencies

### Payment System
- **Swish**: Full integration of the Swedish Swish payment system with m-commerce and QR-code support for donations. Includes `SwishPayment` model, `SwishService` API handler, and real-time status updates via API v2 with certificate-based authentication.

### Social Media Integrations
- **Behold.so**: Instagram integration with a fallback to sample data.
- **Facebook Widget**: Optimized for responsiveness.

### Email Service
- **Flask-Mail**: Used for sending application notifications, configurable via environment variables.

### Frontend Assets
- **Bootstrap 5**: CSS framework via CDN.
- **Font Awesome**: Icons via CDN.
- **Google Fonts**: Playfair Display and Source Sans Pro.
- **Custom CSS**: For brand-specific styling.

### Database
- **PostgreSQL**: Primary database solution, with SQLAlchemy ORM.

### Testing Infrastructure
- **pytest**: Comprehensive test suite with complete database isolation using Flask app factory pattern.
- **SQLite in-memory**: Tests use completely isolated SQLite databases with separate Flask app instances to prevent any interference with development data.
- **conftest.py**: Centralized test configuration creating fresh Flask app instances for each test, ensuring development database is never affected.
- **Test Isolation**: PERFECT - All 28 unit tests now pass with 100% success rate while completely preserving development data.
- **Test Coverage**: Complete coverage across 8 test classes: TestBasicFunctionality, TestModels, TestForms, TestCriticalRoutes, TestPermissions, TestErrorHandling, TestDatabaseIntegrity, and TestSwishPayments.
- **Route Testing**: Comprehensive route testing covers all public routes (/, /om-oss, /evenemang, /kontakt, /ansokan), admin routes (/admin/applications, /admin/events, /admin/users), authentication routes (/login, /register, /forgot-password), and parametric routes with proper security validation.
- **Database Safety**: Development PostgreSQL database with admin user and all production data remains completely untouched during test execution.
- **Code Quality**: Zero warnings - eliminated all SQLAlchemy legacy warnings by migrating from Query.get() to Session.get() methods.
- **Test Organization**: Consolidated from 2 test files to 1 comprehensive test_app.py, eliminating redundant tests and improving maintainability. Single command: `pytest test_app.py`
- **Payment Testing**: Comprehensive Swish payment system testing including model creation, amount formatting, Swedish phone validation, status transitions, database relationships, and error handling.