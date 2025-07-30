# Production Admin User Setup Instructions

## Creating Admin Users in Production

### Method 1: Using the Production Script (Recommended)

1. **In your production environment**, run the admin creation script:
```bash
python3 create_production_admin.py
```

2. **Follow the prompts:**
   - Enter username (minimum 3 characters)
   - Enter email address
   - Enter secure password (minimum 8 characters)
   - Confirm password

3. **The script will:**
   - Check for existing users
   - Create the admin user with encrypted password
   - Confirm successful creation

### Method 2: List Existing Admin Users

```bash
python3 create_production_admin.py list
```

This shows all current admin users and their status.

### Method 3: Using SQL (Advanced)

If you need to create an admin user directly via SQL:

```sql
-- Replace with your actual values
INSERT INTO admin_users (username, email, password_hash, active, created_at) 
VALUES ('yourusername', 'your@email.com', 'HASHED_PASSWORD', true, NOW());
```

**Note:** You'll need to generate the password hash using Werkzeug's `generate_password_hash()` function.

## Admin Password Management Features

Once logged in, admins can:

### Change Their Own Password
- Navigate to `/admin/change-password`
- Enter current password
- Set new password (minimum 8 characters)
- Confirm new password

### Create New Admin Users
- Navigate to `/admin/users`
- Click "Skapa ny administratör"
- Fill in username, email, and password
- Set active status

### View All Admin Users
- Navigate to `/admin/users`
- See list of all administrators
- View last login times and status

## Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Password Requirements**: Minimum 8 characters
- **Form Validation**: Client and server-side validation
- **Conflict Prevention**: Checks for duplicate usernames/emails
- **Session Management**: Secure login/logout handling

## Accessing Admin Panel

1. **Login URL**: `https://yoursite.com/admin/login`
2. **After login**: Redirected to event management dashboard
3. **Main admin features**:
   - Event management (create, edit, delete)
   - Admin user management
   - Password changes
   - Secure logout

## Database Migration Notes

- Admin users are stored in the `admin_users` table
- Password hashes are secure and cannot be reversed
- The system uses Flask-Login for session management
- All admin routes are protected with `@login_required` decorator