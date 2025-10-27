#!/usr/bin/env python3
"""
Build Field Maps Table

Fetches custom field definitions from GHL and populates the field_maps table
with the mapping between GHL custom field IDs, field keys, and database columns.

This creates a database-driven field mapping instead of hardcoded dictionaries.
The field_maps table can then be used by sync scripts to dynamically map data.

CRITICAL: This script uses the ACTUAL field keys from GHL (with underscores!)
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import FieldMap
from ghl_api import GoHighLevelAPI


# Mapping of GHL field keys to (table, column, data_type)
# CRITICAL: Use the ACTUAL field keys from GHL (WITH underscores!)
# Format: 'opportunity.field_key': ('table_name', 'column_name', 'data_type')
FIELD_KEY_TO_TABLE = {
    # Trip fields (TripBooking pipeline)
    'opportunity.birth_country': ('trips', 'birth_country', 'string'),
    'opportunity.passenger_id': ('trips', 'passenger_id', 'string'),
    'opportunity.passenger_name': ('trips', 'passenger_first_name', 'string'),
    'opportunity.passenger_number': ('trips', 'passenger_number', 'integer'),
    'opportunity.trip_id': ('trips', 'trip_id_custom', 'integer'),
    'opportunity.trip_name': ('trips', 'trip_name', 'string'),
    'opportunity.nights': ('trips', 'nights_total', 'integer'),
    'opportunity.arrival_date': ('trips', 'arrival_date', 'date'),
    'opportunity.return_date': ('trips', 'return_date', 'date'),
    'opportunity.max_passengers': ('trips', 'max_passengers', 'integer'),
    'opportunity.travel_category': ('trips', 'travel_category', 'string'),
    'opportunity.trip_standard_level_pricing': ('trips', 'trip_standard_level_pricing', 'decimal'),
    'opportunity.passenger_count': ('trips', 'passenger_count', 'integer'),
    'opportunity.lodging': ('trips', 'lodging', 'string'),
    'opportunity.lodging_notes': ('trips', 'lodging_notes', 'string'),
    'opportunity.deposit_date': ('trips', 'deposit_date', 'date'),
    'opportunity.final_payment': ('trips', 'final_payment', 'date'),
    'opportunity.trip_description': ('trips', 'trip_description', 'string'),
    'opportunity.trip_vendor': ('trips', 'trip_vendor', 'string'),
    'opportunity.vendor_terms': ('trips', 'vendor_terms', 'string'),
    'opportunity.travel_business_used': ('trips', 'travel_business_used', 'string'),
    'opportunity.internal_trip_details': ('trips', 'internal_trip_details', 'string'),
    'opportunity.is_child': ('trips', 'is_child', 'boolean'),
    
    # Passenger fields (Passenger pipeline)
    'opportunity.user_roomate': ('passengers', 'user_roomate', 'string'),
    'opportunity.room_occupancy': ('passengers', 'room_occupancy', 'string'),
    'opportunity.passport_number': ('passengers', 'passport_number', 'string'),
    'opportunity.passport_expire': ('passengers', 'passport_expire', 'date'),
    'opportunity.passport_file': ('passengers', 'passport_file', 'string'),
    'opportunity.passport_country': ('passengers', 'passport_country', 'string'),
    'opportunity.health_state': ('passengers', 'health_state', 'string'),
    'opportunity.health_medical_info': ('passengers', 'health_medical_info', 'string'),
    'opportunity.primary_phy': ('passengers', 'primary_phy', 'string'),
    'opportunity.physician_phone': ('passengers', 'physician_phone', 'string'),
    'opportunity.medication_list': ('passengers', 'medication_list', 'string'),
    'opportunity.contact1_ulast_name': ('passengers', 'contact1_ulast_name', 'string'),
    'opportunity.contact1_ufirst_name': ('passengers', 'contact1_ufirst_name', 'string'),
    'opportunity.contact1_urelationship': ('passengers', 'contact1_urelationship', 'string'),
    'opportunity.contact1_umailing_address': ('passengers', 'contact1_umailing_address', 'string'),
    'opportunity.contact1_ucity': ('passengers', 'contact1_ucity', 'string'),
    'opportunity.contact1_uzip': ('passengers', 'contact1_uzip', 'string'),
    'opportunity.contact1_uemail': ('passengers', 'contact1_uemail', 'string'),
    'opportunity.contact1_uphone': ('passengers', 'contact1_uphone', 'string'),
    'opportunity.contact1_umob_number': ('passengers', 'contact1_umob_number', 'string'),
    'opportunity.contact1_ustate': ('passengers', 'contact1_ustate', 'string'),
    'opportunity.form_submitted_date': ('passengers', 'form_submitted_date', 'date'),
    'opportunity.travel_category_license': ('passengers', 'travel_category_license', 'string'),
    'opportunity.passenger_signature': ('passengers', 'passenger_signature', 'string'),
    'opportunity.reservation': ('passengers', 'reservation', 'string'),
    'opportunity.mou': ('passengers', 'mou', 'string'),
    'opportunity.affidavit': ('passengers', 'affidavit', 'string'),
}


def save_json(data, filename):
    """Save data to JSON file"""
    filepath = Path(filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"✅ Saved to {filepath}")


def main():
    """Main function to build field maps"""
    print("=" * 70)
    print("BUILD FIELD MAPS TABLE")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Get GHL credentials
        location_id = os.getenv('GHL_LOCATION_ID')
        api_key = os.getenv('GHL_API_TOKEN')
        
        if not location_id or not api_key:
            print("❌ ERROR: GHL_LOCATION_ID and GHL_API_TOKEN must be set in environment")
            print("   Create a .env file with:")
            print("   GHL_LOCATION_ID=your_location_id")
            print("   GHL_API_TOKEN=your_api_token")
            sys.exit(1)
        
        print(f"📍 Location ID: {location_id}")
        print()
        
        # Initialize API
        api = GoHighLevelAPI(location_id=location_id, api_key=api_key)
        
        # 1. Fetch custom field definitions from GHL
        print("1️⃣  Fetching custom field definitions from GHL...")
        try:
            response = api.get_custom_fields(model='opportunity')
            custom_fields = response.get('customFields', [])
            
            # Save response for inspection
            save_json(response, 'custom_fields_response.json')
            
            print(f"   ✅ Found {len(custom_fields)} custom fields")
        except Exception as e:
            print(f"❌ Error fetching custom fields: {e}")
            sys.exit(1)
        
        print()
        
        # 2. Show actual field keys from GHL
        print("2️⃣  Actual field keys from GHL:")
        print("   (Verify these have underscores!)")
        print()
        for field in custom_fields[:10]:
            field_key = field.get('fieldKey', 'N/A')
            name = field.get('name', 'N/A')
            field_id = field.get('id', 'N/A')
            print(f"   - {field_key}")
            print(f"     Name: {name}")
            print(f"     ID: {field_id}")
            print()
        
        # 3. Clear existing field maps
        print("3️⃣  Clearing existing field maps...")
        try:
            FieldMap.query.delete()
            db.session.commit()
            print("   ✅ Cleared old mappings")
        except Exception as e:
            print(f"❌ Error clearing field maps: {e}")
            db.session.rollback()
            sys.exit(1)
        
        print()
        
        # 4. Build field maps from GHL data
        print("4️⃣  Building field maps...")
        created_count = 0
        missing_mappings = []
        
        for field in custom_fields:
            field_id = field.get('id')
            field_key = field.get('fieldKey')
            name = field.get('name')
            data_type = field.get('dataType')
            
            if not field_id or not field_key:
                continue
            
            # Check if we have a mapping for this field key
            if field_key in FIELD_KEY_TO_TABLE:
                table, column, db_data_type = FIELD_KEY_TO_TABLE[field_key]
                
                # Create field map entry
                field_map = FieldMap(
                    ghl_key=field_id,
                    field_key=field_key,
                    table_column=column,
                    tablename=table,
                    data_type=db_data_type
                )
                
                try:
                    db.session.add(field_map)
                    created_count += 1
                    print(f"   ✅ {table}.{column} <- {field_key} (ID: {field_id})")
                except Exception as e:
                    print(f"   ❌ Error adding {field_key}: {e}")
            else:
                missing_mappings.append({
                    'field_key': field_key,
                    'name': name,
                    'id': field_id,
                    'data_type': data_type
                })
        
        # Commit all changes
        try:
            db.session.commit()
            print()
            print(f"   ✅ Created {created_count} field mappings")
        except Exception as e:
            print(f"❌ Error committing field maps: {e}")
            db.session.rollback()
            sys.exit(1)
        
        print()
        
        # 5. Report missing mappings
        if missing_mappings:
            print("⚠️  Fields without mappings:")
            print()
            for field in missing_mappings:
                print(f"   - {field['field_key']}")
                print(f"     Name: {field['name']}")
                print(f"     ID: {field['id']}")
                print(f"     Type: {field['data_type']}")
                print()
            
            print(f"   Total unmapped: {len(missing_mappings)}")
            print()
            print("   To add these fields:")
            print("   1. Add them to FIELD_KEY_TO_TABLE in this script")
            print("   2. Run this script again")
        else:
            print("✅ All fields mapped!")
        
        print()
        
        # 6. Verify field maps table
        print("5️⃣  Verifying field_maps table...")
        total = FieldMap.query.count()
        print(f"   Total field maps: {total}")
        
        print()
        print("   Sample mappings:")
        for fm in FieldMap.query.limit(5):
            print(f"     {fm.tablename}.{fm.table_column} <- {fm.field_key} (ID: {fm.ghl_key})")
        
        print()
        print("=" * 70)
        print("BUILD COMPLETE")
        print("=" * 70)
        print()
        print("📁 Files created:")
        print("   - custom_fields_response.json (for inspection)")
        print()
        print("📊 Database tables updated:")
        print("   - field_maps table populated")
        print()
        print("Next steps:")
        print("1. Verify field keys: cat custom_fields_response.json | grep fieldKey | head -20")
        print("2. Check database: sqlite3 instance/tripbuilder.db 'SELECT * FROM field_maps LIMIT 5;'")
        print("3. Run sync with dynamic mapping")
        print()


if __name__ == '__main__':
    main()
