#!/usr/bin/env python3
"""
Export ALL Passengers from GoHighLevel to Raw JSON

This script fetches all passenger opportunities from GHL with pagination
and saves them to raw_ghl_responses/passengers_raw.json

Usage:
    cd ~/Downloads/claude_code_tripbuilder/tripbuilder
    source ../.venv/bin/activate
    python3 export_all_passengers_raw.py
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from ghl_api import GoHighLevelAPI


def export_all_passengers():
    """Fetch all passenger opportunities with pagination"""
    print()
    print("=" * 70)
    print("EXPORT ALL PASSENGERS FROM GOHIGHLEVEL")
    print("=" * 70)
    print()
    
    api = GoHighLevelAPI(
        location_id=os.getenv('GHL_LOCATION_ID'),
        api_key=os.getenv('GHL_API_TOKEN')
    )
    
    # Get passenger pipeline ID
    print("🔍 Fetching pipelines...")
    pipelines = api.get_pipelines()
    
    passenger_pipeline = None
    for pipeline in pipelines.get('pipelines', []):
        if 'passenger' in pipeline.get('name', '').lower():
            passenger_pipeline = pipeline
            break
    
    if not passenger_pipeline:
        print("❌ Could not find Passenger pipeline")
        return
    
    print(f"✅ Found pipeline: {passenger_pipeline['name']}")
    print(f"   Pipeline ID: {passenger_pipeline['id']}")
    print()
    
    # Fetch all passengers with pagination
    print("📥 Fetching all passenger opportunities...")
    all_passengers = []
    page = 1
    limit = 100
    total_fetched = 0
    
    while True:
        print(f"   Page {page}... ", end='', flush=True)
        
        try:
            response = api.search_opportunities(
                pipeline_id=passenger_pipeline['id'],
                limit=limit,
                page=page
            )
            
            opportunities = response.get('opportunities', [])
            count = len(opportunities)
            
            if count == 0:
                print("Done!")
                break
            
            all_passengers.extend(opportunities)
            total_fetched += count
            print(f"Got {count} (Total: {total_fetched})")
            
            # If we got fewer than limit, we're done
            if count < limit:
                break
            
            page += 1
            
        except Exception as e:
            print(f"\n❌ Error on page {page}: {e}")
            break
    
    print()
    print(f"✅ Fetched {total_fetched} total passenger opportunities")
    print()
    
    # Save to raw JSON file
    output_path = os.path.expanduser(
        '~/Downloads/claude_code_tripbuilder/tripbuilder/raw_ghl_responses/passengers_raw.json'
    )
    
    print(f"💾 Saving to: {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(all_passengers, f, indent=2, default=str)
    
    print(f"✅ Saved {total_fetched} passenger records")
    print()
    
    # Summary
    print("=" * 70)
    print("EXPORT COMPLETE!")
    print("=" * 70)
    print()
    print(f"📊 Total passengers exported: {total_fetched}")
    print(f"📁 File: {output_path}")
    print()
    print("Next steps:")
    print("1. Run: python3 link_passengers_from_raw_json.py")
    print()


if __name__ == '__main__':
    export_all_passengers()
