#!/usr/bin/env python3
"""Debug opportunities API response"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from ghl_api import GoHighLevelAPI
import json

with app.app_context():
    # Get API instance
    api = GoHighLevelAPI(
        location_id=os.getenv('GHL_LOCATION_ID'),
        api_key=os.getenv('GHL_API_KEY')
    )
    
    # Test with a single opportunity
    TRIPBOOKING_PIPELINE_ID = "IlWdPtOpcczLpgsde2KF"
    
    params = {
        'limit': 1,
        'location_id': api.location_id,
        'pipeline_id': TRIPBOOKING_PIPELINE_ID
    }
    
    try:
        response = api._make_request("GET", "opportunities/search", params=params)
        opps = response.get('opportunities', [])
        
        if opps:
            opp = opps[0]
            print("Sample TripBooking Opportunity:")
            print(json.dumps(opp, indent=2))
            print(f"\nCustom Fields type: {type(opp.get('customFields'))}")
        else:
            print("No trip opportunities found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
