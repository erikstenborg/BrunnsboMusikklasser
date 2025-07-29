from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, EmailField, TelField, PasswordField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length, Regexp, URL, Optional

class ApplicationForm(FlaskForm):
    """Form for student applications to music classes"""
    
    # Student information
    student_name = StringField('Elevens namn', validators=[
        DataRequired(message='Elevens namn är obligatoriskt'),
        Length(min=2, max=100, message='Namnet måste vara mellan 2 och 100 tecken')
    ])
    
    student_personnummer = StringField('Elevens personnummer (YYYYMMDD-XXXX)', validators=[
        DataRequired(message='Personnummer är obligatoriskt'),
        Regexp(r'^\d{8}-\d{4}$', message='Ange personnummer i formatet YYYYMMDD-XXXX')
    ])
    
    # Parent/Guardian information
    parent_name = StringField('Vårdnadshavares namn', validators=[
        DataRequired(message='Vårdnadshavares namn är obligatoriskt'),
        Length(min=2, max=100, message='Namnet måste vara mellan 2 och 100 tecken')
    ])
    
    parent_email = EmailField('E-postadress', validators=[
        DataRequired(message='E-postadress är obligatorisk'),
        Email(message='Ange en giltig e-postadress')
    ])
    
    parent_phone = TelField('Telefonnummer', validators=[
        DataRequired(message='Telefonnummer är obligatoriskt'),
        Length(min=10, max=20, message='Ange ett giltigt telefonnummer')
    ])
    
    # Address information
    address = StringField('Adress', validators=[
        DataRequired(message='Adress är obligatorisk'),
        Length(max=200)
    ])
    
    postal_code = StringField('Postnummer', validators=[
        DataRequired(message='Postnummer är obligatoriskt'),
        Regexp(r'^\d{3}\s?\d{2}$', message='Ange postnummer i format XXX XX')
    ])
    
    city = StringField('Ort', validators=[
        DataRequired(message='Ort är obligatorisk'),
        Length(max=50)
    ])
    
    # School information
    current_school = StringField('Nuvarande skola', validators=[
        Length(max=100)
    ])
    
    grade_applying_for = SelectField('Årskurs som du söker till', choices=[
        ('4', 'Årskurs 4'),
        ('5', 'Årskurs 5'),
        ('6', 'Årskurs 6'),
        ('7', 'Årskurs 7'),
        ('8', 'Årskurs 8'),
        ('9', 'Årskurs 9')
    ], validators=[DataRequired(message='Välj årskurs')])
    
    # Musical background
    musical_experience = TextAreaField('Berätta om elevens musikbakgrund och tidigare erfarenheter', validators=[
        Length(max=1000, message='Texten får vara max 1000 tecken')
    ])
    
    motivation = TextAreaField('Varför vill eleven gå i musikklass?', validators=[
        DataRequired(message='Motivation är obligatorisk'),
        Length(min=50, max=1000, message='Motivationen måste vara mellan 50 och 1000 tecken')
    ])
    
    # Practical information
    has_transportation = BooleanField('Eleven har möjlighet att ta sig till och från skolan')
    
    additional_info = TextAreaField('Övrig information', validators=[
        Length(max=500, message='Texten får vara max 500 tecken')
    ])

class ContactForm(FlaskForm):
    """Form for general contact inquiries"""
    
    name = StringField('Namn', validators=[
        DataRequired(message='Namn är obligatoriskt'),
        Length(min=2, max=100)
    ])
    
    email = EmailField('E-postadress', validators=[
        DataRequired(message='E-postadress är obligatorisk'),
        Email(message='Ange en giltig e-postadress')
    ])
    
    phone = TelField('Telefonnummer (valfritt)', validators=[
        Length(max=20)
    ])
    
    subject = StringField('Ämne', validators=[
        DataRequired(message='Ämne är obligatoriskt'),
        Length(min=5, max=200)
    ])
    
    message = TextAreaField('Meddelande', validators=[
        DataRequired(message='Meddelande är obligatoriskt'),
        Length(min=20, max=2000, message='Meddelandet måste vara mellan 20 och 2000 tecken')
    ])

class LoginForm(FlaskForm):
    """Form for admin login"""
    
    username = StringField('Användarnamn', validators=[
        DataRequired(message='Användarnamn är obligatoriskt'),
        Length(min=3, max=64)
    ])
    
    password = PasswordField('Lösenord', validators=[
        DataRequired(message='Lösenord är obligatoriskt')
    ])

class EventForm(FlaskForm):
    """Form for creating and editing events"""
    
    title = StringField('Eventtitel', validators=[
        DataRequired(message='Titel är obligatorisk'),
        Length(min=5, max=200, message='Titeln måste vara mellan 5 och 200 tecken')
    ])
    
    description = TextAreaField('Beskrivning', validators=[
        Length(max=2000, message='Beskrivningen får vara max 2000 tecken')
    ])
    
    event_date = DateTimeLocalField('Datum och tid', validators=[
        DataRequired(message='Datum och tid är obligatoriskt')
    ], format='%Y-%m-%dT%H:%M')
    
    location = StringField('Plats', validators=[
        Length(max=200, message='Platsen får vara max 200 tecken')
    ])
    
    ticket_url = StringField('Länk för biljetter (valfritt)', validators=[
        Optional(),
        URL(message='Ange en giltig URL')
    ])
    
    is_active = BooleanField('Aktivt event', default=True)
