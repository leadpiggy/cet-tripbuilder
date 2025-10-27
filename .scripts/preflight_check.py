#!/usr/bin/env python3
"""
Pre-Flight Check for Passenger-Trip Linking

Verifies that everything is set up correctly before running the linking script.

Usage:
    python3 preflight_check.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_env_vars():
    """Check required environment variables"""
    print("1️⃣  Checking environment variables...")
    
    required_vars = ['GHL_LOCATION_ID', 'GHL_API_TOKEN', 'DATABASE_URL']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"   ❌ {var}: NOT SET")
        else:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked}")
    
    if missing:
        print()
        print(f"   ⚠️  Missing: {', '.join(missing)}")
        return False
    
    print()
    return True


def check_raw_json():
    """Check if raw JSON file exists"""
    print("2️⃣  Checking for raw JSON file...")
    
    json_path = Path.home() / 'Downloads' / 'claude_code_tripbuilder' / 'tripbuilder' / 'raw_ghl_responses' / 'passengers_raw.json'
    
    if json_path.exists():
        size_mb = json_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ File found: {json_path}")
        print(f"   📊 Size: {size_mb:.2f} MB")
        print()
        return True
    else:
        print(f"   ❌ File not found: {json_path}")
        print()
        print("   Options:")
        print("   A) Export passenger data from GHL and save to this path")
        print("   B) Update the path in link_passengers_from_raw_json.py (line 62-64)")
        print()
        return False


def check_database_tables():
    """Check if database tables have required columns"""
    print("3️⃣  Checking database schema...")
    
    try:
        from app import app, db
        from sqlalchemy import text, inspect
        
        with app.app_context():
            inspector = inspect(db.engine)
            
            # Check trips table
            if 'trips' in inspector.get_table_names():
                trips_columns = [col['name'] for col in inspector.get_columns('trips')]
                
                if 'name' in trips_columns:
                    print("   ✅ trips.name column exists")
                else:
                    print("   ❌ trips.name column missing")
                    print("      Run: python3 migrate_add_trip_columns.py")
                    return False
            else:
                print("   ❌ trips table not found")
                return False
            
            # Check passengers table
            if 'passengers' in inspector.get_table_names():
                passengers_columns = [col['name'] for col in inspector.get_columns('passengers')]
                
                if 'trip_name' in passengers_columns:
                    print("   ✅ passengers.trip_name column exists")
                else:
                    print("   ❌ passengers.trip_name column missing")
                    print("      Run: python3 migrate_add_trip_columns.py")
                    return False
            else:
                print("   ❌ passengers table not found")
                return False
            
            # Check field_maps table
            if 'field_maps' in inspector.get_table_names():
                print("   ✅ field_maps table exists")
            else:
                print("   ⚠️  field_maps table missing (will be created)")
            
            print()
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        print()
        return False


def check_database_data():
    """Check database has data"""
    print("4️⃣  Checking database data...")
    
    try:
        from app import app
        from models import Trip, Passenger, Contact
        
        with app.app_context():
            trip_count = Trip.query.count()
            passenger_count = Passenger.query.count()
            contact_count = Contact.query.count()
            
            print(f"   📊 Trips: {trip_count}")
            print(f"   📊 Passengers: {passenger_count}")
            print(f"   📊 Contacts: {contact_count}")
            print()
            
            if trip_count == 0:
                print("   ⚠️  No trips in database")
                print("      Consider syncing trips first")
                print()
            
            if passenger_count == 0:
                print("   ⚠️  No passengers in database")
                print("      Consider syncing passengers first")
                print()
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error checking data: {e}")
        print()
        return False


def main():
    """Run all checks"""
    print()
    print("═" * 70)
    print("PRE-FLIGHT CHECK - Passenger-Trip Linking")
    print("═" * 70)
    print()
    
    checks = [
        ("Environment Variables", check_env_vars),
        ("Raw JSON File", check_raw_json),
        ("Database Schema", check_database_tables),
        ("Database Data", check_database_data),
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"   ❌ {check_name} check failed: {e}")
            results[check_name] = False
            print()
    
    print()
    print("═" * 70)
    print("SUMMARY")
    print("═" * 70)
    print()
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {check_name}")
    
    print()
    
    if all_passed:
        print("🎉 All checks passed!")
        print()
        print("Ready to run:")
        print("   python3 link_passengers_from_raw_json.py")
        print()
    else:
        print("⚠️  Some checks failed")
        print()
        print("Please fix the issues above before proceeding.")
        print()
        
        # Give specific guidance
        if not results.get("Database Schema"):
            print("To fix database schema:")
            print("   python3 migrate_add_trip_columns.py")
            print()
        
        if not results.get("Raw JSON File"):
            print("To fix raw JSON file:")
            print("   1. Export passenger data from GoHighLevel")
            print("   2. Save to: ~/Downloads/claude_code_tripbuilder/tripbuilder/raw_ghl_responses/passengers_raw.json")
            print("   OR update path in link_passengers_from_raw_json.py")
            print()


if __name__ == '__main__':
    main()
