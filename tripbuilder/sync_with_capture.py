#!/usr/bin/env python3
"""
Sync with API Response Capture

This script runs the full GHL sync but captures all raw API responses
to JSON files for debugging. This allows you to debug sync logic without
hitting the API repeatedly.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("GHL Sync with Response Capture")
print("=" * 60)

# Import Flask app and models
from app import app
from models import db
from ghl_api import GoHighLevelAPI
from services.ghl_sync import GHLSyncService

# Initialize GHL API
ghl_api = GoHighLevelAPI(
    location_id=os.getenv('GHL_LOCATION_ID'),
    api_key=os.getenv('GHL_API_TOKEN')
)

# Create directory for captured data
capture_dir = 'sync_captures'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
capture_path = os.path.join(capture_dir, timestamp)
os.makedirs(capture_path, exist_ok=True)

print(f"\n📁 Capturing API responses to: {capture_path}")

# Wrapper class to capture API responses
class CaptureGHLAPI:
    def __init__(self, api, capture_path):
        self.api = api
        self.capture_path = capture_path
        self.call_count = {}
    
    def _capture(self, name, data):
        """Save data to JSON file"""
        # Increment call count for this endpoint
        count = self.call_count.get(name, 0) + 1
        self.call_count[name] = count
        
        filename = f"{count:03d}_{name}.json"
        filepath = os.path.join(self.capture_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"   💾 Captured: {filename}")
        return data
    
    def get_pipelines(self):
        data = self.api.get_pipelines()
        return self._capture('pipelines', data)
    
    def get_custom_fields(self, model='opportunity'):
        data = self.api.get_custom_fields(model=model)
        return self._capture(f'custom_fields_{model}', data)
    
    def _make_request(self, method, endpoint, **kwargs):
        """Capture raw API requests"""
        data = self.api._make_request(method, endpoint, **kwargs)
        
        # Determine capture name from endpoint
        endpoint_name = endpoint.replace('/', '_').strip('_')
        if 'contacts' in endpoint:
            capture_name = 'contacts'
        elif 'opportunities' in endpoint:
            capture_name = 'opportunities'
        else:
            capture_name = endpoint_name
        
        return self._capture(capture_name, data)
    
    def search_opportunities(self, **kwargs):
        data = self.api.search_opportunities(**kwargs)
        pipeline_id = kwargs.get('pipeline_id', 'unknown')
        page = kwargs.get('page', 1)
        return self._capture(f'opportunities_{pipeline_id}_page{page}', data)
    
    def __getattr__(self, name):
        """Pass through any other attributes"""
        return getattr(self.api, name)


# Wrap the API
wrapped_api = CaptureGHLAPI(ghl_api, capture_path)

# Run the sync
print("\n🔄 Running sync with capture...")
print("=" * 60)

with app.app_context():
    sync_service = GHLSyncService(wrapped_api)
    
    try:
        results = sync_service.perform_full_sync()
        
        # Save final results
        results_file = os.path.join(capture_path, '000_sync_results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Sync complete with capture!")
        print(f"📁 All responses saved to: {capture_path}")
        print("\nCapture Summary:")
        for name, count in sorted(wrapped_api.call_count.items()):
            print(f"   {name}: {count} calls")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Save error info
        error_file = os.path.join(capture_path, 'error.json')
        with open(error_file, 'w') as f:
            json.dump({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, f, indent=2)
