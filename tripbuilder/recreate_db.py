#!/usr/bin/env python3
"""
Recreate database with new schema.
WARNING: This will delete all existing data!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db

print("⚠️  WARNING: This will drop all tables and recreate them!")
print("All existing data will be lost.")
response = input("Continue? (yes/no): ")

if response.lower() != 'yes':
    print("Aborted.")
    sys.exit(0)

with app.app_context():
    print("\n📦 Dropping all tables...")
    db.drop_all()
    print("✅ All tables dropped")
    
    print("\n📦 Creating new tables...")
    db.create_all()
    print("✅ New tables created")
    
    print("\n✅ Database schema updated successfully!")
    print("Run 'flask sync-ghl' to populate with GHL data.")
