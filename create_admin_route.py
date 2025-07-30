"""
Temporary route for creating admin users in production
Add this to your routes.py temporarily, then remove after use
"""

@app.route('/create-admin-temp', methods=['GET', 'POST'])
def create_admin_temp():
    """Temporary route for creating admin users in production - REMOVE AFTER USE"""
    
    # Security check - only allow this in production with a secret parameter
    secret = request.args.get('secret')
    if secret != 'brunnsbo-admin-setup-2025':
        return "Not authorized", 403
    
    if request.method == 'GET':
        return '''
        <form method="POST">
            <h2>Create Production Admin</h2>
            <p>Username: <input type="text" name="username" required></p>
            <p>Email: <input type="email" name="email" required></p>
            <p>Password: <input type="password" name="password" required minlength="8"></p>
            <p>Confirm Password: <input type="password" name="confirm_password" required></p>
            <p><input type="submit" value="Create Admin"></p>
        </form>
        '''
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([username, email, password, confirm_password]):
        return "All fields required", 400
        
    if password != confirm_password:
        return "Passwords don't match", 400
        
    if len(password) < 8:
        return "Password must be at least 8 characters", 400
    
    # Check if user exists
    existing_user = AdminUser.query.filter(
        (AdminUser.username == username) | (AdminUser.email == email)
    ).first()
    
    if existing_user:
        return f"User with username '{username}' or email '{email}' already exists", 400
    
    try:
        new_user = AdminUser()
        new_user.username = username
        new_user.email = email
        new_user.set_password(password)
        new_user.active = True
        
        db.session.add(new_user)
        db.session.commit()
        
        return f"Admin user '{username}' created successfully! Now DELETE this route from your code."
        
    except Exception as e:
        db.session.rollback()
        return f"Error: {str(e)}", 500