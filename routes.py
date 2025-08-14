import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, mail
from models import Event, Application, NewsPost, Contact, User, Group, EventTask, ConfirmationCode
from forms import ApplicationForm, ContactForm, LoginForm, EventForm, ChangePasswordForm, CreateAdminForm, EditApplicationForm, CreateUserForm, EventTaskForm, ForgotPasswordForm, ResetPasswordForm, RegisterForm, VerifyEmailForm
from utils import create_confirmation_code, verify_confirmation_code, generate_confirmation_code
from permissions import (
    admin_required, applications_manager_required, event_manager_required, 
    parent_access_required, authenticated_required, requires_any_role
)
from user_utils import get_assignable_users, can_manage_tasks, can_access_tasks, get_user_choices_for_forms
from datetime import datetime, timedelta
import logging

@app.route('/')
def index():
    """Homepage with latest news and upcoming events"""
    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.event_date > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.event_date.asc()).limit(3).all()
    
    # Get latest news
    latest_news = NewsPost.query.filter(
        NewsPost.is_published == True
    ).order_by(NewsPost.published_date.desc()).limit(3).all()
    
    # Check if we're in application reminder period (Dec 1 - Jan 15)
    now = datetime.now()
    current_year = now.year
    
    # December 1st of current year
    dec_1_current = datetime(current_year, 12, 1)
    # January 15th of next year
    jan_15_next = datetime(current_year + 1, 1, 15, 23, 59, 59)
    
    # Also check if we're in Jan 1-15 of current year (from previous year's Dec)
    jan_15_current = datetime(current_year, 1, 15, 23, 59, 59)
    dec_1_previous = datetime(current_year - 1, 12, 1)
    
    show_application_reminder = (
        (dec_1_current <= now <= jan_15_next) or  # Dec 1 current year to Jan 15 next year
        (dec_1_previous <= now <= jan_15_current)  # Dec 1 previous year to Jan 15 current year
    )
    
    # Calculate dynamic school year for front page as well
    if now.month >= 7:  # July-December: next school year
        school_year = f"{current_year + 1}/{current_year + 2}"
    else:  # January-June: current school year
        school_year = f"{current_year}/{current_year + 1}"
    
    return render_template('index.html', 
                         upcoming_events=upcoming_events,
                         latest_news=latest_news,
                         show_application_reminder=show_application_reminder,
                         school_year=school_year)

@app.route('/om-oss')
def about():
    """About page with information about the school and teachers"""
    return render_template('om-oss.html')

