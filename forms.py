from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, EmailField, TelField, PasswordField, DateTimeLocalField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, URL, Optional, EqualTo, NumberRange


class ApplicationForm(FlaskForm):
    """Form for student applications to music classes"""

    # Student information
    student_name = StringField(
        'Elevens namn',
        validators=[
            DataRequired(message='Elevens namn är obligatoriskt'),
            Length(min=2,
                   max=100,
                   message='Namnet måste vara mellan 2 och 100 tecken')
        ])

    student_personnummer = StringField(
        'Elevens personnummer (YYYYMMDD-XXXX)',
        validators=[
            DataRequired(message='Personnummer är obligatoriskt'),
            Regexp(r'^\d{8}-\d{4}$',
                   message='Ange personnummer i formatet YYYYMMDD-XXXX')
        ])

    # Parent/Guardian information
    parent_name = StringField(
        'Vårdnadshavares namn',
        validators=[
            DataRequired(message='Vårdnadshavares namn är obligatoriskt'),
            Length(min=2,
                   max=100,
                   message='Namnet måste vara mellan 2 och 100 tecken')
        ])

    parent_email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    parent_phone = TelField(
        'Telefonnummer',
        validators=[
            DataRequired(message='Telefonnummer är obligatoriskt'),
            Length(min=10, max=20, message='Ange ett giltigt telefonnummer')
        ])

    # Address information
    address = StringField('Adress',
                          validators=[
                              DataRequired(message='Adress är obligatorisk'),
                              Length(max=200)
                          ])

    postal_code = StringField(
        'Postnummer',
        validators=[
            DataRequired(message='Postnummer är obligatoriskt'),
            Regexp(r'^\d{3}\s?\d{2}$',
                   message='Ange postnummer i format XXX XX')
        ])

    city = StringField('Ort',
                       validators=[
                           DataRequired(message='Ort är obligatorisk'),
                           Length(max=50)
                       ])

    # School information
    current_school = StringField('Nuvarande skola',
                                 validators=[Length(max=100)])


class SwishPaymentForm(FlaskForm):
    """Form for Swish payment processing"""
    
    amount = StringField(
        'Belopp (SEK)',
        validators=[
            DataRequired(message='Belopp är obligatoriskt'),
            Regexp(r'^\d+(\.\d{1,2})?$', message='Ange ett giltigt belopp (t.ex. 100.50)')
        ])
    
    message = StringField(
        'Meddelande (valfritt)',
        validators=[
            Optional(),
            Length(max=50, message='Meddelandet får vara max 50 tecken')
        ])
    
    payer_phone = StringField(
        'Telefonnummer (för m-commerce)',
        validators=[
            Optional(),
            Regexp(r'^(\+46|46|0)?[0-9\s\-]{8,15}$', 
                   message='Ange ett giltigt svenskt telefonnummer')
        ],
        description='Lämna tomt för vanlig Swish-betalning via QR-kod')


class DonationForm(FlaskForm):
    """Form for donations to the music school"""
    
    amount = SelectField(
        'Välj belopp',
        choices=[
            ('50', '50 SEK'),
            ('100', '100 SEK'),
            ('250', '250 SEK'),
            ('500', '500 SEK'),
            ('1000', '1000 SEK'),
            ('custom', 'Annat belopp')
        ],
        validators=[DataRequired(message='Välj ett belopp')]
    )
    
    custom_amount = StringField(
        'Annat belopp (SEK)',
        validators=[
            Optional(),
            Regexp(r'^\d+(\.\d{1,2})?$', message='Ange ett giltigt belopp')
        ])
    
    donor_name = StringField(
        'Ditt namn (valfritt)',
        validators=[
            Optional(),
            Length(max=50, message='Namnet får vara max 50 tecken')
        ])
    
    donor_phone = StringField(
        'Telefonnummer (för m-commerce)',
        validators=[
            Optional(),
            Regexp(r'^(\+46|46|0)?[0-9\s\-]{8,15}$', 
                   message='Ange ett giltigt svenskt telefonnummer')
        ])
    
    message = StringField(
        'Meddelande (valfritt)',
        validators=[
            Optional(),
            Length(max=40, message='Meddelandet får vara max 40 tecken')
        ],
        default='Donation till Brunnsbo Musikklasser')
    
    anonymous = BooleanField('Anonym donation')

    grade_applying_for = SelectField(
        'Årskurs som du söker till',
        choices=[('4', 'Årskurs 4'), ('5', 'Årskurs 5'), ('6', 'Årskurs 6'),
                 ('7', 'Årskurs 7'), ('8', 'Årskurs 8'), ('9', 'Årskurs 9')],
        validators=[DataRequired(message='Välj årskurs')])

    # Musical background
    musical_experience = TextAreaField(
        'Berätta om elevens musikbakgrund och tidigare erfarenheter',
        validators=[
            Length(max=1000, message='Texten får vara max 1000 tecken')
        ])

    motivation = TextAreaField(
        'Varför vill eleven gå i musikklass?',
        validators=[
            DataRequired(message='Motivation är obligatorisk'),
            Length(min=50,
                   max=1000,
                   message='Motivationen måste vara mellan 50 och 1000 tecken')
        ])

    # Practical information
    has_transportation = BooleanField(
        'Eleven har möjlighet att ta sig till och från skolan')

    additional_info = TextAreaField(
        'Övrig information',
        validators=[Length(max=500, message='Texten får vara max 500 tecken')])


