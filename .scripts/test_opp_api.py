#!/usr/bin/env python3
"""Test script to check opportunity API response structure"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ghl_api import GoHighLevelAPI

# Load environment variables
load_dotenv()

# Initialize API
api = GoHighLevelAPI(
    location_id=os.getenv('GHL_LOCATION_ID'),
    api_key=os.getenv('GHL_API_KEY')
)

# Test trip opportunities
print("=" * 80)
print("Testing TripBooking Opportunities")
print("=" * 80)

TRIPBOOKING_PIPELINE_ID = "IlWdPtOpcczLpgsde2KF"

params = {
    'limit': 1,
    'location_id': api.location_id,
    'pipeline_id': TRIPBOOKING_PIPELINE_ID
}

try:
    response = api._make_request("GET", "opportunities/search", params=params)
    opportunities = response.get('opportunities', [])
    
    if opportunities:
        opp = opportunities[0]
        print(f"\nOpportunity ID: {opp.get('id')}")
        print(f"Name: {opp.get('name')}")
        print(f"Stage ID: {opp.get('stageId')}")
        print(f"Contact ID: {opp.get('contactId')}")
        print(f"\nCustom Fields Type: {type(opp.get('customFields'))}")
        print(f"Custom Fields:")
        print(json.dumps(opp.get('customFields'), indent=2))
    else:
        print("No opportunities found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test passenger opportunities
print("\n" + "=" * 80)
print("Testing Passenger Opportunities")
print("=" * 80)

PASSENGER_PIPELINE_ID = "fnsdpRtY9o83Vr4z15bE"

params = {
    'limit': 1,
    'location_id': api.location_id,
    'pipeline_id': PASSENGER_PIPELINE_ID
}

try:
    response = api._make_request("GET", "opportunities/search", params=params)
    opportunities = response.get('opportunities', [])
    
    if opportunities:
        opp = opportunities[0]
        print(f"\nOpportunity ID: {opp.get('id')}")
        print(f"Name: {opp.get('name')}")
        print(f"Stage ID: {opp.get('stageId')}")
        print(f"Contact ID: {opp.get('contactId')}")
        print(f"\nCustom Fields Type: {type(opp.get('customFields'))}")
        print(f"Custom Fields:")
        print(json.dumps(opp.get('customFields'), indent=2))
    else:
        print("No opportunities found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
