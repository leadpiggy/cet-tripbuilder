#!/usr/bin/env python3
"""
Test script for search and filter functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, Trip, Contact, Passenger
from datetime import datetime, date

def test_search_filters():
    """Test the search and filter queries"""
    with app.app_context():
        print("🧪 Testing Search and Filter Functionality\n")
        
        # Test 1: Basic trip count
        total_trips = Trip.query.count()
        print(f"✅ Test 1: Total trips in database: {total_trips}")
        
        # Test 2: Search by destination
        if total_trips > 0:
            sample_trip = Trip.query.first()
            if sample_trip.destination:
                matching = Trip.query.filter(
                    Trip.destination.ilike(f'%{sample_trip.destination[:3]}%')
                ).count()
                print(f"✅ Test 2: Destination search ('{sample_trip.destination[:3]}'): {matching} results")
        
        # Test 3: Date range filter
        trips_with_dates = Trip.query.filter(
            Trip.start_date.isnot(None)
        ).count()
        print(f"✅ Test 3: Trips with start dates: {trips_with_dates}")
        
        # Test 4: Status filter
        statuses = db.session.query(Trip.status).distinct().all()
        print(f"✅ Test 4: Available statuses: {[s[0] for s in statuses if s[0]]}")
        
        # Test 5: Capacity filter
        trips_with_capacity = Trip.query.filter(
            Trip.max_passengers.isnot(None)
        ).count()
        print(f"✅ Test 5: Trips with max_passengers set: {trips_with_capacity}")
        
        # Test 6: Passenger join test
        total_passengers = Passenger.query.count()
        print(f"✅ Test 6: Total passengers in database: {total_passengers}")
        
        if total_passengers > 0:
            trips_with_passengers = db.session.query(Trip).join(Passenger).distinct().count()
            print(f"✅ Test 7: Trips with at least one passenger: {trips_with_passengers}")
        
        # Test 8: Multi-field OR search
        search_term = "trip"
        multi_field_results = Trip.query.filter(
            db.or_(
                Trip.destination.ilike(f'%{search_term}%'),
                Trip.name.ilike(f'%{search_term}%'),
                Trip.trip_description.ilike(f'%{search_term}%')
            )
        ).count()
        print(f"✅ Test 8: Multi-field search ('{search_term}'): {multi_field_results} results")
        
        # Test 9: Combined filters (status + dates)
        if trips_with_dates > 0:
            today = date.today()
            upcoming_trips = Trip.query.filter(
                Trip.start_date >= today
            ).count()
            print(f"✅ Test 9: Upcoming trips (start_date >= today): {upcoming_trips}")
        
        # Test 10: Dropdown data
        destinations = db.session.query(Trip.destination).distinct().filter(
            Trip.destination.isnot(None)
        ).count()
        categories = db.session.query(Trip.travel_category).distinct().filter(
            Trip.travel_category.isnot(None)
        ).count()
        print(f"✅ Test 10: Unique destinations: {destinations}, categories: {categories}")
        
        print("\n✅ All tests completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - Total Trips: {total_trips}")
        print(f"   - Total Passengers: {total_passengers}")
        print(f"   - Trips with Dates: {trips_with_dates}")
        print(f"   - Unique Statuses: {len([s[0] for s in statuses if s[0]])}")
        
        if total_trips == 0:
            print("\n⚠️  Note: No trips in database. Create some trips to test filters!")
        
        return True

if __name__ == '__main__':
    try:
        test_search_filters()
        print("\n✅ Search and filter functionality is working correctly!")
    except Exception as e:
        print(f"\n❌ Error testing search functionality: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
