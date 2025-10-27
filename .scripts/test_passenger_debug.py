#!/usr/bin/env python3
"""Quick test to sync passengers with debug output"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import app, db
from ghl_api import GoHighLevelAPI
from services.ghl_sync import GHLSyncService

with app.app_context():
    # Initialize API
    api = GoHighLevelAPI(
        location_id=os.getenv('GHL_LOCATION_ID'),
        api_key=os.getenv('GHL_API_KEY')
    )
    
    # Initialize sync service
    sync_service = GHLSyncService(api)
    
    # Get first passenger opportunity to debug
    PASSENGER_PIPELINE_ID = "fnsdpRtY9o83Vr4z15bE"
    
    response = api.search_opportunities(pipeline_id=PASSENGER_PIPELINE_ID, limit=1)
    opps = response.get('opportunities', [])
    
    if opps:
        opp = opps[0]
        print("Sample Passenger Opportunity:")
        print(f"  ID: {opp.get('id')}")
        print(f"  Name: {opp.get('name')}")
        print(f"  Contact ID: {opp.get('contactId')}")
        print(f"\n  Custom Fields (first 5):")
        for i, field in enumerate(opp.get('custom_fields', [])[:5]):
            print(f"    {i+1}. id={field.get('id')}, value={field.get('fieldValue')}")
