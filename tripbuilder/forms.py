"""
WTForms for TripBuilder Multi-Step Enrollment Wizard
Created: October 27, 2025

Forms for the 5-step enrollment process:
1. Trip Info (display only)
2. Passenger Information
3. Passport & DOB
4. Health Information  
5. Emergency Contact + Signature
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SelectField, RadioField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, Length


class Step2PassengerInfoForm(FlaskForm):
    """Step 2: Passenger Information"""
    
    # Legal name (from passport)
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    
    # Address
    mailing_address = StringField('Mailing Address', validators=[DataRequired(), Length(max=255)])
    user_city = StringField('City', validators=[DataRequired(), Length(max=100)])
    user_state = SelectField('State', validators=[DataRequired()], choices=[])  # Populated dynamically
    user_zip = StringField('Zip Code', validators=[DataRequired(), Length(max=20)])
    
    # Contact
    user_email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=200)])
    user_phone = StringField('Phone Number', validators=[Optional(), Length(max=50)])
    mob_number = StringField('Mobile Number', validators=[Optional(), Length(max=50)])
    
    # Room preferences
    choose_occupancy = SelectField('Occupancy', 
                                   choices=[('', 'Choose Occupancy'),
                                           ('single', 'Single Occupancy'),
                                           ('double', 'Double Occupancy')],
                                   validators=[DataRequired()])
    user_roomate = StringField('Roommate', validators=[Optional(), Length(max=255)])
    
    # Birth country
    birth_country = SelectField('Country of Birth', validators=[DataRequired()], choices=[])  # From GHL


class Step3PassportInfoForm(FlaskForm):
    """Step 3: Passport Information"""
    
    passport_number = StringField('Passport Number', validators=[DataRequired(), Length(max=255)])
    user_dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    gender = RadioField('Gender', 
                       choices=[('male', 'Male'), ('female', 'Female')],
                       validators=[DataRequired()])
    passport_expire = DateField('Passport Expiration', validators=[DataRequired()], format='%Y-%m-%d')
    passport_country = SelectField('Passport Country', validators=[DataRequired()], choices=[])  # From GHL
    passport_file = FileField('Passport Photo', 
                             validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 
                                                    'Images only (JPG, PNG, GIF)')])


class Step4HealthInfoForm(FlaskForm):
    """Step 4: Health Information"""
    
    health_state = TextAreaField('General State of Health', 
                                 validators=[Optional()],
                                 render_kw={'rows': 4, 'placeholder': 'How is your general state of health?'})
    health_medical_info = TextAreaField('Medical/Physical/Dietary Limitations', 
                                       validators=[Optional()],
                                       render_kw={'rows': 4, 'placeholder': 'Special medical, physical, dietary limitations, or allergies?'})
    primary_phy = StringField('Primary Physician', validators=[Optional(), Length(max=255)])
    physician_phone = StringField('Physician Phone Number', validators=[Optional(), Length(max=50)])
    medication_list = TextAreaField('Medications', 
                                   validators=[Optional()],
                                   render_kw={'rows': 4, 'placeholder': 'List all Rx medications (recommended)'})


class Step5SignatureForm(FlaskForm):
    """Step 5: Emergency Contact + Signature"""
    
    # Emergency Contact 1 (Required)
    contact1_ufirst_name = StringField('First Name', validators=[DataRequired(), Length(max=255)])
    contact1_ulast_name = StringField('Last Name', validators=[DataRequired(), Length(max=255)])
    contact1_urelationship = StringField('Relationship', validators=[DataRequired(), Length(max=255)])
    contact1_umailing_address = StringField('Mailing Address', validators=[DataRequired(), Length(max=255)])
    contact1_ucity = StringField('City', validators=[DataRequired(), Length(max=255)])
    contact1_ustate = SelectField('State', validators=[DataRequired()], choices=[])
    contact1_uzip = StringField('Zip Code', validators=[DataRequired(), Length(max=255)])
    contact1_uemail = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    contact1_uphone = StringField('Phone', validators=[Optional(), Length(max=255)])
    contact1_umob_number = StringField('Mobile', validators=[Optional(), Length(max=255)])
    
    # Emergency Contact 2 (Optional)
    contact2_ufirst_name = StringField('First Name', validators=[Optional(), Length(max=255)])
    contact2_ulast_name = StringField('Last Name', validators=[Optional(), Length(max=255)])
    contact2_urelationship = StringField('Relationship', validators=[Optional(), Length(max=255)])
    contact2_umailing_address = StringField('Mailing Address', validators=[Optional(), Length(max=255)])
    contact2_ucity = StringField('City', validators=[Optional(), Length(max=255)])
    contact2_ustate = SelectField('State', validators=[Optional()], choices=[])
    contact2_uzip = StringField('Zip Code', validators=[Optional(), Length(max=255)])
    contact2_uemail = StringField('Email', validators=[Optional(), Email(), Length(max=255)])
    contact2_uphone = StringField('Phone', validators=[Optional(), Length(max=255)])
    contact2_umob_number = StringField('Mobile', validators=[Optional(), Length(max=255)])
    
    # Travel category and signature
    travel_category_license = SelectField('Travel Category License', 
                                         validators=[DataRequired()],
                                         choices=[])  # From GHL
    signature_data = HiddenField('Signature Data', validators=[DataRequired()])
    agree = BooleanField('I agree to the Responsibility Statement', validators=[DataRequired()])


# Helper function to populate form choices from database
def populate_form_choices(form):
    """
    Populate SelectField choices from CustomField options in database.
    
    Args:
        form: Form instance to populate
        
    This should be called before rendering the form to ensure
    dropdown options are current from GHL sync.
    """
    from models import CustomField
    from constants import US_STATES, get_custom_field_options
    
    # U.S. States (static list)
    state_choices = [('', 'State')] + [(s, s) for s in US_STATES]
    
    # Birth countries (from GHL)
    birth_countries = get_custom_field_options('opportunity.birthcountry')
    birth_country_choices = [('', 'Select Country of Birth...')] + [(c, c) for c in birth_countries]
    
    # Passport countries (from GHL)
    passport_countries = get_custom_field_options('opportunity.passportcountry')
    passport_country_choices = [('', 'Select Country...')] + [(c, c) for c in passport_countries]
    
    # Travel categories (from GHL)
    travel_categories = get_custom_field_options('opportunity.travelcategory')
    travel_category_choices = [('', 'Select Travel Category License')] + [(c, c) for c in travel_categories]
    
    # Apply choices to form fields
    if hasattr(form, 'user_state'):
        form.user_state.choices = state_choices
    
    if hasattr(form, 'birth_country'):
        form.birth_country.choices = birth_country_choices
    
    if hasattr(form, 'passport_country'):
        form.passport_country.choices = passport_country_choices
    
    if hasattr(form, 'travel_category_license'):
        form.travel_category_license.choices = travel_category_choices
    
    # Emergency contact states
    if hasattr(form, 'contact1_ustate'):
        form.contact1_ustate.choices = state_choices
    if hasattr(form, 'contact2_ustate'):
        form.contact2_ustate.choices = state_choices