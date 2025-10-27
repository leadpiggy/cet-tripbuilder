#!/usr/bin/env python3
"""
Comprehensive Passenger-Trip Linking Script

This script performs the following operations:
1. Adds trip_name field mapping to the field_maps table
2. Ensures all Trip names are in the GHL 'opportunity.trip_name' dropdown
3. Re-syncs passengers to populate trip_name field
4. Links passengers to trips by matching trip_name

Usage:
    python3 link_passengers_comprehensive.py
"""

import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

from app import app
from models import db, Passenger, Trip, CustomField, FieldMap
from ghl_api import GoHighLevelAPI


def ensure_trip_name_field_mapping():
    """
    Ensure the trip_name field mapping exists in field_maps table.
    """
    print("=" * 70)
    print("STEP 1: Ensure Field Mapping")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Check if mapping exists for passengers table
        mapping = FieldMap.query.filter_by(
            tablename='passengers',
            field_key='opportunity.trip_name'
        ).first()
        
        if mapping:
            print(f"✅ Field mapping already exists:")
            print(f"   {mapping.field_key} -> passengers.{mapping.table_column}")
            print(f"   GHL Key: {mapping.ghl_key}")
        else:
            print("📝 Creating field mapping...")
            # Use prefixed ghl_key to avoid unique constraint issues
            mapping = FieldMap(
                ghl_key='passenger_tJoung7L6ymp1vHmU2Tq',
                field_key='opportunity.trip_name',
                table_column='trip_name',
                tablename='passengers',
                data_type='string'
            )
            db.session.add(mapping)
            db.session.commit()
            print(f"✅ Created mapping: opportunity.trip_name -> passengers.trip_name")
        print()


def sync_trip_names_to_ghl_dropdown(api):
    """
    Ensure all trip names exist in the GHL opportunity.trip_name custom field dropdown.
    
    This updates the GHL custom field definition to include all trip names as options.
    """
    print("=" * 70)
    print("STEP 2: Sync Trip Names to GHL Dropdown")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Get all trips
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
            print(f"   Field Key: {trip_name_field.get('fieldKey')}")
            print(f"   Data Type: {trip_name_field.get('dataType')}")
            print()
            
            # Get existing options
            existing_options = trip_name_field.get('options', [])
            print(f"📋 Current dropdown has {len(existing_options)} options")
            
            # Find missing trip names
            existing_option_values = set(existing_options)
            missing_names = [name for name in all_trip_names if name not in existing_option_values]
            
            if not missing_names:
                print("✅ All trip names already exist in dropdown!")
                print()
                return True
            
            print(f"⚠️  Found {len(missing_names)} trip names missing from dropdown:")
            for name in missing_names[:10]:  # Show first 10
                print(f"   - {name}")
            if len(missing_names) > 10:
                print(f"   ... and {len(missing_names) - 10} more")
            print()
            
            # Add missing names to options
            updated_options = list(existing_option_values) + missing_names
            updated_options.sort()
            
            print(f"🔄 Updating custom field with {len(updated_options)} total options...")
            
            # Update the custom field in GHL
            update_data = {
                'name': trip_name_field.get('name'),
                'dataType': trip_name_field.get('dataType'),
                'options': updated_options
            }
            
            update_response = api._make_request(
                "PUT",
                f"locations/{api.location_id}/customFields/{trip_name_field['id']}",
                data=update_data
            )
            
            print(f"✅ Successfully updated GHL dropdown!")
            print(f"   Added {len(missing_names)} new trip names")
            print()
            return True
            
        except Exception as e:
            print(f"❌ Error updating GHL dropdown: {e}")
            import traceback
            traceback.print_exc()
            return False


def resync_passenger_trip_names(api):
    """
    Re-sync passengers from GHL to populate the trip_name field.
    Only updates passengers that don't have trip_name set.
    """
    print("=" * 70)
    print("STEP 3: Re-sync Passenger Trip Names")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Count passengers without trip_name
        passengers_without_name = Passenger.query.filter(
            (Passenger.trip_name == None) | (Passenger.trip_name == '')
        ).count()
        
        if passengers_without_name == 0:
            print("✅ All passengers already have trip_name populated!")
            print()
            return True
        
        print(f"📊 Found {passengers_without_name} passengers without trip_name")
        print("🔄 Fetching opportunity data from GHL...")
        print()
        
        # Get passengers without trip_name
        passengers = Passenger.query.filter(
            (Passenger.trip_name == None) | (Passenger.trip_name == '')
        ).all()
        
        updated_count = 0
        error_count = 0
        batch_size = 100
        
        for i, passenger in enumerate(passengers, 1):
            try:
                # Fetch opportunity from GHL
                response = api._make_request("GET", f"opportunities/{passenger.id}")
                
                if 'opportunity' in response:
                    opportunity = response['opportunity']
                    custom_fields = opportunity.get('customFields', [])
                    
                    # Find trip_name field
                    for field in custom_fields:
                        if field.get('id') == 'tJoung7L6ymp1vHmU2Tq':
                            trip_name = (field.get('fieldValue') or 
                                       field.get('fieldValueString') or 
                                       field.get('value'))
                            
                            if trip_name:
                                passenger.trip_name = str(trip_name)
                                passenger.updated_at = datetime.utcnow()
                                db.session.add(passenger)
                                updated_count += 1
                            break
                
                # Commit every batch_size records
                if i % batch_size == 0:
                    db.session.commit()
                    print(f"   💾 Updated {updated_count} passengers (processed {i}/{len(passengers)})")
                    
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only show first 5 errors
                    print(f"   ⚠️  Error fetching passenger {passenger.id}: {e}")
                db.session.rollback()
        
        # Final commit
        db.session.commit()
        
        print()
        print(f"✅ Updated trip_name for {updated_count} passengers")
        if error_count > 0:
            print(f"⚠️  {error_count} errors occurred")
        print()
        return True


