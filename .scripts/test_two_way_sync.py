#!/usr/bin/env python3
"""
Test Two-Way Sync Functionality

This script tests the bidirectional sync between local database and GoHighLevel.
"""

from app import app, db, ghl_api
from services.two_way_sync import TwoWaySyncService
from models import Trip, Passenger, Contact
from datetime import date, timedelta

def test_trip_sync():
    """Test trip creation and sync to GHL"""
    print("\n" + "="*60)
    print("TEST 1: Trip Creation & Sync to GHL")
    print("="*60)
    
    with app.app_context():
        sync_service = TwoWaySyncService(ghl_api)
        
        # Create a test trip
        trip = Trip(
            name="Test Sync Trip",
            destination="Paris, France",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=37),
            max_capacity=15,
            internal_trip_details="This is a test trip for sync verification"
        )
        
        db.session.add(trip)
        db.session.flush()
        
        print(f"\n✅ Created Trip locally: {trip.name} (ID: {trip.id})")
        print(f"   GHL Opportunity ID: {trip.ghl_opportunity_id}")
        
        # Push to GHL
        try:
            response = sync_service.push_trip_to_ghl(trip)
            db.session.commit()
            
            print(f"\n✅ Synced to GHL!")
            print(f"   GHL Opportunity ID: {trip.ghl_opportunity_id}")
            print(f"   Response: {response.get('id')}")
            
            return trip
        except Exception as e:
            print(f"\n❌ Sync failed: {e}")
            db.session.rollback()
            return None


def test_trip_update_sync(trip):
    """Test trip update and sync to GHL"""
    print("\n" + "="*60)
    print("TEST 2: Trip Update & Sync to GHL")
    print("="*60)
    
    with app.app_context():
        sync_service = TwoWaySyncService(ghl_api)
        
        # Update the trip
        trip = Trip.query.get(trip.id)
        trip.internal_trip_details = "Updated: This trip has been modified"
        trip.max_capacity = 20
        
        print(f"\n📝 Updating Trip: {trip.name}")
        print(f"   New max capacity: {trip.max_capacity}")
        
        # Push update to GHL
        try:
            response = sync_service.push_trip_to_ghl(trip)
            db.session.commit()
            
            print(f"\n✅ Update synced to GHL!")
            return True
        except Exception as e:
            print(f"\n❌ Update sync failed: {e}")
            return False


def test_passenger_sync(trip):
    """Test passenger creation and sync to GHL"""
    print("\n" + "="*60)
    print("TEST 3: Passenger Creation & Sync to GHL")
    print("="*60)
    
    with app.app_context():
        sync_service = TwoWaySyncService(ghl_api)
        
        # Create or get test contact
        contact = Contact.query.filter_by(email='test.sync@example.com').first()
        
        if not contact:
            contact = Contact(
                id=f"test_contact_{int(date.today().timestamp())}",
                firstname="Test",
                lastname="Passenger",
                email="test.sync@example.com",
                phone="+15551234567"
            )
            db.session.add(contact)
            db.session.flush()
            
            # Sync contact to GHL
            try:
                sync_service.push_contact_to_ghl(contact)
                print(f"\n✅ Created Contact: {contact.firstname} {contact.lastname}")
            except Exception as e:
                print(f"\n⚠️  Contact sync warning: {e}")
        
        # Create passenger
        trip = Trip.query.get(trip.id)
        passenger = Passenger(
            contact_id=contact.id,
            trip_id=trip.id,
            trip_name=trip.name
        )
        
        db.session.add(passenger)
        db.session.flush()
        
        print(f"\n✅ Created Passenger locally for: {contact.firstname} {contact.lastname}")
        
        # Push to GHL
        try:
            response = sync_service.push_passenger_to_ghl(passenger)
            db.session.commit()
            
            print(f"\n✅ Passenger synced to GHL!")
            print(f"   GHL Opportunity ID: {passenger.id}")
            
            return passenger
        except Exception as e:
            print(f"\n❌ Passenger sync failed: {e}")
            db.session.rollback()
            return None


def test_pull_from_ghl():
    """Test pulling data from GHL to local"""
    print("\n" + "="*60)
    print("TEST 4: Pull Data from GHL to Local")
    print("="*60)
    
    with app.app_context():
        sync_service = TwoWaySyncService(ghl_api)
        
        # Find a trip with GHL ID
        trip = Trip.query.filter(Trip.ghl_opportunity_id.isnot(None)).first()
        
        if not trip:
            print("\n⚠️  No trips with GHL IDs found. Skipping pull test.")
            return
        
        print(f"\n📥 Pulling Trip {trip.ghl_opportunity_id} from GHL...")
        
        try:
            updated_trip = sync_service.pull_trip_from_ghl(trip.ghl_opportunity_id)
            print(f"\n✅ Successfully pulled and updated Trip: {updated_trip.name}")
        except Exception as e:
            print(f"\n❌ Pull failed: {e}")


def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*60)
    print("CLEANUP: Removing Test Data")
    print("="*60)
    
    response = input("\nDo you want to delete the test trip and passenger? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cleanup cancelled.")
        return
    
    with app.app_context():
        # Delete test trips
        test_trips = Trip.query.filter(Trip.name.like('%Test Sync%')).all()
        
        for trip in test_trips:
            # Delete from GHL first
            if trip.ghl_opportunity_id:
                try:
                    ghl_api.delete_opportunity(trip.ghl_opportunity_id)
                    print(f"✅ Deleted Trip opportunity from GHL: {trip.ghl_opportunity_id}")
                except Exception as e:
                    print(f"⚠️  Failed to delete from GHL: {e}")
            
            # Delete passengers
            for passenger in trip.passengers:
                if passenger.id:
                    try:
                        ghl_api.delete_opportunity(passenger.id)
                        print(f"✅ Deleted Passenger opportunity from GHL: {passenger.id}")
                    except Exception as e:
                        print(f"⚠️  Failed to delete passenger from GHL: {e}")
            
            # Delete from database
            db.session.delete(trip)
            print(f"✅ Deleted Trip from database: {trip.name}")
        
        # Delete test contact
        test_contact = Contact.query.filter_by(email='test.sync@example.com').first()
        if test_contact:
            try:
                ghl_api.delete_contact(test_contact.id)
                print(f"✅ Deleted Contact from GHL: {test_contact.email}")
            except:
                pass
            
            db.session.delete(test_contact)
            print(f"✅ Deleted Contact from database: {test_contact.email}")
        
        db.session.commit()
        print("\n✅ Cleanup complete!")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("TWO-WAY SYNC TEST SUITE")
    print("="*60)
    print("\nThis will test bidirectional sync between local database and GHL.")
    print("Make sure your .env file has valid GHL credentials.\n")
    
    response = input("Proceed with tests? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Tests cancelled.")
        exit(0)
    
    # Run tests
    trip = test_trip_sync()
    
    if trip:
        test_trip_update_sync(trip)
        test_passenger_sync(trip)
        test_pull_from_ghl()
        cleanup_test_data()
    else:
        print("\n❌ Trip sync failed. Skipping remaining tests.")