class ContactForm(FlaskForm):
    """Form for general contact inquiries"""

    name = StringField('Namn',
                       validators=[
                           DataRequired(message='Namn är obligatoriskt'),
                           Length(min=2, max=100)
                       ])

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    phone = TelField('Telefonnummer (valfritt)', validators=[Length(max=20)])

    subject = StringField('Ämne',
                          validators=[
                              DataRequired(message='Ämne är obligatoriskt'),
                              Length(min=5, max=200)
                          ])

    message = TextAreaField(
        'Meddelande',
        validators=[
            DataRequired(message='Meddelande är obligatoriskt'),
            Length(min=20,
                   max=2000,
                   message='Meddelandet måste vara mellan 20 och 2000 tecken')
        ])


class LoginForm(FlaskForm):
    """Form for admin login"""

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    password = PasswordField(
        'Lösenord',
        validators=[DataRequired(message='Lösenord är obligatoriskt')])

    remember_me = BooleanField('Kom ihåg mig')


class ChangePasswordForm(FlaskForm):
    """Form for changing admin password"""

    current_password = PasswordField(
        'Nuvarande lösenord',
        validators=[
            DataRequired(message='Nuvarande lösenord är obligatoriskt')
        ])

    new_password = PasswordField(
        'Nytt lösenord',
        validators=[
            DataRequired(message='Nytt lösenord är obligatoriskt'),
            Length(min=8, message='Lösenordet måste vara minst 8 tecken långt')
        ])

    confirm_password = PasswordField(
        'Bekräfta nytt lösenord',
        validators=[
            DataRequired(message='Bekräfta det nya lösenordet'),
            EqualTo('new_password', message='Lösenorden matchar inte')
        ])


class CreateAdminForm(FlaskForm):
    """Form for creating new admin users"""

    username = StringField(
        'Användarnamn',
        validators=[
            DataRequired(message='Användarnamn är obligatoriskt'),
            Length(min=3,
                   max=64,
                   message='Användarnamn måste vara mellan 3 och 64 tecken')
        ])

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    password = PasswordField(
        'Lösenord',
        validators=[
            DataRequired(message='Lösenord är obligatoriskt'),
            Length(min=8, message='Lösenordet måste vara minst 8 tecken långt')
        ])

    confirm_password = PasswordField(
        'Bekräfta lösenord',
        validators=[
            DataRequired(message='Bekräfta lösenordet'),
            EqualTo('password', message='Lösenorden matchar inte')
        ])

    active = BooleanField('Aktiv användare', default=True)


class EventForm(FlaskForm):
    """Form for creating and editing events"""

    title = StringField(
        'Titel',
        validators=[
            DataRequired(message='Titel är obligatorisk'),
            Length(min=5,
                   max=200,
                   message='Titeln måste vara mellan 5 och 200 tecken')
        ])

    description = TextAreaField(
        'Beskrivning',
        validators=[
            Length(max=2000, message='Beskrivningen får vara max 2000 tecken')
        ])

    event_date = DateTimeLocalField(
        'Datum och tid',
        validators=[DataRequired(message='Datum och tid är obligatoriskt')],
        format='%Y-%m-%dT%H:%M',
        render_kw={
            'lang': 'sv-SE',
            'data-locale': 'sv-SE'
        })

    location = StringField('Plats',
                           validators=[
                               Length(
                                   max=200,
                                   message='Platsen får vara max 200 tecken')
                           ])

    ticket_url = StringField(
        'Länk för biljetter (valfritt)',
        validators=[Optional(), URL(message='Ange en giltig URL')])

    is_active = BooleanField('Aktivt evenemang', default=True)

    # Parent-specific information
    info_to_parents = TextAreaField(
        'Information till föräldrar (visas endast för föräldrar)',
        validators=[
            Optional(),
            Length(
                max=2000,
                message='Information till föräldrar får vara max 2000 tecken')
        ])

    # Event coordinator
    coordinator_id = SelectField('Evenemangskoordinator (valfritt)',
                                 coerce=int,
                                 validators=[Optional()])


