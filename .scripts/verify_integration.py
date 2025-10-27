#!/usr/bin/env python3
"""
Verification script for field mapping integration.
Run this to verify that the updates were applied correctly.
"""

import os
import sys

print("=" * 70)
print("Field Mapping Integration Verification")
print("=" * 70)

# Check 1: File existence
print("\n1️⃣  Checking files exist...")
files_to_check = [
    ('services/ghl_sync.py', 'Sync service'),
    ('field_mapping.py', 'Field mapping utilities'),
    ('app.py', 'Flask app'),
    ('models.py', 'Database models'),
]

all_files_exist = True
for filepath, description in files_to_check:
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"   {status} {description}: {filepath}")
    if not exists:
        all_files_exist = False

if not all_files_exist:
    print("\n❌ Some files are missing. Make sure you're in the tripbuilder directory.")
    sys.exit(1)

# Check 2: Import field mapping
print("\n2️⃣  Checking field mapping module...")
try:
    from field_mapping import (
        parse_ghl_custom_fields, 
        map_trip_custom_fields, 
        map_passenger_custom_fields,
        TRIP_FIELD_MAP,
        PASSENGER_FIELD_MAP
    )
    print(f"   ✅ Module imports successfully")
    print(f"   ✅ TRIP_FIELD_MAP has {len(TRIP_FIELD_MAP)} mappings")
    print(f"   ✅ PASSENGER_FIELD_MAP has {len(PASSENGER_FIELD_MAP)} mappings")
except ImportError as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Check 3: Verify ghl_sync uses field mapping
print("\n3️⃣  Checking ghl_sync.py uses field mapping...")
with open('services/ghl_sync.py', 'r') as f:
    content = f.read()
    
checks = [
    ('from field_mapping import', 'Import statement'),
    ('parse_ghl_custom_fields', 'parse_ghl_custom_fields usage'),
    ('map_trip_custom_fields', 'map_trip_custom_fields usage'),
    ('map_passenger_custom_fields', 'map_passenger_custom_fields usage'),
]

all_checks_pass = True
for check_str, description in checks:
    found = check_str in content
    status = "✅" if found else "❌"
    print(f"   {status} {description}")
    if not found:
        all_checks_pass = False

if not all_checks_pass:
    print("\n❌ ghl_sync.py doesn't use field mapping. The file may not have been updated correctly.")
    sys.exit(1)

# Check 4: Verify app.py shows trips and passengers
print("\n4️⃣  Checking app.py displays trips and passengers...")
with open('app.py', 'r') as f:
    content = f.read()

checks = [
    ("print(f\"  Trips: {results.get('trips'", 'Trips output'),
    ("print(f\"  Passengers: {results.get('passengers'", 'Passengers output'),
]

all_checks_pass = True
for check_str, description in checks:
    found = check_str in content
    status = "✅" if found else "❌"
    print(f"   {status} {description}")
    if not found:
        all_checks_pass = False

if not all_checks_pass:
    print("\n❌ app.py doesn't display trips/passengers. The file may not have been updated correctly.")
    sys.exit(1)

# Check 5: Database models have required columns
print("\n5️⃣  Checking database models...")
try:
    from models import Trip, Passenger
    
    # Check Trip model has new columns
    trip_columns = [
        'arrival_date', 'return_date', 'max_passengers', 
        'trip_vendor', 'trip_standard_level_pricing'
    ]
    
    missing_trip_cols = []
    for col in trip_columns:
        if not hasattr(Trip, col):
            missing_trip_cols.append(col)
    
    if missing_trip_cols:
        print(f"   ❌ Trip model missing columns: {', '.join(missing_trip_cols)}")
        print("   ⚠️  You may need to run: python3 recreate_db.py")
    else:
        print(f"   ✅ Trip model has required columns")
    
    # Check Passenger model has new columns
    passenger_columns = [
        'passport_number', 'passport_country', 'health_state',
        'contact1_ufirst_name', 'room_occupancy'
    ]
    
    missing_passenger_cols = []
    for col in passenger_columns:
        if not hasattr(Passenger, col):
            missing_passenger_cols.append(col)
    
    if missing_passenger_cols:
        print(f"   ❌ Passenger model missing columns: {', '.join(missing_passenger_cols)}")
        print("   ⚠️  You may need to run: python3 recreate_db.py")
    else:
        print(f"   ✅ Passenger model has required columns")
        
except ImportError as e:
    print(f"   ❌ Failed to import models: {e}")
    sys.exit(1)

# Check 6: Environment variables
print("\n6️⃣  Checking environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    ghl_token = os.getenv('GHL_API_TOKEN')
    ghl_location = os.getenv('GHL_LOCATION_ID')
    
    if ghl_token:
        print(f"   ✅ GHL_API_TOKEN is set")
    else:
        print(f"   ❌ GHL_API_TOKEN is not set")
        
    if ghl_location:
        print(f"   ✅ GHL_LOCATION_ID is set")
    else:
        print(f"   ❌ GHL_LOCATION_ID is not set")
        
except Exception as e:
    print(f"   ⚠️  Could not check environment: {e}")

# Summary
print("\n" + "=" * 70)
print("✅ VERIFICATION COMPLETE!")
print("=" * 70)
print("\nNext steps:")
print("1. Make sure database is up to date:")
print("   python3 recreate_db.py")
print("")
print("2. Run the sync:")
print("   flask sync-ghl")
print("")
print("3. Verify data in database:")
print("   psql -U ridiculaptop -d tripbuilder")
print("   SELECT COUNT(*) FROM trips WHERE arrival_date IS NOT NULL;")
print("   SELECT COUNT(*) FROM passengers WHERE passport_number IS NOT NULL;")
print("")
print("Expected results:")
print("   - 2 pipelines, 11 stages")
print("   - 53 custom fields")
print("   - ~5,453 contacts")
print("   - ~693 trips (with all custom fields mapped!)")
print("   - ~6,477 passengers (with all custom fields mapped!)")
print("=" * 70)
