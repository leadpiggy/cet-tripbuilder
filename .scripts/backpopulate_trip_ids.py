#!/usr/bin/env python3
"""
Back-populate Trip IDs for Passengers - FIXED VERSION

This script fixes trip-passenger relationships using the actual data structure.
It reads from captured API responses to match passengers to trips.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Back-populate Trip IDs for Passengers (v2)")
print("=" * 60)

from app import app
from models import db, Trip, Passenger, Contact

# Find the latest sync capture
sync_captures_dir = 'sync_captures'
if not os.path.exists(sync_captures_dir):
    print(f"\n❌ No sync captures found in {sync_captures_dir}")
    exit(1)

captures = sorted([d for d in os.listdir(sync_captures_dir) if os.path.isdir(os.path.join(sync_captures_dir, d))])
if not captures:
    print(f"\n❌ No capture directories found")
    exit(1)

latest_capture = os.path.join(sync_captures_dir, captures[-1])
print(f"\n📁 Using capture: {latest_capture}")

# Load custom field definitions to get ID-to-key mapping
custom_fields_file = os.path.join(latest_capture, '001_custom_fields_opportunity.json')
if not os.path.exists(custom_fields_file):
    print(f"\n❌ Custom fields file not found")
    exit(1)

with open(custom_fields_file, 'r') as f:
    custom_fields_data = json.load(f)

# Build ID to fieldKey mapping
field_id_to_key = {}
for field in custom_fields_data.get('customFields', []):
    field_id_to_key[field['id']] = field['fieldKey']

print(f"\n✅ Loaded {len(field_id_to_key)} custom field mappings")

# Find trip_id and trip_name field IDs
trip_id_field_id = None
trip_name_field_id = None
for field_id, field_key in field_id_to_key.items():
    if field_key == 'opportunity.trip_id':
        trip_id_field_id = field_id
        print(f"   Found trip_id field: {field_id}")
    elif field_key == 'opportunity.trip_name':
        trip_name_field_id = field_id
        print(f"   Found trip_name field: {field_id}")

if not trip_id_field_id and not trip_name_field_id:
    print("\n⚠️  No trip_id or trip_name fields found in custom fields")
    print("   Will try to match passengers to trips by other means...")

# Load all passenger opportunities from captures
print("\n📦 Loading passenger opportunities from captures...")
passenger_opps = []
for filename in sorted(os.listdir(latest_capture)):
    if 'opportunities_fnsdpRtY9o83Vr4z15bE' in filename and filename.endswith('.json'):
        filepath = os.path.join(latest_capture, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            passenger_opps.extend(data.get('opportunities', []))

print(f"   ✅ Loaded {len(passenger_opps)} passenger opportunities")

# Create mapping of passenger GHL ID to trip info
passenger_trip_mapping = {}
for opp in passenger_opps:
    opp_id = opp.get('id')
    custom_fields = opp.get('customFields', [])
    
    trip_id_value = None
    trip_name_value = None
    
    # Extract trip info from custom fields
    for cf in custom_fields:
        if cf.get('id') == trip_id_field_id:
            trip_id_value = cf.get('fieldValueString')
        elif cf.get('id') == trip_name_field_id:
            trip_name_value = cf.get('fieldValueString')
    
    if trip_id_value or trip_name_value:
        passenger_trip_mapping[opp_id] = {
            'trip_id_value': trip_id_value,
            'trip_name_value': trip_name_value
        }

print(f"   ✅ Found trip info for {len(passenger_trip_mapping)} passengers")

# Now update the database
with app.app_context():
    print("\n📊 Current Status:")
    
    total_trips = Trip.query.count()
    total_passengers = Passenger.query.count()
    passengers_with_trip = Passenger.query.filter(Passenger.trip_id.isnot(None)).count()
    passengers_without_trip = total_passengers - passengers_with_trip
    
    print(f"   Total Trips: {total_trips}")
    print(f"   Total Passengers: {total_passengers}")
    print(f"   Passengers with trip_id: {passengers_with_trip}")
    print(f"   Passengers WITHOUT trip_id: {passengers_without_trip}")
    
    if passengers_without_trip == 0:
        print("\n✅ All passengers already have trip assignments!")
        exit(0)
    
    print("\n🔧 Attempting to match passengers to trips...")
    print("=" * 60)
    
    unmatched_passengers = Passenger.query.filter(Passenger.trip_id.is_(None)).all()
    
    matched_count = 0
    match_strategies = {
        'trip_ghl_id_exact': 0,
        'trip_name_exact': 0,
        'trip_name_fuzzy': 0,
        'no_match': 0
    }
    
    for passenger in unmatched_passengers:
        trip = None
        strategy = None
        
        # Get trip info from our mapping
        trip_info = passenger_trip_mapping.get(passenger.id, {})
        trip_id_value = trip_info.get('trip_id_value')
        trip_name_value = trip_info.get('trip_name_value')
        
        # Strategy 1: Match by GHL opportunity ID
        if trip_id_value:
            trip = Trip.query.filter_by(ghl_opportunity_id=trip_id_value).first()
            if trip:
                strategy = 'trip_ghl_id_exact'
        
        # Strategy 2: Exact match by trip name
        if not trip and trip_name_value and isinstance(trip_name_value, str) and len(trip_name_value) > 2:
            trip = Trip.query.filter(
                (Trip.name == trip_name_value) | (Trip.destination == trip_name_value)
            ).first()
            if trip:
                strategy = 'trip_name_exact'
        
        # Strategy 3: Fuzzy match by trip name
        if not trip and trip_name_value and isinstance(trip_name_value, str) and len(trip_name_value) > 2:
            trip = Trip.query.filter(
                Trip.name.ilike(f"%{trip_name_value}%") | Trip.destination.ilike(f"%{trip_name_value}%")
            ).first()
            if trip:
                strategy = 'trip_name_fuzzy'
        
        # Update passenger if we found a match
        if trip:
            passenger.trip_id = trip.id
            passenger.updated_at = datetime.utcnow()
            matched_count += 1
            match_strategies[strategy] += 1
            
            contact = Contact.query.get(passenger.contact_id)
            contact_name = f"{contact.firstname} {contact.lastname}" if contact else passenger.contact_id
            
            if matched_count <= 10:  # Only print first 10 to avoid spam
                print(f"   ✅ Matched: {contact_name} → {trip.name} (strategy: {strategy})")
        else:
            match_strategies['no_match'] += 1
            if match_strategies['no_match'] <= 5:  # Print first 5 failures
                print(f"   ❌ No match for passenger {passenger.id} (trip_id: {trip_id_value}, trip_name: {trip_name_value})")
    
    # Commit changes
    if matched_count > 0:
        try:
            db.session.commit()
            print(f"\n{'   ...' if matched_count > 10 else ''}")
            print("\n" + "=" * 60)
            print(f"✅ Successfully matched {matched_count} passengers to trips!")
            print("\nMatch Strategy Breakdown:")
            for strategy, count in match_strategies.items():
                if count > 0:
                    print(f"   {strategy}: {count}")
            
            # Updated stats
            passengers_with_trip = Passenger.query.filter(Passenger.trip_id.isnot(None)).count()
            passengers_without_trip = total_passengers - passengers_with_trip
            print(f"\n📊 Final Status:")
            print(f"   Passengers with trip_id: {passengers_with_trip}")
            print(f"   Passengers WITHOUT trip_id: {passengers_without_trip}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing changes: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠️  No passengers could be automatically matched to trips")
        print("\nPossible reasons:")
        print("   - Trip IDs in passenger records don't match any trip ghl_opportunity_id")
        print("   - Trip names in passenger records don't match trip destinations")
        print("   - Passenger opportunities don't have trip_id or trip_name fields set")
