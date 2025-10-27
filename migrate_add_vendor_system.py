"""
Migration: Add Vendor Management and Dropdown Cache System
Date: October 27, 2025

This migration adds:
1. trip_vendors table - For vendor management with GHL sync
2. dropdown_cache table - For caching GHL dropdown field values
3. trip_vendor_id column to trips table - Foreign key to vendors

Run this migration before using vendor management features.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tripbuilder.app import app, db
from sqlalchemy import text

def migrate():
    """Execute the migration"""
    with app.app_context():
        print("Starting vendor system migration...")
        
        try:
            # Create trip_vendors table
            print("Creating trip_vendors table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS trip_vendors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ trip_vendors table created")
            
            # Create dropdown_cache table
            print("Creating dropdown_cache table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS dropdown_cache (
                    id SERIAL PRIMARY KEY,
                    field_key VARCHAR(100) NOT NULL UNIQUE,
                    options JSON NOT NULL,
                    last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ dropdown_cache table created")
            
            # Add trip_vendor_id column to trips table
            print("Adding trip_vendor_id column to trips table...")
            db.session.execute(text("""
                ALTER TABLE trips 
                ADD COLUMN IF NOT EXISTS trip_vendor_id INTEGER 
                REFERENCES trip_vendors(id) ON DELETE SET NULL
            """))
            print("✅ trip_vendor_id column added to trips table")
            
            # Commit all changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("\nNext steps:")
            print("1. Run GHL sync to populate dropdown_cache: cd tripbuilder && flask sync-ghl")
            print("2. Create vendors through the UI or import from GHL")
            print("3. Start using the enrollment wizard")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure PostgreSQL is running")
            print("2. Verify database credentials in .env")
            print("3. Check if tables already exist")
            raise

def verify():
    """Verify the migration was successful"""
    with app.app_context():
        print("\nVerifying migration...")
        
        try:
            # Check trip_vendors table
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'trip_vendors'
            """))
            if result.fetchone():
                print("✅ trip_vendors table exists")
            else:
                print("❌ trip_vendors table NOT found")
            
            # Check dropdown_cache table
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'dropdown_cache'
            """))
            if result.fetchone():
                print("✅ dropdown_cache table exists")
            else:
                print("❌ dropdown_cache table NOT found")
            
            # Check trip_vendor_id column
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'trips' 
                AND column_name = 'trip_vendor_id'
            """))
            if result.fetchone():
                print("✅ trip_vendor_id column exists in trips table")
            else:
                print("❌ trip_vendor_id column NOT found in trips table")
            
            print("\nVerification complete!")
            
        except Exception as e:
            print(f"\n❌ Verification failed: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("TripBuilder - Vendor System Migration")
    print("=" * 60)
    print()
    
    # Run migration
    migrate()
    
    # Verify migration
    verify()
    
    print("\n" + "=" * 60)
    print("Migration process complete!")
    print("=" * 60)