#!/usr/bin/env python3
"""
Comprehensive Passenger-Trip Linking Script Using Raw JSON Data

This script:
1. Reads passengers from raw_ghl_responses/passengers_raw.json
2. Extracts trip_name using correct field naming (fieldValueString, fieldValueNumber, etc.)
3. Updates passenger records with trip_name
4. Ensures all trip names are in GHL dropdown
5. Links passengers to trips by matching trip_name

Usage:
    python3 link_passengers_from_raw_json.py
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app import app
from models import db, Passenger, Trip, CustomField, FieldMap
from ghl_api import GoHighLevelAPI


def get_field_value_by_type(field_data):
    """
    Extract value from custom field based on type.
    
    GHL uses naming convention: fieldValue + CapitalizedType
    - STRING -> fieldValueString
    - NUMBER -> fieldValueNumber
    - DATE -> fieldValueDate
    - etc.
    """
    field_type = field_data.get('type', '').upper()
    
    # Try the typed key first
    typed_key = f'fieldValue{field_type.capitalize()}'
    if typed_key in field_data:
        return field_data[typed_key]
    
    # Fallback to generic fieldValue
    if 'fieldValue' in field_data:
        return field_data['fieldValue']
    
    return None


def extract_trip_names_from_raw_json():
    """
    Read passengers_raw.json and extract all trip names.
    Returns dict: {passenger_id: trip_name}
    """
    print("=" * 70)
    print("STEP 1: Extract Trip Names from Raw JSON")
    print("=" * 70)
    print()
    
    json_path = os.path.expanduser(
        '~/Downloads/claude_code_tripbuilder/tripbuilder/raw_ghl_responses/passengers_raw.json'
    )
    
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return {}
    
    print(f"📂 Reading file: {json_path}")
    
    with open(json_path, 'r') as f:
        passengers_data = json.load(f)
    
    print(f"   Loaded {len(passengers_data)} passenger records")
    print()
    
    # Extract trip names
    trip_name_field_id = 'tJoung7L6ymp1vHmU2Tq'
    passenger_trip_names = {}
    passengers_with_trip_name = 0
    
    for passenger in passengers_data:
        passenger_id = passenger.get('id')
        if not passenger_id:
            continue
        
        custom_fields = passenger.get('customFields', [])
        
        for field in custom_fields:
            if field.get('id') == trip_name_field_id:
                trip_name = get_field_value_by_type(field)
                
                if trip_name:
                    passenger_trip_names[passenger_id] = str(trip_name)
                    passengers_with_trip_name += 1
                break
    
    print(f"✅ Extracted trip names:")
    print(f"   Passengers with trip_name: {passengers_with_trip_name}")
    print(f"   Passengers without trip_name: {len(passengers_data) - passengers_with_trip_name}")
    print()
    
    # Show sample
    if passenger_trip_names:
        sample_id = list(passenger_trip_names.keys())[0]
        print(f"   Sample: {sample_id[:20]}... -> {passenger_trip_names[sample_id]}")
        print()
    
    return passenger_trip_names


def update_passenger_trip_names(passenger_trip_names):
    """
    Update passenger records in database with trip_name values.
    """
    print("=" * 70)
    print("STEP 2: Update Database with Trip Names")
    print("=" * 70)
    print()
    
    with app.app_context():
        updated_count = 0
        not_found_count = 0
        already_set_count = 0
        
        for passenger_id, trip_name in passenger_trip_names.items():
            passenger = Passenger.query.get(passenger_id)
            
            if not passenger:
                not_found_count += 1
                continue
            
            if passenger.trip_name and passenger.trip_name.strip():
                already_set_count += 1
                continue
            
            passenger.trip_name = trip_name
            passenger.updated_at = datetime.utcnow()
            db.session.add(passenger)
            updated_count += 1
            
            if updated_count % 100 == 0:
                db.session.commit()
                print(f"   💾 Updated {updated_count} passengers...")
        
        # Final commit
        db.session.commit()
        
        print()
        print(f"✅ Results:")
        print(f"   Updated: {updated_count} passengers")
        print(f"   Already had trip_name: {already_set_count} passengers")
        print(f"   Not found in DB: {not_found_count} passengers")
        print()


def ensure_field_mapping():
    """Ensure trip_name field mapping exists."""
    print("=" * 70)
    print("STEP 3: Ensure Field Mapping")
    print("=" * 70)
    print()
    
    with app.app_context():
        mapping = FieldMap.query.filter_by(
            tablename='passengers',
            field_key='opportunity.trip_name'
        ).first()
        
        if mapping:
            print(f"✅ Field mapping exists: {mapping.field_key} -> passengers.{mapping.table_column}")
        else:
            print("📝 Creating field mapping...")
            mapping = FieldMap(
                ghl_key='passenger_tJoung7L6ymp1vHmU2Tq',
                field_key='opportunity.trip_name',
                table_column='trip_name',
                tablename='passengers',
                data_type='string'
            )
            db.session.add(mapping)
            db.session.commit()
            print("✅ Created field mapping")
        print()


def sync_trip_names_to_ghl_dropdown(api):
    """
    Ensure all trip names exist in GHL opportunity.trip_name dropdown.
    """
    print("=" * 70)
    print("STEP 4: Sync Trip Names to GHL Dropdown")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Get all unique trip names from database
        trips = Trip.query.all()
        all_trip_names = sorted(set([trip.name for trip in trips if trip.name]))
        
        print(f"📊 Found {len(all_trip_names)} unique trip names in database")
        print()
        
        # Get the custom field from GHL
        print("🔍 Fetching custom field definition from GHL...")
        try:
            response = api.get_custom_fields(model='opportunity')
            custom_fields = response.get('customFields', [])
            
            trip_name_field = None
            for field in custom_fields:
                if field.get('id') == 'tJoung7L6ymp1vHmU2Tq':
                    trip_name_field = field
                    break
            
            if not trip_name_field:
                print("❌ Could not find opportunity.trip_name field in GHL")
                return False
            
            print(f"✅ Found field: {trip_name_field.get('name')}")
            print(f"   Data Type: {trip_name_field.get('dataType')}")
            print()
            
            # Get existing options
            existing_options = trip_name_field.get('options', [])
            print(f"📋 Current dropdown has {len(existing_options)} options")
            
            # Find missing trip names
            existing_set = set(existing_options)
            missing_names = [name for name in all_trip_names if name not in existing_set]
            
            if not missing_names:
                print("✅ All trip names already in dropdown!")
                print()
                return True
            
            print(f"⚠️  Found {len(missing_names)} missing trip names")
            if len(missing_names) <= 10:
                for name in missing_names:
                    print(f"   - {name}")
            else:
                for name in missing_names[:10]:
                    print(f"   - {name}")
                print(f"   ... and {len(missing_names) - 10} more")
            print()
            
            # Update the dropdown
            updated_options = list(existing_set) + missing_names
            updated_options.sort()
            
            print(f"🔄 Updating GHL dropdown with {len(updated_options)} total options...")
            
            update_data = {
                'name': trip_name_field.get('name'),
                'dataType': trip_name_field.get('dataType'),
                'options': updated_options
            }
            
            api._make_request(
                "PUT",
                f"locations/{api.location_id}/customFields/{trip_name_field['id']}",
                data=update_data
            )
            
            print(f"✅ Successfully updated GHL dropdown!")
            print(f"   Added {len(missing_names)} new options")
            print()
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def link_passengers_to_trips():
    """
    Link passengers to trips by matching trip_name.
    """
    print("=" * 70)
    print("STEP 5: Link Passengers to Trips")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Get stats
        total_passengers = Passenger.query.count()
        passengers_without_trip = Passenger.query.filter_by(trip_id=None).count()
        passengers_with_trip_name = Passenger.query.filter(
            Passenger.trip_name != None,
            Passenger.trip_name != ''
        ).count()
        
        print(f"📊 Database Status:")
        print(f"   Total Passengers: {total_passengers}")
        print(f"   Without trip_id: {passengers_without_trip}")
        print(f"   With trip_name: {passengers_with_trip_name}")
        print()
        
        if passengers_without_trip == 0:
            print("✅ All passengers already linked!")
            return True
        
        # Build trip lookup tables
        print("📚 Building trip lookup tables...")
        all_trips = Trip.query.all()
        
        # Exact match lookup
        trip_exact = {}
        # Case-insensitive lookup
        trip_lower = {}
        
        for trip in all_trips:
            if trip.name:
                trip_exact[trip.name] = trip
                trip_lower[trip.name.lower()] = trip
        
        print(f"   Loaded {len(trip_exact)} trips")
        print()
        
        # Link passengers
        print("🔗 Linking passengers...")
        linked_count = 0
        no_trip_name = 0
        no_match = 0
        
        passengers = Passenger.query.filter(
            Passenger.trip_id == None,
            Passenger.trip_name != None,
            Passenger.trip_name != ''
        ).all()
        
        unmatched_samples = []
        
        for i, passenger in enumerate(passengers, 1):
            trip_name = passenger.trip_name.strip()
            
            # Try exact match
            trip = trip_exact.get(trip_name)
            
            # Try case-insensitive
            if not trip:
                trip = trip_lower.get(trip_name.lower())
            
            # Try partial match
            if not trip:
                name_lower = trip_name.lower()
                for stored_lower, stored_trip in trip_lower.items():
                    if name_lower in stored_lower or stored_lower in name_lower:
                        trip = stored_trip
                        break
            
            if trip:
                passenger.trip_id = trip.id
                db.session.add(passenger)
                linked_count += 1
                
                if linked_count % 100 == 0:
                    print(f"   ✅ Linked {linked_count}...")
                    db.session.commit()
            else:
                no_match += 1
                if len(unmatched_samples) < 10:
                    unmatched_samples.append(trip_name)
            
            if i % 500 == 0:
                db.session.commit()
        
        db.session.commit()
        
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"✅ Linked: {linked_count}")
        print(f"⚠️  No match: {no_match}")
        print()
        
        if unmatched_samples:
            print("Sample unmatched trip names:")
            for name in unmatched_samples:
                print(f"   - {name}")
            print()
        
        remaining = Passenger.query.filter_by(trip_id=None).count()
        success_rate = ((total_passengers - remaining) / total_passengers) * 100
        
        print(f"📊 Final Status:")
        print(f"   With trip_id: {total_passengers - remaining}")
        print(f"   Without trip_id: {remaining}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        if remaining == 0:
            print("🎉 SUCCESS! All passengers linked!")
        
        return True


def main():
    """Run all steps."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "PASSENGER-TRIP LINKING FROM RAW JSON" + " " * 21 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    try:
        # Step 1: Extract trip names from raw JSON
        passenger_trip_names = extract_trip_names_from_raw_json()
        
        if not passenger_trip_names:
            print("❌ No trip names found in raw JSON")
            return
        
        # Step 2: Update database
        update_passenger_trip_names(passenger_trip_names)
        
        # Step 3: Ensure field mapping
        ensure_field_mapping()
        
        # Step 4: Sync to GHL dropdown
        api = GoHighLevelAPI(
            location_id=os.getenv('GHL_LOCATION_ID'),
            api_key=os.getenv('GHL_API_TOKEN')
        )
        sync_trip_names_to_ghl_dropdown(api)
        
        # Step 5: Link passengers
        link_passengers_to_trips()
        
        print()
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 25 + "ALL STEPS COMPLETE!" + " " * 24 + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        
    except Exception as e:
        print()
        print("❌ Fatal error:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
