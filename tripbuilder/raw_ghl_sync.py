#!/usr/bin/env python3
"""
RAW GHL Sync - Fetch Unconverted Responses

This script fetches data from GHL and saves it RAW (unconverted) to JSON files.
The purpose is to see the ACTUAL structure GHL uses, not a converted version.

This helps debug field mapping issues by showing:
- The actual field keys GHL uses (with underscores!)
- The actual structure of customFields arrays
- The actual data types and formats

Output files in raw_ghl_responses/:
- contacts_raw.json - All contacts as GHL returns them
- trips_raw.json - All trip opportunities as GHL returns them  
- passengers_raw.json - All passenger opportunities as GHL returns them
- custom_fields_raw.json - All custom field definitions
- sync_summary.json - Summary counts
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from ghl_api import GoHighLevelAPI


def save_json(data, filename):
    """Save data to JSON file with pretty formatting"""
    output_dir = Path('raw_ghl_responses')
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"✅ Saved to {filepath}")
    return filepath


def fetch_all_paginated(api, fetch_function, result_key, **kwargs):
    """Fetch all results from a paginated endpoint"""
    all_results = []
    limit = 100
    offset = 0
    
    while True:
        print(f"  Fetching {result_key} (offset={offset})...")
        response = fetch_function(limit=limit, offset=offset, **kwargs)
        
        items = response.get(result_key, [])
        if not items:
            break
        
        all_results.extend(items)
        
        # Check if we got fewer results than the limit (last page)
        if len(items) < limit:
            break
        
        offset += len(items)
    
    return all_results


def main():
    """Main sync function"""
    print("=" * 70)
    print("RAW GHL SYNC - Fetching Unconverted Data")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Get GHL credentials from config
        location_id = os.getenv('GHL_LOCATION_ID')
        api_key = os.getenv('GHL_API_TOKEN')
        
        if not location_id or not api_key:
            print("❌ ERROR: GHL_LOCATION_ID and GHL_API_TOKEN must be set in environment")
            print("   Check your .env file")
            sys.exit(1)
        
        print(f"📍 Location ID: {location_id}")
        print(f"🔑 API Key: {api_key[:20]}...")
        print()
        
        # Initialize API
        api = GoHighLevelAPI(location_id=location_id, api_key=api_key)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'location_id': location_id,
            'counts': {}
        }
        
        # 1. Fetch Custom Fields (to see actual field keys)
        print("1️⃣  Fetching custom field definitions...")
        try:
            custom_fields_response = api.get_custom_fields(model='opportunity')
            custom_fields = custom_fields_response.get('customFields', [])
            
            save_json(custom_fields_response, 'custom_fields_raw.json')
            summary['counts']['custom_fields'] = len(custom_fields)
            print(f"   Found {len(custom_fields)} custom fields")
            
            # Print sample field keys to verify underscores
            print("\n   Sample field keys:")
            for field in custom_fields[:5]:
                field_key = field.get('fieldKey', 'N/A')
                name = field.get('name', 'N/A')
                print(f"     - {field_key} ({name})")
        except Exception as e:
            print(f"❌ Error fetching custom fields: {e}")
            summary['errors'] = summary.get('errors', [])
            summary['errors'].append(f"Custom fields: {str(e)}")
        
        print()
        
        # 2. Fetch Contacts
        print("2️⃣  Fetching all contacts...")
        try:
            contacts = fetch_all_paginated(api, api.search_contacts, 'contacts')
            
            save_json(contacts, 'contacts_raw.json')
            summary['counts']['contacts'] = len(contacts)
            print(f"   ✅ Fetched {len(contacts)} contacts")
        except Exception as e:
            print(f"❌ Error fetching contacts: {e}")
            summary['errors'] = summary.get('errors', [])
            summary['errors'].append(f"Contacts: {str(e)}")
        
        print()
        
        # 3. Fetch Pipelines to get pipeline/stage IDs
        print("3️⃣  Fetching pipelines...")
        try:
            pipelines_response = api.get_pipelines()
            pipelines = pipelines_response.get('pipelines', [])
            
            print(f"   Found {len(pipelines)} pipelines")
            
            trip_pipeline = None
            passenger_pipeline = None
            
            for pipeline in pipelines:
                name = pipeline.get('name', '')
                print(f"     - {name} (ID: {pipeline.get('id')})")
                
                if 'trip' in name.lower() and 'booking' in name.lower():
                    trip_pipeline = pipeline
                elif 'passenger' in name.lower():
                    passenger_pipeline = pipeline
            
            summary['pipelines'] = {
                'trip': trip_pipeline.get('id') if trip_pipeline else None,
                'passenger': passenger_pipeline.get('id') if passenger_pipeline else None
            }
        except Exception as e:
            print(f"❌ Error fetching pipelines: {e}")
            summary['errors'] = summary.get('errors', [])
            summary['errors'].append(f"Pipelines: {str(e)}")
            trip_pipeline = None
            passenger_pipeline = None
        
        print()
        
        # 4. Fetch Trip Opportunities
        if trip_pipeline:
            print("4️⃣  Fetching Trip opportunities...")
            try:
                trips_response = api.search_opportunities(pipeline_id=trip_pipeline['id'])
                trips = trips_response.get('opportunities', [])
                
                save_json(trips, 'trips_raw.json')
                summary['counts']['trips'] = len(trips)
                print(f"   ✅ Fetched {len(trips)} trip opportunities")
                
                # Show sample custom fields structure
                if trips:
                    print("\n   Sample trip custom fields structure:")
                    sample_trip = trips[0]
                    custom_fields = sample_trip.get('customFields', [])
                    print(f"     customFields array length: {len(custom_fields)}")
                    if custom_fields:
                        sample_field = custom_fields[0]
                        print(f"     Sample field: {json.dumps(sample_field, indent=6)}")
            except Exception as e:
                print(f"❌ Error fetching trips: {e}")
                summary['errors'] = summary.get('errors', [])
                summary['errors'].append(f"Trips: {str(e)}")
        else:
            print("4️⃣  ⚠️  Skipping Trip opportunities (no TripBooking pipeline found)")
        
        print()
        
        # 5. Fetch Passenger Opportunities
        if passenger_pipeline:
            print("5️⃣  Fetching Passenger opportunities...")
            try:
                passengers_response = api.search_opportunities(pipeline_id=passenger_pipeline['id'])
                passengers = passengers_response.get('opportunities', [])
                
                save_json(passengers, 'passengers_raw.json')
                summary['counts']['passengers'] = len(passengers)
                print(f"   ✅ Fetched {len(passengers)} passenger opportunities")
            except Exception as e:
                print(f"❌ Error fetching passengers: {e}")
                summary['errors'] = summary.get('errors', [])
                summary['errors'].append(f"Passengers: {str(e)}")
        else:
            print("5️⃣  ⚠️  Skipping Passenger opportunities (no Passenger pipeline found)")
        
        print()
        
        # Save summary
        save_json(summary, 'sync_summary.json')
        
        print()
        print("=" * 70)
        print("SYNC COMPLETE")
        print("=" * 70)
        print()
        print("📁 Files created in raw_ghl_responses/:")
        print("   - contacts_raw.json")
        print("   - trips_raw.json")
        print("   - passengers_raw.json")
        print("   - custom_fields_raw.json")
        print("   - sync_summary.json")
        print()
        print("Next steps:")
        print("1. Inspect the raw files to see actual GHL structure")
        print("2. Run: python build_field_maps.py")
        print("3. Verify field mappings in the database")
        print()


if __name__ == '__main__':
    main()
