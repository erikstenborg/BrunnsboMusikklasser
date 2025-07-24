from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Message
from app import app, db, mail
from models import Event, Application, NewsPost, Contact
from forms import ApplicationForm, ContactForm
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

# Context processor to make current year available in all templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}
