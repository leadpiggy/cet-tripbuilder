"""
GHL Custom Field Mapping Utilities

Maps between GHL custom field format and database columns.
GHL format: list of {id: field_id, fieldValue: value}
DB format: column values

IMPORTANT: This reflects the ACTUAL database schema columns.
"""

from datetime import datetime, date
from typing import Dict, List, Any, Optional


# Field mappings: GHL field key -> DB column name
TRIP_FIELD_MAP = {
    # Basic trip info
    'opportunity.tripname': 'name',
    'opportunity.destination': 'destination',
    'opportunity.tripdescription': 'trip_description',
    
    # Dates
    'opportunity.arrivaldate': 'arrival_date',
    'opportunity.returndate': 'return_date',
    'opportunity.depositdate': 'deposit_date',
    'opportunity.finalpayment': 'final_payment',
    
    # Capacity
    'opportunity.maxpassengers': 'max_passengers',
    'opportunity.passengercount': 'passenger_count',
    
    # Pricing
    'opportunity.tripstandardlevelpricing': 'trip_standard_level_pricing',
    
    # Vendor
    'opportunity.tripvendor': 'trip_vendor',
    'opportunity.vendorterms': 'vendor_terms',
    'opportunity.travelbusinessused': 'travel_business_used',
    
    # Trip details
    'opportunity.travelcategory': 'travel_category',
    'opportunity.nights': 'nights_total',
    'opportunity.lodging': 'lodging',
    'opportunity.lodgingnotes': 'lodging_notes',
    'opportunity.internaltripdetails': 'internal_trip_details',
    
    # Additional fields
    'opportunity.birthcountry': 'birth_country',
    'opportunity.passengerid': 'passenger_id',
    'opportunity.passengername': 'passenger_first_name',
    'opportunity.passengernumber': 'passenger_number',
    'opportunity.tripid': 'trip_id_custom',
    'opportunity.ischild': 'is_child',
}

PASSENGER_FIELD_MAP = {
    # Trip linking
    'opportunity.tripname': 'trip_name',
    
    # Basic info (denormalized)
    'contact.firstname': 'firstname',
    'contact.lastname': 'lastname',
    'contact.email': 'email',
    'contact.phone': 'phone',
    
    # Room Info
    'opportunity.userroomate': 'user_roomate',
    'opportunity.roomoccupancy': 'room_occupancy',
    
    # Passport Info
    'opportunity.passportnumber': 'passport_number',
    'opportunity.passportexpire': 'passport_expire',
    'opportunity.passportfile': 'passport_file',
    'opportunity.passportcountry': 'passport_country',
    
    # Health Details
    'opportunity.healthstate': 'health_state',
    'opportunity.healthmedicalinfo': 'health_medical_info',
    'opportunity.primaryphy': 'primary_phy',
    'opportunity.physicianphone': 'physician_phone',
    'opportunity.medicationlist': 'medication_list',
    
    # Emergency Contact
    'opportunity.contact1ulastname': 'contact1_ulast_name',
    'opportunity.contact1ufirstname': 'contact1_ufirst_name',
    'opportunity.contact1urelationship': 'contact1_urelationship',
    'opportunity.contact1umailingaddress': 'contact1_umailing_address',
    'opportunity.contact1ucity': 'contact1_ucity',
    'opportunity.contact1uzip': 'contact1_uzip',
    'opportunity.contact1uemail': 'contact1_uemail',
    'opportunity.contact1uphone': 'contact1_uphone',
    'opportunity.contact1umobnumber': 'contact1_umob_number',
    'opportunity.contact1ustate': 'contact1_ustate',
    
    # Legal
    'opportunity.formsubmitteddate': 'form_submitted_date',
    'opportunity.travelcategorylicense': 'travel_category_license',
    'opportunity.passengersignature': 'passenger_signature',
    
    # Documents
    'opportunity.reservation': 'reservation',
    'opportunity.mou': 'mou',
    'opportunity.affidavit': 'affidavit',
}