class EditApplicationForm(FlaskForm):
    """Form for editing application details and status"""

    # Application status selection
    status = SelectField(
        'Status',
        choices=[('applied', 'Ansökt'),
                 ('application_withdrawn', 'Ansökan återkallad'),
                 ('invited_for_audition', 'Inbjuden till provsjungning'),
                 ('rejected', 'Avvisad'), ('offered', 'Erbjuden plats'),
                 ('accepted', 'Antagen')],
        validators=[DataRequired(message='Status är obligatorisk')])

    # Email confirmation status
    email_confirmed = BooleanField('E-post bekräftad')

    # Admin notes (optional)
    admin_notes = TextAreaField(
        'Administratörens anteckningar',
        validators=[
            Optional(),
            Length(max=500, message='Anteckningar får vara max 500 tecken')
        ])

    # Application year (editable for admin)
    application_year = StringField(
        'Ansökningsår',
        validators=[
            DataRequired(message='Ansökningsår är obligatoriskt'),
            Length(max=9, message='Format: YYYY/YYYY')
        ])


class CreateUserForm(FlaskForm):
    """Form for creating new users with role assignment"""

    first_name = StringField(
        'Förnamn',
        validators=[
            DataRequired(message='Förnamn är obligatoriskt'),
            Length(min=2,
                   max=50,
                   message='Förnamnet måste vara mellan 2 och 50 tecken')
        ])

    last_name = StringField(
        'Efternamn',
        validators=[
            DataRequired(message='Efternamn är obligatoriskt'),
            Length(min=2,
                   max=50,
                   message='Efternamnet måste vara mellan 2 och 50 tecken')
        ])

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    password = PasswordField(
        'Lösenord',
        validators=[
            DataRequired(message='Lösenord är obligatoriskt'),
            Length(min=8, message='Lösenordet måste vara minst 8 tecken långt')
        ])

    confirm_password = PasswordField(
        'Bekräfta lösenord',
        validators=[
            DataRequired(message='Bekräfta lösenordet'),
            EqualTo('password', message='Lösenorden matchar inte')
        ])

    active = BooleanField('Aktiv användare', default=True)


class EventTaskForm(FlaskForm):
    """Form for creating and editing event tasks"""

    title = StringField(
        'Uppgiftstitel',
        validators=[
            DataRequired(message='Titel är obligatorisk'),
            Length(min=3,
                   max=200,
                   message='Titeln måste vara mellan 3 och 200 tecken')
        ])

    description = TextAreaField(
        'Beskrivning',
        validators=[
            Optional(),
            Length(max=500, message='Beskrivningen får vara max 500 tecken')
        ])

    # Optional: assign to specific user
    assigned_to_user_id = SelectField('Tilldela till användare (valfritt)',
                                      choices=[],
                                      coerce=lambda x: int(x) if x else None,
                                      validators=[Optional()])

    # Due date offset fields
    due_offset_days = IntegerField(
        'Förfaller (dagar före/efter evenemanget)',
        validators=[
            Optional(),
            NumberRange(min=-365,
                        max=365,
                        message='Ange ett värde mellan -365 och 365 dagar')
        ],
        description=
        'Negativt tal = dagar före evenemanget, positivt = dagar efter')

    due_offset_hours = IntegerField(
        'Ytterligare timmar',
        validators=[
            Optional(),
            NumberRange(min=-24,
                        max=24,
                        message='Ange ett värde mellan -24 och 24 timmar')
        ],
        default=0)


class ForgotPasswordForm(FlaskForm):
    """Form for requesting password reset"""

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])


