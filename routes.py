import os
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Message
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, mail
from models import Event, Application, NewsPost, Contact, AdminUser
from forms import ApplicationForm, ContactForm, LoginForm, EventForm, ChangePasswordForm, CreateAdminForm
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
    
    return render_template('index.html', 
                         upcoming_events=upcoming_events,
                         latest_news=latest_news)

@app.route('/om-oss')
def about():
    """About page with information about the school and teachers"""
    return render_template('om-oss.html')

@app.route('/ansokan', methods=['GET', 'POST'])
def application():
    """Application page for music classes"""
    form = ApplicationForm()
    
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
            new_application.application_year = "2025/2026"
            
            db.session.add(new_application)
            db.session.commit()
            
            # Send confirmation email
            try:
                msg = Message(
                    subject='Bekräftelse av ansökan till Brunnsbo Musikklasser',
                    recipients=[form.parent_email.data] if form.parent_email.data else [],
                    body=f"""
Tack för din ansökan till Brunnsbo Musikklasser!

Vi har mottagit ansökan för {form.student_name.data} till årskurs {form.grade_applying_for.data} för läsåret 2025/2026.

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
            
            flash('Din ansökan har skickats! Du kommer att få en bekräftelse via e-post.', 'success')
            return redirect(url_for('application'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving application: {str(e)}")
            flash('Ett fel uppstod när ansökan skulle skickas. Försök igen.', 'error')
    
    return render_template('ansokan.html', form=form)

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
        'behold_feed_id': os.environ.get('BEHOLD_FEED_ID', '')
    }

@app.route('/evenemang')
def events():
    """Page showing all upcoming events"""
    upcoming_events = Event.query.filter(
        Event.event_date > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.event_date.asc()).all()
    
    return render_template('evenemang.html', events=upcoming_events)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_events'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin_events')
            return redirect(next_page)
        else:
            flash('Felaktigt användarnamn eller lösenord.', 'error')
    
    return render_template('admin_login.html', form=form)

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Du har loggats ut.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/events')
@login_required
def admin_events():
    """Admin page for managing events"""
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin_events.html', events=events)

@app.route('/admin/events/new', methods=['GET', 'POST'])
@login_required
def admin_event_new():
    """Create new event"""
    form = EventForm()
    
    if form.validate_on_submit():
        try:
            new_event = Event()
            new_event.title = form.title.data
            new_event.description = form.description.data
            new_event.event_date = form.event_date.data
            new_event.location = form.location.data
            new_event.ticket_url = form.ticket_url.data
            new_event.is_active = form.is_active.data
            
            db.session.add(new_event)
            db.session.commit()
            
            flash('Eventet har skapats!', 'success')
            return redirect(url_for('admin_events'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating event: {str(e)}")
            flash('Ett fel uppstod när eventet skulle skapas.', 'error')
    
    return render_template('admin_event_form.html', form=form, title='Skapa nytt event')

@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
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
@login_required
def admin_create_user():
    """Create new admin user"""
    form = CreateAdminForm()
    
    if form.validate_on_submit():
        
        # Check if username or email already exists
        existing_user = AdminUser.query.filter(
            (AdminUser.username == form.username.data) | 
            (AdminUser.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Användarnamn eller e-postadress finns redan.', 'error')
        else:
            try:
                new_user = AdminUser()
                new_user.username = form.username.data
                new_user.email = form.email.data
                new_user.set_password(form.password.data)
                new_user.active = form.active.data
                
                db.session.add(new_user)
                db.session.commit()
                
                flash(f'Administratörsanvändare "{form.username.data}" har skapats!', 'success')
                return redirect(url_for('admin_users'))
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error creating admin user: {str(e)}")
                flash('Ett fel uppstod när användaren skulle skapas.', 'error')
    
    return render_template('admin_create_user.html', form=form)

@app.route('/admin/users')
@login_required
def admin_users():
    """List all admin users"""
    users = AdminUser.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def admin_event_edit(event_id):
    """Edit existing event"""
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        try:
            event.title = form.title.data
            event.description = form.description.data
            event.event_date = form.event_date.data
            event.location = form.location.data
            event.ticket_url = form.ticket_url.data
            event.is_active = form.is_active.data
            
            db.session.commit()
            
            flash('Eventet har uppdaterats!', 'success')
            return redirect(url_for('admin_events'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating event: {str(e)}")
            flash('Ett fel uppstod när eventet skulle uppdateras.', 'error')
    
    return render_template('admin_event_form.html', form=form, event=event, title='Redigera event')

@app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
@login_required
def admin_event_delete(event_id):
    """Delete event"""
    event = Event.query.get_or_404(event_id)
    
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Eventet har tagits bort!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting event: {str(e)}")
        flash('Ett fel uppstod när eventet skulle tas bort.', 'error')
    
    return redirect(url_for('admin_events'))
