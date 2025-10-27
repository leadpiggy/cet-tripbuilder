#!/usr/bin/env python3
"""
Complete Sync and Debug Process

This master script runs the complete sync process with data capture and analysis:
1. Captures raw API responses during sync
2. Exports all database data to JSON
3. Attempts to back-populate trip-passenger relationships
4. Creates a comprehensive debugging package

Run this instead of individual scripts for a complete debugging snapshot.
"""

import os
import sys
import subprocess
from datetime import datetime

print("=" * 70)
print(" " * 15 + "COMPLETE SYNC AND DEBUG PROCESS")
print("=" * 70)

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Activate virtual environment
venv_python = os.path.join('..', '.venv', 'bin', 'python')
if not os.path.exists(venv_python):
    venv_python = 'python'  # Fallback to system Python

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
print(f"\n📅 Run timestamp: {timestamp}")
print(f"📁 Working directory: {script_dir}")
print(f"🐍 Python: {venv_python}")

# Step 1: Run sync with capture
print("\n" + "=" * 70)
print("STEP 1: Sync with API Response Capture")
print("=" * 70)
result = subprocess.run([venv_python, 'sync_with_capture.py'])
if result.returncode != 0:
    print("\n⚠️  Sync failed, but continuing with other steps...")

# Step 2: Export database
print("\n" + "=" * 70)
print("STEP 2: Export Database to JSON")
print("=" * 70)
result = subprocess.run([venv_python, 'export_database.py'])
if result.returncode != 0:
    print("\n⚠️  Export failed, but continuing...")

# Step 3: Back-populate trip IDs
print("\n" + "=" * 70)
print("STEP 3: Back-populate Trip-Passenger Relationships")
print("=" * 70)
result = subprocess.run([venv_python, 'backpopulate_trip_ids.py'])
if result.returncode != 0:
    print("\n⚠️  Back-population failed, but continuing...")

# Step 4: Export database again (to capture changes from back-population)
print("\n" + "=" * 70)
print("STEP 4: Export Database Again (Post Back-population)")
print("=" * 70)
result = subprocess.run([venv_python, 'export_database.py'])

# Summary
print("\n" + "=" * 70)
print("✅ COMPLETE SYNC AND DEBUG PROCESS FINISHED")
print("=" * 70)

# Find the latest export directories
sync_captures_dir = 'sync_captures'
database_exports_dir = 'database_exports'

latest_capture = None
latest_export = None

if os.path.exists(sync_captures_dir):
    captures = sorted([d for d in os.listdir(sync_captures_dir) if os.path.isdir(os.path.join(sync_captures_dir, d))])
    if captures:
        latest_capture = os.path.join(sync_captures_dir, captures[-1])

if os.path.exists(database_exports_dir):
    exports = sorted([d for d in os.listdir(database_exports_dir) if os.path.isdir(os.path.join(database_exports_dir, d))])
    if exports:
        latest_export = os.path.join(database_exports_dir, exports[-1])

print("\n📦 Debugging Package Created:")
if latest_capture:
    print(f"   🔍 API Captures: {latest_capture}")
if latest_export:
    print(f"   💾 Database Export: {latest_export}")

print("\n💡 Next Steps:")
print("   1. Review sync captures in sync_captures/ to see raw API responses")
print("   2. Review database exports in database_exports/ to see what was saved")
print("   3. Check passengers.json to see which passengers have trip_id set")
print("   4. If issues persist, you can now debug without re-running API calls!")
print("\n" + "=" * 70)