@app.route('/ansokan', methods=['GET', 'POST'])
def application():
    """Application page for music classes"""
    form = ApplicationForm()
    
    # Check if we're in application reminder period (Dec 1 - Jan 15)
    now = datetime.now()
    current_year = now.year
    
    # December 1st of current year
    dec_1_current = datetime(current_year, 12, 1)
    # January 15th of next year
    jan_15_next = datetime(current_year + 1, 1, 15, 23, 59, 59)
    
    # Also check if we're in Jan 1-15 of current year (from previous year's Dec)
    jan_15_current = datetime(current_year, 1, 15, 23, 59, 59)
    dec_1_previous = datetime(current_year - 1, 12, 1)
    
    show_application_reminder = (
        (dec_1_current <= now <= jan_15_next) or  # Dec 1 current year to Jan 15 next year
        (dec_1_previous <= now <= jan_15_current)  # Dec 1 previous year to Jan 15 current year
    )
    
    # Calculate dynamic school year based on current date
    if now.month >= 7:  # July-December: next school year
        school_year = f"{current_year + 1}/{current_year + 2}"
        application_year = f"{current_year + 1}/{current_year + 2}"
    else:  # January-June: current school year
        school_year = f"{current_year}/{current_year + 1}"
        application_year = f"{current_year}/{current_year + 1}"
    
    if form.validate_on_submit():
        try:
            # Create new application
            new_application = Application()
            new_application.student_name = form.student_name.data
            new_application.student_personnummer = form.student_personnummer.data
            new_application.parent_name = form.parent_name.data
            new_application.parent_email = form.parent_email.data
            new_application.parent_phone = form.parent_phone.data
            new_application.address = form.address.data
            new_application.postal_code = form.postal_code.data
            new_application.city = form.city.data
            new_application.current_school = form.current_school.data
            new_application.musical_experience = form.musical_experience.data
            new_application.motivation = form.motivation.data
            new_application.grade_applying_for = form.grade_applying_for.data
            new_application.has_transportation = form.has_transportation.data
            new_application.additional_info = form.additional_info.data
            new_application.application_year = application_year
            
            db.session.add(new_application)
            db.session.commit()
            
            # Generate confirmation code
            confirmation = create_confirmation_code(
                email=form.parent_email.data,
                purpose='email_verification',
                expires_in_hours=24
            )
            
            # Send confirmation email with verification link
            try:
                confirmation_url = url_for('confirm_email', code=confirmation.code, _external=True)
                msg = Message(
                    subject='Bekräftelse av ansökan till Brunnsbo Musikklasser',
                    recipients=[form.parent_email.data] if form.parent_email.data else [],
                    body=f"""
Tack för din ansökan till Brunnsbo Musikklasser!

Vi har mottagit ansökan för {form.student_name.data} till årskurs {form.grade_applying_for.data} för läsåret {application_year}.

För att bekräfta din e-postadress, klicka på länken nedan:
{confirmation_url}

Denna länk är giltig i 24 timmar. Efter bekräftelse kommer din ansökan att behandlas.

Ansökan följs av provsjungningar där eleverna prövas individuellt avseende musikalitet, gehör, sångröst, rytmsinne och tonsäkerhet.

Vi återkommer med information om provsjungning.

Med vänliga hälsningar,
Brunnsbo Musikklasser

Kontakt: info@brunnsbomusikklasser.nu
Telefon: 031-366 86 50
                    """
                )
                mail.send(msg)
                logging.info(f"Confirmation email sent to {form.parent_email.data}")
            except Exception as e:
                logging.error(f"Failed to send confirmation email: {str(e)}")
            
            flash('Din ansökan har skickats! Kontrollera din e-post och klicka på bekräftelselänken för att slutföra processen.', 'success')
            return redirect(url_for('application'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving application: {str(e)}")
            flash('Ett fel uppstod när ansökan skulle skickas. Försök igen.', 'error')
    
    return render_template('ansokan.html', 
                         form=form,
                         show_application_reminder=show_application_reminder,
                         school_year=school_year)

@app.route('/confirm-email/<code>')
def confirm_email(code):
    """Handle email confirmation for applications"""
    try:
        # Find the confirmation by code only for email confirmation
        from models import ConfirmationCode
        confirmation = ConfirmationCode.query.filter_by(code=code, used=False).first()
        
        if confirmation and not confirmation.is_expired():
            confirmation.used = True
            confirmation.used_at = datetime.utcnow()
            db.session.commit()
        else:
            confirmation = None
        
        if not confirmation:
            flash('Ogiltig eller utgången bekräftelselänk.', 'error')
            return redirect(url_for('index'))
        
        # Find application by email and mark as confirmed
        application = Application.query.filter_by(
            parent_email=confirmation.email,
            email_confirmed=False
        ).order_by(Application.created_at.desc()).first()
        
        if application:
            application.email_confirmed = True
            application.email_confirmed_at = datetime.utcnow()
            db.session.commit()
            
            flash('Tack! Din e-postadress är nu bekräftad och ansökan kommer att behandlas.', 'success')
            logging.info(f"Email confirmed for application: {application.student_name} ({confirmation.email})")
        else:
            flash('Ingen ansökan hittades för denna e-postadress.', 'warning')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logging.error(f"Error confirming email: {str(e)}")
        flash('Ett fel uppstod vid bekräftelse av e-post.', 'error')
        return redirect(url_for('index'))

@app.route('/admin/applications')
@applications_manager_required
def admin_applications():
    """Admin page to view and manage applications"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    year_filter = request.args.get('year', 'all')
    
    # Build query with filters
    query = Application.query
    
    if status_filter != 'all':
        query = query.filter(Application.status == status_filter)
    
    if year_filter != 'all':
        query = query.filter(Application.application_year == year_filter)
    
    # Get applications with pagination
    applications = query.order_by(Application.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get unique years and status options for filters
    available_years = db.session.query(Application.application_year.distinct()).all()
    available_years = [year[0] for year in available_years]
    
    status_options = [
        ('applied', 'Ansökt'),
        ('application_withdrawn', 'Ansökan återkallad'),
        ('invited_for_audition', 'Inbjuden till provsjungning'),
        ('rejected', 'Avvisad'),
        ('offered', 'Erbjuden plats'),
        ('accepted', 'Antagen')
    ]
    
    return render_template('admin_applications.html', 
                         applications=applications,
                         status_filter=status_filter,
                         year_filter=year_filter,
                         available_years=available_years,
                         status_options=status_options)

@app.route('/admin/applications/<int:application_id>', methods=['GET', 'POST'])
@applications_manager_required
def admin_edit_application(application_id):
    """Edit specific application"""
    application = Application.query.get_or_404(application_id)
    form = EditApplicationForm()
    
    if form.validate_on_submit():
        # Update application
        application.status = form.status.data
        application.email_confirmed = form.email_confirmed.data
        application.admin_notes = form.admin_notes.data
        application.application_year = form.application_year.data
        
        # If status changed to email_confirmed, update timestamp
        if form.status.data == 'email_confirmed' and not application.email_confirmed_at:
            application.email_confirmed_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Ansökan har uppdaterats!', 'success')
            logging.info(f"Application {application_id} updated by admin {current_user.username}")
            return redirect(url_for('admin_applications'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating application: {str(e)}")
            flash('Ett fel uppstod när ansökan skulle uppdateras.', 'error')
    
    # Pre-populate form with existing data
    form.status.data = application.status
    form.email_confirmed.data = application.email_confirmed
    form.admin_notes.data = application.admin_notes
    form.application_year.data = application.application_year
    
    return render_template('admin_edit_application.html', 
                         form=form,
                         application=application)

@app.route('/kontakt', methods=['GET', 'POST'])
def contact():
    """Contact page with form"""
    form = ContactForm()
    
    if form.validate_on_submit():
        try:
            # Save contact form submission
            new_contact = Contact()
            new_contact.name = form.name.data
            new_contact.email = form.email.data
            new_contact.phone = form.phone.data
            new_contact.subject = form.subject.data
            new_contact.message = form.message.data
            
            db.session.add(new_contact)
            db.session.commit()
            
            # Send notification email to school
            try:
                msg = Message(
                    subject=f'Nytt meddelande från hemsidan: {form.subject.data}',
                    recipients=['info@brunnsbomusikklasser.nu'],
                    body=f"""
Nytt meddelande från hemsidan:

Namn: {form.name.data}
E-post: {form.email.data}
Telefon: {form.phone.data or 'Ej angivet'}
Ämne: {form.subject.data}

Meddelande:
{form.message.data}

Skickat: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    """
                )
                mail.send(msg)
                logging.info(f"Contact form notification sent for {form.name.data}")
            except Exception as e:
                logging.error(f"Failed to send contact notification: {str(e)}")
            
            flash('Tack för ditt meddelande! Vi återkommer så snart som möjligt.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving contact form: {str(e)}")
            flash('Ett fel uppstod när meddelandet skulle skickas. Försök igen.', 'error')
    
    return render_template('kontakt.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Context processor to make current year and datetime available in all templates
@app.context_processor
def inject_current_year():
    return {
        'current_year': datetime.now().year,
        'moment': lambda: datetime,
        'behold_feed_id': os.environ.get('BEHOLD_FEED_ID', ''),
        'current_user': current_user
    }

@app.route('/evenemang')
def events():
    """Page showing all upcoming events with parent/admin info when logged in"""
    upcoming_events = Event.query.filter(
        Event.event_date > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.event_date.asc()).all()
    
    # Check if user has parent access or admin access for enhanced event information
    show_parent_info = False
    show_admin_info = False
    
    if current_user.is_authenticated:
        # Use same role check as task management
        from user_utils import can_access_tasks, can_manage_tasks
        show_parent_info = can_access_tasks(current_user)  # parent, event_manager, or admin
        show_admin_info = can_manage_tasks(current_user)   # event_manager or admin
    
    return render_template('evenemang.html', 
                         events=upcoming_events,
                         show_parent_info=show_parent_info,
                         show_admin_info=show_admin_info)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        # If already logged in, redirect to homepage unless they have a specific next page
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')  # Default to homepage instead of admin page
            return redirect(next_page)
        else:
            flash('Felaktig e-postadress eller lösenord.', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
@authenticated_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Du har loggats ut.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/events')
@event_manager_required
def admin_events():
    """Admin page for managing events"""
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin_events.html', events=events)

# User management routes
@app.route('/admin/users/<int:user_id>/roles', methods=['GET', 'POST'])
@admin_required
def admin_user_roles(user_id):
    """Manage user roles"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get selected roles from form
        selected_roles = request.form.getlist('roles')
        
        # Clear current roles
        user.groups.clear()
        
        # Add selected roles
        for role_name in selected_roles:
            group = Group.query.filter_by(name=role_name).first()
            if group:
                user.groups.append(group)
        
        db.session.commit()
        flash(f'Roller uppdaterade för {user.username}', 'success')
        return redirect(url_for('admin_users'))
    
    # Get all available groups
    all_groups = Group.query.all()
    user_groups = [group.name for group in user.groups]
    
    return render_template('admin_user_roles.html', 
                         user=user, 
                         all_groups=all_groups,
                         user_groups=user_groups)

@app.route('/profile')
@authenticated_required
def user_profile():
    """User profile page for all authenticated users"""
    return render_template('user_profile.html')

# Remove the separate parent info route since we integrated it into the main events page

@app.route('/events/<int:event_id>/tasks')
@requires_any_role('parent', 'event_manager', 'admin')
def event_tasks(event_id):
    """View and manage tasks for a specific event"""
    event = Event.query.get_or_404(event_id)
    tasks = EventTask.query.filter_by(event_id=event_id).all()
    
    return render_template('event_tasks.html', event=event, tasks=tasks)

@app.route('/events/<int:event_id>/tasks/<int:task_id>/complete', methods=['POST'])
@requires_any_role('parent', 'event_manager', 'admin')
def complete_task(event_id, task_id):
    """Mark a task as completed"""
    task = EventTask.query.get_or_404(task_id)
    
    if not task.completed:
        task.completed = True
        task.completed_at = datetime.utcnow()
        task.completed_by_user_id = current_user.id
        db.session.commit()
        flash('Uppgift markerad som slutförd!', 'success')
    
    return redirect(url_for('event_tasks', event_id=event_id))

# Task management routes for event managers
@app.route('/admin/events/<int:event_id>/tasks/new', methods=['GET', 'POST'])
@requires_any_role('event_manager', 'admin')
def admin_create_task(event_id):
    """Create new task for an event"""
    event = Event.query.get_or_404(event_id)
    form = EventTaskForm()
    
    # Populate user choices for assignment
    form.assigned_to_user_id.choices = get_user_choices_for_forms()
    
    if form.validate_on_submit():
        try:
            task = EventTask()
            task.event_id = event_id
            task.title = form.title.data
            task.description = form.description.data
            if form.assigned_to_user_id.data:
                task.assigned_to_user_id = form.assigned_to_user_id.data
            # Set due date offset if provided
            if form.due_offset_days.data is not None:
                task.due_offset_days = form.due_offset_days.data
                task.due_offset_hours = form.due_offset_hours.data or 0
            
            db.session.add(task)
            db.session.commit()
            
            flash('Uppgift skapad!', 'success')
            return redirect(url_for('admin_event_tasks', event_id=event_id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating task: {str(e)}")
            flash('Ett fel uppstod när uppgiften skulle skapas.', 'error')
    
    return render_template('admin_task_form.html', form=form, event=event, title='Skapa uppgift')

@app.route('/admin/events/<int:event_id>/tasks')
@requires_any_role('event_manager', 'admin')
def admin_event_tasks(event_id):
    """Manage tasks for a specific event"""
    event = Event.query.get_or_404(event_id)
    tasks = EventTask.query.filter_by(event_id=event_id).all()
    
    # Get all assignable users for reassignment dropdown
    assignable_users = get_assignable_users()
    
    return render_template('admin_event_tasks.html', event=event, tasks=tasks, assignable_users=assignable_users)

@app.route('/admin/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@requires_any_role('event_manager', 'admin')
def admin_edit_task(task_id):
    """Edit an existing task"""
    task = EventTask.query.get_or_404(task_id)
    event = task.event
    form = EventTaskForm(obj=task)
    
    # Populate user choices for assignment
    form.assigned_to_user_id.choices = get_user_choices_for_forms()
    
    # Set current assignment if exists
    if task.assigned_to_user_id:
        form.assigned_to_user_id.data = str(task.assigned_to_user_id)
    
    # Pre-populate due date offset fields
    form.due_offset_days.data = task.due_offset_days
    form.due_offset_hours.data = task.due_offset_hours
    
    if form.validate_on_submit():
        try:
            task.title = form.title.data
            task.description = form.description.data
            if form.assigned_to_user_id.data:
                task.assigned_to_user_id = form.assigned_to_user_id.data
            else:
                task.assigned_to_user_id = None
            # Update due date offset
            task.due_offset_days = form.due_offset_days.data
            task.due_offset_hours = form.due_offset_hours.data or 0
            
            db.session.commit()
            
            flash('Uppgift uppdaterad!', 'success')
            return redirect(url_for('admin_event_tasks', event_id=event.id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating task: {str(e)}")
            flash('Ett fel uppstod när uppgiften skulle uppdateras.', 'error')
    
    return render_template('admin_task_form.html', form=form, event=event, task=task, title='Redigera uppgift')

@app.route('/admin/tasks/<int:task_id>/delete', methods=['POST'])
@requires_any_role('event_manager', 'admin')
def admin_delete_task(task_id):
    """Delete a task"""
    task = EventTask.query.get_or_404(task_id)
    event_id = task.event_id
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Uppgift borttagen!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting task: {str(e)}")
        flash('Ett fel uppstod när uppgiften skulle tas bort.', 'error')
    
    return redirect(url_for('admin_event_tasks', event_id=event_id))

@app.route('/user/tasks')
@requires_any_role('parent', 'event_manager', 'admin')
def user_tasks():
    """Personal task management page for parents"""
    # Get all tasks assigned to the current user
    tasks = EventTask.query.filter_by(assigned_to_user_id=current_user.id).all()
    
    return render_template('parent_tasks.html', tasks=tasks)

@app.route('/user/tasks/<int:task_id>/complete', methods=['POST'])
@requires_any_role('parent', 'event_manager', 'admin')
def complete_user_task(task_id):
    """Allow parents to complete their assigned tasks"""
    task = EventTask.query.get_or_404(task_id)
    
    # Verify the task is assigned to the current user
    if task.assigned_to_user_id != current_user.id:
        flash('Du kan endast slutföra uppgifter som är tilldelade till dig.', 'error')
        return redirect(url_for('user_tasks'))
    
    # Check if already completed
    if task.completed_at:
        flash('Denna uppgift är redan slutförd.', 'info')
        return redirect(url_for('user_tasks'))
    
    try:
        task.completed_at = datetime.utcnow()
        task.completed_by_id = current_user.id
        db.session.commit()
        
        flash(f'Uppgift "{task.title}" markerad som slutförd!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error completing task: {str(e)}")
        flash('Ett fel uppstod när uppgiften skulle slutföras.', 'error')
    
    return redirect(url_for('user_tasks'))

@app.route('/admin/tasks/<int:task_id>/reassign', methods=['POST'])
@requires_any_role('event_manager', 'admin')
def admin_reassign_task(task_id):
    """Reassign a task to a different user"""
    task = EventTask.query.get_or_404(task_id)
    new_assignee_id = request.form.get('new_assignee')
    
    if not new_assignee_id:
        flash('Ingen användare vald för omtilldelning.', 'error')
        return redirect(url_for('admin_event_tasks', event_id=task.event_id))
    
    # Verify the new assignee exists and can be assigned tasks
    new_assignee = User.query.get(new_assignee_id)
    if not new_assignee:
        flash('Användaren kunde inte hittas.', 'error')
        return redirect(url_for('admin_event_tasks', event_id=task.event_id))
    
    # Check if the new assignee can access tasks (parent, event_manager, or admin)
    if not can_access_tasks(new_assignee):
        flash('Uppgifter kan endast tilldelas föräldrar, eventansvariga eller administratörer.', 'error')
        return redirect(url_for('admin_event_tasks', event_id=task.event_id))
    
    try:
        old_assignee = task.assigned_to_user.first_name + ' ' + task.assigned_to_user.last_name if task.assigned_to_user else 'Ingen'
        task.assigned_to_user_id = new_assignee_id
        
        # Reset completion status if task was completed
        if task.completed_at:
            task.completed_at = None
            task.completed_by_id = None
        
        db.session.commit()
        
        new_assignee_name = new_assignee.first_name + ' ' + new_assignee.last_name
        flash(f'Uppgift "{task.title}" omtilldelad från {old_assignee} till {new_assignee_name}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error reassigning task: {str(e)}")
        flash('Ett fel uppstod när uppgiften skulle omtilldelas.', 'error')
    
    return redirect(url_for('admin_event_tasks', event_id=task.event_id))

@app.route('/admin/tasks/<int:task_id>/toggle-complete', methods=['POST'])
@requires_any_role('event_manager', 'admin')
def admin_toggle_task_completion(task_id):
    """Toggle task completion status for event managers"""
    task = EventTask.query.get_or_404(task_id)
    
    try:
        if task.completed_at:
            # Mark as incomplete
            task.completed_at = None
            task.completed_by_id = None
            flash(f'Uppgift "{task.title}" markerad som ofullständig.', 'info')
        else:
            # Mark as complete
            task.completed_at = datetime.utcnow()
            task.completed_by_id = current_user.id
            flash(f'Uppgift "{task.title}" markerad som slutförd.', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error toggling task completion: {str(e)}")
        flash('Ett fel uppstod när uppgiftens status skulle ändras.', 'error')
    
    return redirect(url_for('admin_event_tasks', event_id=task.event_id))

# Password reset routes
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset via email"""
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Create confirmation code
            confirmation_obj = create_confirmation_code(user.email, 'password_reset', 1)  # 1 hour expiry
            confirmation_code = confirmation_obj.code
            
            try:
                # Send reset email
                msg = Message(
                    'Återställ ditt lösenord - Brunnsbo Musikklasser',
                    recipients=[user.email]
                )
                reset_url = url_for('reset_password', email=user.email, code=confirmation_code, _external=True)
                msg.html = f"""
                <h2>Återställ ditt lösenord</h2>
                <p>Du har begärt att återställa ditt lösenord för ditt konto hos Brunnsbo Musikklasser.</p>
                <p><strong>Din bekräftelsekod är: {confirmation_code}</strong></p>
                <p>Använd denna kod på återställningssidan för att återställa ditt lösenord. Koden är giltig i 1 timme.</p>
                <p><a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">Återställ lösenord</a></p>
                <p>Om länken inte fungerar, kopiera och klistra in koden ovan direkt i återställningsformuläret.</p>
                <p>Om du inte begärde denna återställning kan du ignorera detta meddelande.</p>
                <hr>
                <p><em>Brunnsbo Musikklasser</em></p>
                """
                
                mail.send(msg)
                flash('En bekräftelsekod har skickats till din e-postadress.', 'info')
                return redirect(url_for('reset_password', email=user.email))
                
            except Exception as e:
                logging.error(f"Error sending password reset email: {str(e)}")
                flash('Ett fel uppstod vid skickning av e-post. Försök igen.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('En bekräftelsekod har skickats till din e-postadress om kontot finns.', 'info')
            return redirect(url_for('reset_password', email=form.email.data))
    
    return render_template('forgot_password.html', form=form)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password with confirmation code"""
    form = ResetPasswordForm()
    
    # Pre-populate email and code if provided as parameters
    email_param = request.args.get('email')
    code_param = request.args.get('code')
    if email_param and not form.email.data:
        form.email.data = email_param
    if code_param and not form.confirmation_code.data:
        form.confirmation_code.data = code_param
    
    if form.validate_on_submit():
        # Verify confirmation code
        if verify_confirmation_code(form.email.data, form.confirmation_code.data, 'password_reset'):
            user = User.query.filter_by(email=form.email.data).first()
            
            if user:
                user.set_password(form.new_password.data)
                db.session.commit()
                
                flash('Ditt lösenord har återställts. Du kan nu logga in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Användaren hittades inte.', 'error')
        else:
            flash('Ogiltig eller utgången bekräftelsekod.', 'error')
    
    return render_template('reset_password.html', form=form)

# Registration routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email verification"""
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('E-postadressen är redan registrerad.', 'error')
        else:
            try:
                # Create confirmation code for email verification
                confirmation_code = create_confirmation_code(form.email.data, 'user_registration')
                
                # Create user account immediately but mark as inactive until email verified
                new_user = User()
                new_user.first_name = form.first_name.data
                new_user.last_name = form.last_name.data
                new_user.email = form.email.data
                new_user.set_password(form.password.data)
                new_user.active = False  # Inactive until email verified
                # Note: User model doesn't have email_verified field, using active status instead
                
                db.session.add(new_user)
                db.session.commit()
                
                # Store minimal data in session for verification process
                session['pending_registration'] = {
                    'email': form.email.data,
                    'user_id': new_user.id
                }
                
                # Send verification email  
                msg = Message(
                    'Bekräfta din registrering - Brunnsbo Musikklasser',
                    recipients=[form.email.data]
                )
                msg.html = f"""
                <h2>Välkommen till Brunnsbo Musikklasser!</h2>
                <p>Tack för att du vill registrera ett konto hos oss.</p>
                <p><strong>Din bekräftelsekod är: {confirmation_code.code}</strong></p>
                <p>Använd denna kod för att slutföra din registrering. Koden är giltig i 1 timme.</p>
                <p><a href="{url_for('verify_email', email=form.email.data, code=confirmation_code.code, _external=True)}" style="display: inline-block; padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Slutför registrering</a></p>
                <p>Om länken inte fungerar, kopiera och klistra in koden ovan i registreringsformuläret.</p>
                <p>Efter verifiering kan du logga in, men du behöver vänta på att en administratör tilldelar dig behörigheter.</p>
                <hr>
                <p><em>Brunnsbo Musikklasser</em></p>
                """
                
                mail.send(msg)
                flash('En bekräftelsekod har skickats till din e-postadress.', 'info')
                return redirect(url_for('verify_email'))
                
            except Exception as e:
                logging.error(f"Error sending registration email: {str(e)}")
                flash('Ett fel uppstod vid registreringen. Försök igen.', 'error')
    
    return render_template('register.html', form=form)

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Verify email and complete registration"""
    # Check if coming from direct link with parameters
    email_param = request.args.get('email')
    code_param = request.args.get('code')
    
    # Handle direct links - find user by email parameter or session
    form = VerifyEmailForm()
    
    if email_param and code_param:
        # Direct link - check if user exists and is inactive
        user = User.query.filter_by(email=email_param, active=False).first()
        if user:
            form.email.data = email_param
            session['pending_registration'] = {
                'email': email_param,
                'user_id': user.id
            }
        else:
            flash('Ogiltig registreringslänk eller användare hittades inte.', 'error')
            return redirect(url_for('register'))
    elif 'pending_registration' in session:
        form.email.data = session['pending_registration']['email']
    else:
        flash('Ingen väntande registrering hittades. Vänligen registrera dig igen.', 'error')
        return redirect(url_for('register'))
    
    # Pre-populate code from URL parameters
    if code_param and not form.confirmation_code.data:
        form.confirmation_code.data = code_param
    
    if form.validate_on_submit():
        # Verify the confirmation code first
        confirmation = verify_confirmation_code(form.email.data, form.confirmation_code.data, 'user_registration')
        
        if confirmation:
            try:
                # Find the user account that was created during registration
                user = User.query.filter_by(email=form.email.data, active=False).first()
                
                if user:
                    # Activate the user account and mark email as verified
                    user.active = True
                    # Note: User model uses active status for email verification
                    
                    db.session.commit()
                    
                    # Clear the pending registration
                    session.pop('pending_registration', None)
                    
                    flash('Registrering slutförd! Du kan nu logga in. En administratör kommer att tilldela dig behörigheter inom kort.', 'success')
                    return redirect(url_for('login'))
                else:
                    # Handle case where user account doesn't exist (shouldn't happen)
                    flash('Användarkonot hittades inte. Vänligen registrera dig igen.', 'error')
                    return redirect(url_for('register'))
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error activating user account: {str(e)}")
                flash('Ett fel uppstod vid aktivering av kontot.', 'error')
        else:
            flash('Ogiltig eller utgången bekräftelsekod.', 'error')
    
    return render_template('verify_email.html', form=form)

@app.route('/admin/events/new', methods=['GET', 'POST'])
@event_manager_required
def admin_event_new():
    """Create new event"""
    form = EventForm()
    
    # Populate coordinator choices
    from user_utils import get_event_manager_choices
    form.coordinator_id.choices = get_event_manager_choices()
    
    if form.validate_on_submit():
        try:
            new_event = Event()
            new_event.title = form.title.data
            new_event.description = form.description.data
            new_event.event_date = form.event_date.data
            new_event.location = form.location.data
            new_event.ticket_url = form.ticket_url.data
            new_event.is_active = form.is_active.data
            new_event.info_to_parents = form.info_to_parents.data
            if form.coordinator_id.data and form.coordinator_id.data != 0:
                new_event.coordinator_id = form.coordinator_id.data
            
            db.session.add(new_event)
            db.session.commit()
            
            flash('Evenemanget har skapats!', 'success')
            return redirect(url_for('admin_events'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating event: {str(e)}")
            flash('Ett fel uppstod när evenemanget skulle skapas.', 'error')
    
    return render_template('admin_event_form.html', form=form, title='Skapa nytt evenemang')

@app.route('/admin/change-password', methods=['GET', 'POST'])
@authenticated_required
def admin_change_password():
    """Change admin password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Lösenordet har ändrats!', 'success')
            return redirect(url_for('admin_events'))
        else:
            flash('Nuvarande lösenord är felaktigt.', 'error')
    
    return render_template('admin_change_password.html', form=form)

@app.route('/admin/create-user', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    """Create new user"""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('E-postadress finns redan.', 'error')
        else:
            try:
                new_user = User()
                new_user.first_name = form.first_name.data
                new_user.last_name = form.last_name.data
                new_user.email = form.email.data
                new_user.set_password(form.password.data)
                new_user.active = form.active.data
                
                db.session.add(new_user)
                db.session.commit()
                
                flash(f'Användare "{form.first_name.data} {form.last_name.data}" har skapats!', 'success')
                return redirect(url_for('admin_users'))
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error creating admin user: {str(e)}")
                flash('Ett fel uppstod när användaren skulle skapas.', 'error')
    
    return render_template('admin_create_user.html', form=form)

@app.route('/admin/users')
@admin_required
def admin_users():
    """List all admin users"""
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/events/edit/<int:event_id>', methods=['GET', 'POST'])
@event_manager_required
def admin_event_edit(event_id):
    """Edit existing event"""
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    # Populate coordinator choices
    from user_utils import get_event_manager_choices
    form.coordinator_id.choices = get_event_manager_choices()
    
    # Set current coordinator if exists
    if event.coordinator_id:
        form.coordinator_id.data = event.coordinator_id
    
    if form.validate_on_submit():
        try:
            event.title = form.title.data
            event.description = form.description.data
            event.event_date = form.event_date.data
            event.location = form.location.data
            event.ticket_url = form.ticket_url.data
            event.is_active = form.is_active.data
            event.info_to_parents = form.info_to_parents.data
            if form.coordinator_id.data and form.coordinator_id.data != 0:
                event.coordinator_id = form.coordinator_id.data
            else:
                event.coordinator_id = None
            
            db.session.commit()
            
            flash('Evenemanget har uppdaterats!', 'success')
            return redirect(url_for('admin_events'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating event: {str(e)}")
            flash('Ett fel uppstod när evenemanget skulle uppdateras.', 'error')
    
    return render_template('admin_event_form.html', form=form, event=event, title='Redigera evenemang')

@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@event_manager_required
def admin_event_delete(event_id):
    """Delete event"""
    event = Event.query.get_or_404(event_id)
    
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Evenemanget har tagits bort!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting event: {str(e)}")
        flash('Ett fel uppstod när evenemanget skulle tas bort.', 'error')
    
    return redirect(url_for('admin_events'))