class ResetPasswordForm(FlaskForm):
    """Form for resetting password with confirmation code"""

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    confirmation_code = StringField(
        'Bekräftelsekod',
        validators=[
            DataRequired(message='Bekräftelsekod är obligatorisk'),
            Length(min=32,
                   max=32,
                   message='Bekräftelsekoden måste vara 32 tecken')
        ])

    new_password = PasswordField(
        'Nytt lösenord',
        validators=[
            DataRequired(message='Nytt lösenord är obligatoriskt'),
            Length(min=8, message='Lösenordet måste vara minst 8 tecken långt')
        ])

    confirm_password = PasswordField(
        'Bekräfta nytt lösenord',
        validators=[
            DataRequired(message='Bekräfta det nya lösenordet'),
            EqualTo('new_password', message='Lösenorden matchar inte')
        ])


class RegisterForm(FlaskForm):
    """Form for user registration with email verification"""

    first_name = StringField(
        'Förnamn',
        validators=[
            DataRequired(message='Förnamn är obligatoriskt'),
            Length(min=2,
                   max=50,
                   message='Förnamnet måste vara mellan 2 och 50 tecken')
        ])

    last_name = StringField(
        'Efternamn',
        validators=[
            DataRequired(message='Efternamn är obligatoriskt'),
            Length(min=2,
                   max=50,
                   message='Efternamnet måste vara mellan 2 och 50 tecken')
        ])

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    password = PasswordField(
        'Lösenord',
        validators=[
            DataRequired(message='Lösenord är obligatoriskt'),
            Length(min=8, message='Lösenordet måste vara minst 8 tecken långt')
        ])

    confirm_password = PasswordField(
        'Bekräfta lösenord',
        validators=[
            DataRequired(message='Bekräfta lösenordet'),
            EqualTo('password', message='Lösenorden matchar inte')
        ])


class VerifyEmailForm(FlaskForm):
    """Form for verifying email with confirmation code"""

    email = EmailField(
        'E-postadress',
        validators=[
            DataRequired(message='E-postadress är obligatorisk'),
            Email(message='Ange en giltig e-postadress')
        ])

    confirmation_code = StringField(
        'Bekräftelsekod',
        validators=[
            DataRequired(message='Bekräftelsekod är obligatorisk'),
            Length(min=32,
                   max=32,
                   message='Bekräftelsekoden måste vara 32 tecken')
        ])



# Swish Payment Forms
class DonationForm(FlaskForm):
    """Form for making donations via Swish"""
    
    amount = SelectField(
        "Donationsbelopp",
        choices=[
            ("50", "50 SEK"),
            ("100", "100 SEK"), 
            ("250", "250 SEK"),
            ("500", "500 SEK"),
            ("1000", "1 000 SEK"),
            ("custom", "Annat belopp")
        ],
        validators=[DataRequired(message="Välj ett donationsbelopp")]
    )
    
    custom_amount = DecimalField(
        "Eget belopp (SEK)",
        validators=[Optional()],
        render_kw={"placeholder": "0.00", "min": "1.00", "step": "0.01"}
    )
    
    donor_name = StringField(
        "Ditt namn (valfritt)",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "Visas i donationsmeddelandet om inte anonym"}
    )
    
    anonymous = BooleanField(
        "Anonym donation",
        default=False
    )
    
    donor_phone = StringField(
        "Telefonnummer för m-commerce (valfritt)",
        validators=[Optional(), Length(max=20)],
        render_kw={"placeholder": "070-123 45 67"}
    )
    
    message = StringField(
        "Meddelande (valfritt)",
        validators=[Optional(), Length(max=40)],
        render_kw={"placeholder": "Visas i Swish-betalningen"}
    )
    
    submit = SubmitField("Donera med Swish")


class SwishPaymentForm(FlaskForm):
    """Form for Swish payment details"""
    
    amount = DecimalField(
        "Belopp (SEK)",
        validators=[
            DataRequired(message="Belopp är obligatoriskt"),
            NumberRange(min=1, message="Minsta belopp är 1 SEK")
        ]
    )
    
    message = StringField(
        "Meddelande",
        validators=[Optional(), Length(max=50)],
        render_kw={"placeholder": "Meddelande som visas i Swish"}
    )
    
    payer_alias = StringField(
        "Telefonnummer (för m-commerce)",
        validators=[Optional(), Length(max=15)],
        render_kw={"placeholder": "46701234567"}
    )
    
    submit = SubmitField("Skapa betalning")