def link_passengers_to_trips():
    """
    Link passengers to trips by matching trip_name to trip.name.
    """
    print("=" * 70)
    print("STEP 4: Link Passengers to Trips")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Get counts
        total_passengers = Passenger.query.count()
        passengers_without_trip = Passenger.query.filter_by(trip_id=None).count()
        passengers_with_trip_name = Passenger.query.filter(
            Passenger.trip_name != None,
            Passenger.trip_name != ''
        ).count()
        total_trips = Trip.query.count()
        
        print(f"📊 Database Status:")
        print(f"   Total Passengers: {total_passengers}")
        print(f"   Passengers without trip_id: {passengers_without_trip}")
        print(f"   Passengers with trip_name: {passengers_with_trip_name}")
        print(f"   Total Trips: {total_trips}")
        print()
        
        if passengers_without_trip == 0:
            print("✅ All passengers already linked to trips!")
            return True
        
        # Load all trips into memory for faster matching
        print("📚 Loading all trips into memory...")
        all_trips = Trip.query.all()
        trip_lookup = {trip.name.lower(): trip for trip in all_trips if trip.name}
        print(f"   Loaded {len(trip_lookup)} trips with names")
        print()
        
        # Process passengers
        print("🔗 Linking passengers to trips...")
        print()
        
        linked_count = 0
        no_trip_name_count = 0
        no_match_count = 0
        already_linked_count = 0
        
        # Get passengers without trip_id but with trip_name
        passengers = Passenger.query.filter(
            Passenger.trip_id == None,
            Passenger.trip_name != None,
            Passenger.trip_name != ''
        ).all()
        
        unmatched_names = set()
        
        for i, passenger in enumerate(passengers, 1):
            try:
                trip_name = passenger.trip_name.strip()
                
                # Try exact match (case-insensitive)
                matching_trip = trip_lookup.get(trip_name.lower())
                
                # Try partial match if exact fails
                if not matching_trip:
                    for trip_key, trip in trip_lookup.items():
                        if trip_name.lower() in trip_key or trip_key in trip_name.lower():
                            matching_trip = trip
                            break
                
                if matching_trip:
                    passenger.trip_id = matching_trip.id
                    passenger.updated_at = datetime.utcnow()
                    db.session.add(passenger)
                    linked_count += 1
                    
                    if linked_count % 50 == 0:
                        print(f"   ✅ Linked {linked_count} passengers...")
                else:
                    no_match_count += 1
                    unmatched_names.add(trip_name)
                
                # Commit every 100 records
                if i % 100 == 0:
                    db.session.commit()
                    
            except Exception as e:
                print(f"   ❌ Error processing passenger {passenger.id}: {e}")
                db.session.rollback()
        
        # Final commit
        db.session.commit()
        
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"✅ Successfully linked: {linked_count} passengers")
        print(f"⚠️  No match found: {no_match_count} passengers")
        print()
        
        if unmatched_names and no_match_count <= 20:
            print("Unmatched trip names:")
            for name in sorted(unmatched_names)[:20]:
                print(f"   - {name}")
        
        # Verify final state
        remaining = Passenger.query.filter_by(trip_id=None).count()
        print()
        print(f"📊 Final Status:")
        print(f"   Passengers with trip_id: {total_passengers - remaining}")
        print(f"   Passengers still without trip_id: {remaining}")
        print()
        
        if remaining == 0:
            print("🎉 SUCCESS! All passengers are now linked to trips!")
        
        return True


def main():
    """Run all steps in sequence."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PASSENGER-TRIP COMPREHENSIVE LINKING" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Initialize GHL API
    api = GoHighLevelAPI(
        location_id=os.getenv('GHL_LOCATION_ID'),
        api_key=os.getenv('GHL_API_TOKEN')
    )
    
    try:
        # Step 1: Ensure field mapping
        ensure_trip_name_field_mapping()
        
        # Step 2: Sync trip names to GHL dropdown
        if not sync_trip_names_to_ghl_dropdown(api):
            print("⚠️  Warning: Could not update GHL dropdown, continuing anyway...")
            print()
        
        # Step 3: Re-sync passenger trip names
        resync_passenger_trip_names(api)
        
        # Step 4: Link passengers to trips
        link_passengers_to_trips()
        
        print()
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 24 + "ALL STEPS COMPLETE!" + " " * 25 + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        
    except Exception as e:
        print()
        print("❌ Fatal error occurred:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
