#!/usr/bin/env python3
"""
Link passengers to trips by matching trip names.

This script:
1. Finds passengers without trip_id
2. Fetches their opportunity data from GHL to get trip_name
3. Matches trip_name against trips.name
4. Updates passenger records with matching trip_id
"""

import os
from dotenv import load_dotenv
from sqlalchemy import func

load_dotenv()

from app import app
from models import db, Passenger, Trip
from ghl_api import GoHighLevelAPI


def get_trip_name_from_opportunity(api, opportunity_id):
    """
    Fetch opportunity from GHL and extract trip_name custom field.
    
    Args:
        api: GoHighLevelAPI instance
        opportunity_id: GHL opportunity ID
    
    Returns:
        str: Trip name or None
    """
    try:
        # Fetch the opportunity
        response = api._make_request("GET", f"opportunities/{opportunity_id}")
        
        if 'opportunity' in response:
            opportunity = response['opportunity']
            custom_fields = opportunity.get('customFields', [])
            
            # Look for trip_name field (GHL field ID: tJoung7L6ymp1vHmU2Tq)
            for field in custom_fields:
                if field.get('id') == 'tJoung7L6ymp1vHmU2Tq':
                    # Get the value
                    trip_name = (field.get('fieldValue') or 
                               field.get('fieldValueString') or 
                               field.get('value'))
                    return trip_name
        
        return None
        
    except Exception as e:
        print(f"  ⚠️  Error fetching opportunity {opportunity_id}: {e}")
        return None


def find_matching_trip(trip_name, all_trips):
    """
    Find a trip that matches the given trip name.
    
    Uses fuzzy matching with ILIKE for case-insensitive partial matches.
    
    Args:
        trip_name: Trip name to search for
        all_trips: List of all Trip objects
    
    Returns:
        Trip: Matching trip or None
    """
    if not trip_name:
        return None
    
    trip_name = str(trip_name).strip()
    if len(trip_name) < 3:  # Skip very short names
        return None
    
    # First try exact match (case-insensitive)
    for trip in all_trips:
        if trip.name and trip.name.lower() == trip_name.lower():
            return trip
    
    # Then try partial match
    for trip in all_trips:
        if trip.name and trip_name.lower() in trip.name.lower():
            return trip
    
    # Finally try reverse partial match
    for trip in all_trips:
        if trip.name and trip.name.lower() in trip_name.lower():
            return trip
    
    return None


def link_passengers_to_trips():
    """Main function to link passengers to trips."""
    
    print("=" * 70)
    print("PASSENGER-TRIP LINKING SCRIPT")
    print("=" * 70)
    print()
    
    # Initialize GHL API
    api = GoHighLevelAPI(
        location_id=os.getenv('GHL_LOCATION_ID'),
        api_key=os.getenv('GHL_API_TOKEN')
    )
    
    with app.app_context():
        # Get counts
        total_passengers = Passenger.query.count()
        passengers_without_trip = Passenger.query.filter_by(trip_id=None).count()
        total_trips = Trip.query.count()
        
        print(f"📊 Database Status:")
        print(f"   Total Passengers: {total_passengers}")
        print(f"   Passengers without trip_id: {passengers_without_trip}")
        print(f"   Total Trips: {total_trips}")
        print()
        
        if passengers_without_trip == 0:
            print("✅ All passengers are already linked to trips!")
            return
        
        # Load all trips into memory for faster matching
        print("📚 Loading all trips into memory...")
        all_trips = Trip.query.all()
        print(f"   Loaded {len(all_trips)} trips")
        print()
        
        # Process passengers in batches
        batch_size = 100
        linked_count = 0
        not_found_count = 0
        error_count = 0
        
        print(f"🔗 Starting to link passengers (batch size: {batch_size})...")
        print()
        
        # Get all passengers without trip_id
        passengers = Passenger.query.filter_by(trip_id=None).all()
        
        for i, passenger in enumerate(passengers, 1):
            try:
                # Fetch trip name from GHL
                trip_name = get_trip_name_from_opportunity(api, passenger.id)
                
                if trip_name:
                    # Try to find matching trip
                    matching_trip = find_matching_trip(trip_name, all_trips)
                    
                    if matching_trip:
                        passenger.trip_id = matching_trip.id
                        db.session.add(passenger)
                        linked_count += 1
                        
                        if linked_count % 10 == 0:
                            print(f"   ✅ Linked {linked_count} passengers...")
                    else:
                        not_found_count += 1
                        if not_found_count <= 10:  # Only show first 10
                            print(f"   ⚠️  No trip match for: '{trip_name}' (passenger {passenger.id})")
                else:
                    not_found_count += 1
                
                # Commit every batch_size records
                if i % batch_size == 0:
                    db.session.commit()
                    print(f"   💾 Committed batch (processed {i}/{len(passengers)})")
                    
            except Exception as e:
                error_count += 1
                print(f"   ❌ Error processing passenger {passenger.id}: {e}")
                db.session.rollback()
        
        # Final commit
        db.session.commit()
        
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"✅ Successfully linked: {linked_count} passengers")
        print(f"⚠️  No match found: {not_found_count} passengers")
        print(f"❌ Errors: {error_count}")
        print()
        
        # Verify final state
        remaining = Passenger.query.filter_by(trip_id=None).count()
        print(f"📊 Final Status:")
        print(f"   Passengers still without trip_id: {remaining}")
        print(f"   Passengers with trip_id: {total_passengers - remaining}")
        print()
        
        if remaining == 0:
            print("🎉 SUCCESS! All passengers are now linked to trips!")
        else:
            print(f"ℹ️  {remaining} passengers could not be linked (no matching trip name found)")


if __name__ == '__main__':
    link_passengers_to_trips()
