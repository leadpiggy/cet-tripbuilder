#!/usr/bin/env python3
"""
Database Migration: Add trip_name and name columns

This migration adds:
1. 'name' column to trips table
2. 'trip_name' column to passengers table  
3. Makes trip_id nullable in passengers table
4. Creates field_maps table if it doesn't exist

Usage:
    python3 migrate_add_trip_columns.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app import app, db
from sqlalchemy import text

def run_migration():
    """Run the migration"""
    print()
    print("=" * 70)
    print("DATABASE MIGRATION: Add Trip Columns")
    print("=" * 70)
    print()
    
    with app.app_context():
        try:
            # 1. Add name column to trips table
            print("1️⃣  Adding 'name' column to trips table...")
            try:
                db.session.execute(text(
                    "ALTER TABLE trips ADD COLUMN name VARCHAR(200)"
                ))
                db.session.commit()
                print("   ✅ Added trips.name column")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("   ℹ️  Column trips.name already exists")
                    db.session.rollback()
                else:
                    raise
            
            print()
            
            # 2. Add trip_name column to passengers table
            print("2️⃣  Adding 'trip_name' column to passengers table...")
            try:
                db.session.execute(text(
                    "ALTER TABLE passengers ADD COLUMN trip_name VARCHAR(200)"
                ))
                db.session.commit()
                print("   ✅ Added passengers.trip_name column")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e).lower():
                    print("   ℹ️  Column passengers.trip_name already exists")
                    db.session.rollback()
                else:
                    raise
            
            print()
            
            # 3. Make trip_id nullable in passengers (if not already)
            print("3️⃣  Making passengers.trip_id nullable...")
            try:
                # Check if it's already nullable
                result = db.session.execute(text("""
                    SELECT is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name='passengers' 
                    AND column_name='trip_id'
                """))
                row = result.fetchone()
                
                if row and row[0] == 'NO':
                    # Make it nullable
                    db.session.execute(text(
                        "ALTER TABLE passengers ALTER COLUMN trip_id DROP NOT NULL"
                    ))
                    db.session.commit()
                    print("   ✅ Made passengers.trip_id nullable")
                else:
                    print("   ℹ️  passengers.trip_id is already nullable")
            except Exception as e:
                print(f"   ⚠️  Could not modify trip_id: {e}")
                db.session.rollback()
            
            print()
            
            # 4. Create field_maps table if it doesn't exist
            print("4️⃣  Creating field_maps table...")
            try:
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS field_maps (
                        id SERIAL PRIMARY KEY,
                        ghl_key VARCHAR(100) UNIQUE NOT NULL,
                        field_key VARCHAR(200) NOT NULL,
                        table_column VARCHAR(100) NOT NULL,
                        tablename VARCHAR(100) NOT NULL,
                        data_type VARCHAR(50) NOT NULL
                    )
                """))
                db.session.commit()
                print("   ✅ Created field_maps table")
            except Exception as e:
                if "already exists" in str(e):
                    print("   ℹ️  Table field_maps already exists")
                    db.session.rollback()
                else:
                    raise
            
            print()
            print("=" * 70)
            print("MIGRATION COMPLETE!")
            print("=" * 70)
            print()
            print("✅ Database schema updated successfully")
            print()
            print("Next steps:")
            print("1. Run: python3 link_passengers_from_raw_json.py")
            print()
            
        except Exception as e:
            print()
            print("❌ Migration failed:")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)


if __name__ == '__main__':
    run_migration()