def parse_ghl_custom_fields(custom_fields_list: List[Dict]) -> Dict[str, Any]:
    """
    Convert GHL custom fields list to dictionary.
    
    GHL format: [{"id": "field_id", "fieldValue": "value"}, ...]
    Returns: {"field_key": "value", ...}
    
    Args:
        custom_fields_list: List of custom field objects from GHL
    
    Returns:
        Dictionary mapping field keys to values
    """
    result = {}
    
    if not isinstance(custom_fields_list, list):
        return result
    
    for field in custom_fields_list:
        if not isinstance(field, dict):
            continue
        
        field_id = field.get('id')
        field_value = field.get('fieldValue')
        
        if field_id:
            result[field_id] = field_value
    
    return result


def map_trip_custom_fields(custom_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map GHL custom fields to Trip model columns.
    
    Args:
        custom_fields: Dictionary of field_key -> value
    
    Returns:
        Dictionary of column_name -> value
    """
    mapped = {}
    
    for field_key, column_name in TRIP_FIELD_MAP.items():
        value = custom_fields.get(field_key)
        
        if value is not None:
            # Type conversions
            if column_name in ['arrival_date', 'return_date', 'deposit_date', 'final_payment', 'start_date', 'end_date']:
                # Parse date fields
                try:
                    if isinstance(value, str):
                        mapped[column_name] = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
                    elif isinstance(value, (int, float)):
                        mapped[column_name] = datetime.fromtimestamp(value / 1000).date()
                except:
                    pass
            
            elif column_name in ['max_passengers', 'passenger_number', 'passenger_count', 'nights_total', 'trip_id_custom', 'current_passengers']:
                # Parse integer fields
                try:
                    mapped[column_name] = int(float(value)) if value else None
                except:
                    pass
            
            elif column_name in ['trip_standard_level_pricing', 'base_price']:
                # Parse decimal fields
                try:
                    mapped[column_name] = float(value) if value else None
                except:
                    pass
            
            elif column_name == 'is_child':
                # Parse boolean
                if isinstance(value, bool):
                    mapped[column_name] = value
                elif isinstance(value, str):
                    mapped[column_name] = value.lower() in ['true', 'yes', '1']
            
            else:
                # String fields
                mapped[column_name] = str(value) if value else None
    
    return mapped


def map_passenger_custom_fields(custom_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map GHL custom fields to Passenger model columns.
    
    Args:
        custom_fields: Dictionary of field_key -> value
    
    Returns:
        Dictionary of column_name -> value
    """
    mapped = {}
    
    for field_key, column_name in PASSENGER_FIELD_MAP.items():
        value = custom_fields.get(field_key)
        
        if value is not None:
            # Type conversions
            if column_name in ['passport_expire', 'form_submitted_date', 'date_of_birth']:
                # Parse date fields
                try:
                    if isinstance(value, str):
                        mapped[column_name] = datetime.fromisoformat(value.replace('Z', '+00:00')).date()
                    elif isinstance(value, (int, float)):
                        mapped[column_name] = datetime.fromtimestamp(value / 1000).date()
                except:
                    pass
            
            elif column_name in ['registration_completed', 'documents_completed']:
                # Parse boolean
                if isinstance(value, bool):
                    mapped[column_name] = value
                elif isinstance(value, str):
                    mapped[column_name] = value.lower() in ['true', 'yes', '1']
            
            else:
                # String/text fields
                mapped[column_name] = str(value) if value else None
    
    return mapped


def create_ghl_custom_fields_dict(model_data: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert model data back to GHL custom fields dictionary format.
    
    Args:
        model_data: Dictionary of column values
        field_map: Mapping of field_key -> column_name
    
    Returns:
        Dict of {"field_key": "value"}
    """
    custom_fields_dict = {}
    
    # Reverse the mapping
    reverse_map = {v: k for k, v in field_map.items()}
    
    for column_name, value in model_data.items():
        field_key = reverse_map.get(column_name)
        
        if field_key and value is not None:
            # Convert dates to ISO format
            if isinstance(value, date):
                value = value.isoformat()
            # Convert boolean to string
            elif isinstance(value, bool):
                value = str(value).lower()
            
            custom_fields_dict[field_key] = value
    
    return custom_fields_dict
