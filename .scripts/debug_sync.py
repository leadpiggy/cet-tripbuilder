#!/usr/bin/env python3
"""
Debug script to test GHL sync functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("GHL Sync Debug Script")
print("=" * 60)

# Check environment variables
print("\n1. Checking Environment Variables...")
ghl_token = os.getenv('GHL_API_TOKEN')
ghl_location = os.getenv('GHL_LOCATION_ID')
db_url = os.getenv('DATABASE_URL')

print(f"   GHL_API_TOKEN: {'✅ Set' if ghl_token else '❌ Missing'}")
print(f"   GHL_LOCATION_ID: {'✅ Set' if ghl_location else '❌ Missing'}")
print(f"   DATABASE_URL: {db_url if db_url else '❌ Missing'}")

if not ghl_token or not ghl_location:
    print("\n❌ Error: GHL credentials not set in .env file")
    sys.exit(1)

# Test imports
print("\n2. Testing Imports...")
try:
    from app import app
    print("   ✅ Flask app imported")
except Exception as e:
    print(f"   ❌ Failed to import app: {e}")
    sys.exit(1)

try:
    from ghl_api import GoHighLevelAPI
    print("   ✅ GHL API imported")
except Exception as e:
    print(f"   ❌ Failed to import GHL API: {e}")
    sys.exit(1)

try:
    from ghl_sync import GHLSyncService
    print("   ✅ GHL Sync Service imported")
except Exception as e:
    print(f"   ❌ Failed to import GHL Sync Service: {e}")
    sys.exit(1)

# Test database connection
print("\n3. Testing Database Connection...")
try:
    with app.app_context():
        from models import db
        # Try to execute a simple query
        result = db.session.execute(db.text("SELECT 1")).fetchone()
        print(f"   ✅ Database connected: {result[0] == 1}")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    sys.exit(1)

# Test GHL API initialization
print("\n4. Testing GHL API Initialization...")
try:
    ghl_api = GoHighLevelAPI(
        location_id=ghl_location,
        api_key=ghl_token
    )
    print("   ✅ GHL API initialized")
except Exception as e:
    print(f"   ❌ GHL API initialization failed: {e}")
    sys.exit(1)

# Test sync service initialization
print("\n5. Testing Sync Service Initialization...")
try:
    sync_service = GHLSyncService(ghl_api)
    print("   ✅ Sync service initialized")
except Exception as e:
    print(f"   ❌ Sync service initialization failed: {e}")
    sys.exit(1)

# Check if methods exist
print("\n6. Checking Sync Methods...")
methods = ['sync_pipelines', 'sync_custom_fields', 'sync_contacts', 'perform_full_sync']
for method in methods:
    if hasattr(sync_service, method):
        print(f"   ✅ {method} exists")
    else:
        print(f"   ❌ {method} missing")

# Try running a simple sync
print("\n7. Testing Pipeline Sync...")
try:
    with app.app_context():
        result = sync_service.sync_pipelines()
        print(f"   ✅ Pipeline sync successful: {result}")
except Exception as e:
    print(f"   ❌ Pipeline sync failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Debug Complete!")
print("=" * 60)
