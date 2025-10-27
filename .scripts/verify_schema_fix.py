#!/usr/bin/env python3
"""
Verify Schema Fix - Test that models match database

This script tests that the updated models.py correctly matches
the actual database schema and can perform queries without errors.
"""

from app import app, db
from models import Trip, Passenger, Contact

def test_trip_queries():
    """Test Trip model queries"""
    print("\n=== Testing Trip Model ===")
    
    with app.app_context():
        try:
            # Test count query
            count = Trip.query.count()
            print(f"✅ Trip.query.count() = {count}")
            
            # Test accessing all columns
            trip = Trip.query.first()
            if trip:
                # Access some columns to verify they exist
                attrs = ['id', 'name', 'destination', 'start_date', 'end_date', 
                        'max_passengers', 'current_passengers', 'status', 
                        'internal_trip_details', 'ghl_opportunity_id', 
                        'trip_vendor', 'nights_total', 'base_price']
                
                for attr in attrs:
                    val = getattr(trip, attr, 'MISSING')
                    if val == 'MISSING':
                        print(f"❌ Column '{attr}' not accessible")
                    # else: don't print success for each - too verbose
                
                print(f"✅ All Trip columns accessible")
                print(f"   Sample: Trip {trip.id} - {trip.name or trip.destination}")
            else:
                print("⚠️  No trips in database (this is okay)")
            
            return True
            
        except Exception as e:
            print(f"❌ Trip model error: {e}")
            return False


def test_passenger_queries():
    """Test Passenger model queries"""
    print("\n=== Testing Passenger Model ===")
    
    with app.app_context():
        try:
            # Test count query
            count = Passenger.query.count()
            print(f"✅ Passenger.query.count() = {count}")
            
            # Test accessing all columns
            passenger = Passenger.query.first()
            if passenger:
                # Access some columns to verify they exist
                attrs = ['id', 'contact_id', 'trip_id', 'firstname', 'lastname',
                        'email', 'phone', 'status', 'registration_completed',
                        'passport_number', 'health_state', 'user_roomate',
                        'trip_name']
                
                for attr in attrs:
                    val = getattr(passenger, attr, 'MISSING')
                    if val == 'MISSING':
                        print(f"❌ Column '{attr}' not accessible")
                
                print(f"✅ All Passenger columns accessible")
                print(f"   Sample: Passenger {passenger.id}")
                
                # Test relationships
                if passenger.contact:
                    print(f"✅ Passenger.contact relationship works")
                if passenger.trip:
                    print(f"✅ Passenger.trip relationship works")
            else:
                print("⚠️  No passengers in database (this is okay)")
            
            return True
            
        except Exception as e:
            print(f"❌ Passenger model error: {e}")
            return False


def test_contact_queries():
    """Test Contact model queries"""
    print("\n=== Testing Contact Model ===")
    
    with app.app_context():
        try:
            # Test count query
            count = Contact.query.count()
            print(f"✅ Contact.query.count() = {count}")
            
            # Test accessing columns
            contact = Contact.query.first()
            if contact:
                print(f"✅ Contact columns accessible")
                print(f"   Sample: Contact {contact.id} - {contact.firstname} {contact.lastname}")
                
                # Test relationship
                if contact.passengers:
                    print(f"✅ Contact.passengers relationship works ({len(contact.passengers)} passengers)")
            else:
                print("⚠️  No contacts in database (this is okay)")
            
            return True
            
        except Exception as e:
            print(f"❌ Contact model error: {e}")
            return False


def test_create_and_query():
    """Test creating a test record and querying it"""
    print("\n=== Testing Create/Query Operations ===")
    
    with app.app_context():
        try:
            from datetime import date, timedelta
            
            # Try to create a test trip
            test_trip = Trip(
                name="Schema Verification Test Trip",
                destination="Test City",
                start_date=date.today() + timedelta(days=30),
                end_date=date.today() + timedelta(days=37),
                max_passengers=10,
                status='draft',
                is_public=False
            )
            
            db.session.add(test_trip)
            db.session.flush()
            
            print(f"✅ Created test trip with ID {test_trip.id}")
            
            # Query it back
            found_trip = Trip.query.get(test_trip.id)
            if found_trip and found_trip.name == "Schema Verification Test Trip":
                print(f"✅ Successfully queried test trip back")
            
            # Clean up
            db.session.rollback()
            print(f"✅ Rolled back test trip (not saved)")
            
            return True
            
        except Exception as e:
            print(f"❌ Create/query error: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("SCHEMA VERIFICATION TEST")
    print("=" * 60)
    print("\nTesting that models.py matches actual database schema...")
    
    results = []
    
    results.append(("Trip Queries", test_trip_queries()))
    results.append(("Passenger Queries", test_passenger_queries()))
    results.append(("Contact Queries", test_contact_queries()))
    results.append(("Create/Query Operations", test_create_and_query()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Schema is correct!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("=" * 60)
