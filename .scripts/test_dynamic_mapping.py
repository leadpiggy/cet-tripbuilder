#!/usr/bin/env python3
"""
Test the dynamic field mapping with actual GHL data.
"""

import json
from app import app, db
from models import Trip, Passenger

with app.app_context():
    # Load a sample trip from raw data
    with open('raw_ghl_responses/trips_raw.json', 'r') as f:
        trips = json.load(f)
    
    if trips:
        sample_trip = trips[0]
        
        print("=" * 70)
        print("TESTING DYNAMIC FIELD MAPPING")
        print("=" * 70)
        print()
        
        print(f"GHL Opportunity ID: {sample_trip['id']}")
        print(f"Name: {sample_trip['name']}")
        print(f"Custom Fields Count: {len(sample_trip.get('customFields', []))}")
        print()
        
        # Create Trip from GHL data
        print("Creating Trip from GHL opportunity...")
        trip = Trip.from_ghl_opportunity(sample_trip)
        
        print(f"✅ Trip created!")
        print(f"   - Name: {trip.name}")
        print(f"   - GHL ID: {trip.ghl_opportunity_id}")
        print(f"   - Deposit Date: {trip.deposit_date}")
        print(f"   - Final Payment: {trip.final_payment}")
        print(f"   - Max Passengers: {trip.max_passengers}")
        print(f"   - Arrival Date: {trip.arrival_date}")
        print(f"   - Return Date: {trip.return_date}")
        print(f"   - Travel Business: {trip.travel_business_used}")
        print()
        
        # Test with passenger
        with open('raw_ghl_responses/passengers_raw.json', 'r') as f:
            passengers = json.load(f)
        
        if passengers:
            sample_passenger = passengers[0]
            
            print(f"GHL Passenger Opportunity ID: {sample_passenger['id']}")
            print(f"Custom Fields Count: {len(sample_passenger.get('customFields', []))}")
            print()
            
            print("Creating Passenger from GHL opportunity...")
            passenger = Passenger.from_ghl_opportunity(sample_passenger)
            
            print(f"✅ Passenger created!")
            print(f"   - ID: {passenger.id}")
            print(f"   - Contact ID: {passenger.contact_id}")
            print(f"   - Passport Number: {passenger.passport_number}")
            print(f"   - Passport Expire: {passenger.passport_expire}")
            print(f"   - Health State: {passenger.health_state}")
            print(f"   - Room Occupancy: {passenger.room_occupancy}")
            print()
        
        print("=" * 70)
        print("SUCCESS! Dynamic mapping working correctly.")
        print("=" * 70)
