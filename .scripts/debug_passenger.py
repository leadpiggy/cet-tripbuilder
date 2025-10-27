#!/usr/bin/env python3
"""Debug passenger opportunity structure"""

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
    
    # Get one passenger opportunity
    PASSENGER_PIPELINE_ID = "fnsdpRtY9o83Vr4z15bE"
    
    response = api.search_opportunities(pipeline_id=PASSENGER_PIPELINE_ID, limit=1)
    opps = response.get('opportunities', [])
    
    if opps:
        opp = opps[0]
        print("Sample Passenger Opportunity:")
        print(f"ID: {opp.get('id')}")
        print(f"Name: {opp.get('name')}")
        print(f"Contact ID: {opp.get('contactId')}")
        print(f"\nCustom Fields type: {type(opp.get('custom_fields'))}")
        print(f"Custom Fields:")
        print(json.dumps(opp.get('custom_fields'), indent=2))
    else:
        print("No passenger opportunities found")
