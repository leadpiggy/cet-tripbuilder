"""
Global constants for TripBuilder application
Created: October 27, 2025
Purpose: Centralize commonly used values across forms, PDFs, and templates
"""

# Responsibility Statement (from passenger enrollment form)
# Used in: Enrollment wizard, PDF generation (MOU, Affidavit)
RESPONSIBILITY_STATEMENT = """Cuba Educational Travel serves only to assist in making necessary travel arrangements for its participating members, and in no way represents, or acts as agent for, transportation carriers, hotels, and other suppliers of services connected with this tour. Therefore, is not liable for any injury, damage, loss, accident, delay or other irregularity which may be caused by the defect of any vehicle or the negligence or default of any company or person engaged in performing any of the services involved. Additionally, responsibility is not accepted for losses or expenses due to sickness, weather, strike, hostilities, wars, natural disasters or other such causes. All services and accommodations are subject to the laws of the country in which they are provided. Cuba Educational Travel does not accept liability for any airline cancellation or delay incurred by the purchase of an airline ticket. Baggage and personal effects are the sole responsibility of the owners at all times. Cuba Educational Travel reserves the right to make changes in the published itineraries whenever, in its sole judgment, conditions so warrant, or if they deem it necessary for the comfort, convenience or safety of the tour participants.

Cuba Educational Travel also reserves the right to decline to accept any person as a participant in the tours, or to require any participant to withdraw from the tour at any time, when such an action is determined by the appropriate Cuba Educational Travel staff representative to be in the best interests of the health, safety, and general welfare of the tour group, or of the individual participant.

The undersigned has read carefully the schedule of activities for this tour. The undersigned recognizes that there is a moderate level of physical activity involved in the tour and the tour may require participants to walk long distances and climb stairs. The undersigned accepts any risks thereof and the conditions set forth therein. The undersigned agrees to release and hold harmless Cuba Educational Travel and any of their officers or representatives from any and all liability for delays, injuries or death, or for the loss of or damage to, his/her property however occurring during any portion of the program."""

# Travel Category License Options
# NOTE: These should be loaded from CustomField.options for field_key='opportunity.travelcategory'
# NOT hardcoded here. The GHL sync populates the actual dropdown values.
#
# To get travel categories in templates/forms:
#   from models import CustomField
#   categories = CustomField.query.filter_by(field_key='opportunity.travelcategory').first().options

# U.S. States for address forms
US_STATES = [
    'Alaska', 'Alabama', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia',
    'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
    'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
    'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
    'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia',
    'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
]

# NOTE: Countries, travel categories, and other dropdown values should be loaded
# from the CustomField.options column in the database, NOT hardcoded here.
# The GHL sync populates CustomField.options with actual dropdown values from GHL.
#
# To get dropdown options in templates/forms:
#   from models import CustomField
#   countries = CustomField.query.filter_by(field_key='opportunity.passportcountry').first().options

# Gender options
GENDER_OPTIONS = [
    {'value': 'male', 'label': 'Male', 'abbr': 'M'},
    {'value': 'female', 'label': 'Female', 'abbr': 'F'}
]

# Occupancy options
OCCUPANCY_OPTIONS = [
    {'value': 'single', 'label': 'Single Occupancy'},
    {'value': 'double', 'label': 'Double Occupancy'}
]

# Wizard step names (for enrollment process)
ENROLLMENT_STEPS = {
    1: 'trip_info',
    2: 'passenger',
    3: 'passport',
    4: 'health',
    5: 'signature'
}

# Wizard step labels (for progress bar)
ENROLLMENT_STEP_LABELS = {
    1: 'Trip Info',
    2: 'Passenger Info',
    3: 'Passport',
    4: 'Health',
    5: 'Signature'
}

# File upload allowed extensions
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Helper function to get dropdown options from database
def get_custom_field_options(field_key):
    """
    Get dropdown options for a custom field from database.
    
    Args:
        field_key: The field key (e.g., 'opportunity.travelcategory', 'opportunity.passportcountry')
    
    Returns:
        list: List of option values, or empty list if field not found
    
    Example:
        >>> get_custom_field_options('opportunity.travelcategory')
        ['Visiting Close Relatives – 515.561', 'Official Government Business – 515.562', ...]
    """
    from tripbuilder.models import CustomField
    field = CustomField.query.filter_by(field_key=field_key).first()
    return field.options if field and field.options else []