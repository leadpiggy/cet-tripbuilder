#!/usr/bin/env python3
"""
Script to update missing trip_name values in passengers table
by cross-referencing with the CET passengers CSV file.

Processes CSV in chunks to avoid memory issues.
Uses raw SQL to avoid model/schema mismatches.
"""

import pandas as pd
from app import app, db

# Configuration
CSV_FILE = 'cet_passengers.csv'
CHUNK_SIZE = 1000  # Process 1000 rows at a time

def analyze_csv_columns():
    """First pass: analyze what columns we have in the CSV"""
    print("=== Analyzing CSV structure ===")
    
    # Read just the first few rows to see columns
    df_sample = pd.read_csv(CSV_FILE, nrows=5)
    print(f"\nAvailable columns in CSV:")
    for col in df_sample.columns:
        print(f"  - {col}")
    
    print(f"\nSample data:")
    print(df_sample[['passenger_id', 'ghl_id', 'user_email', 'trip_name']].head())
    
    return list(df_sample.columns)


def update_missing_trip_names():
    """Process CSV and update passengers with missing trip_name"""
    
    with app.app_context():
        # Get passengers with missing trip_name using raw SQL
        query = """
            SELECT p.id, p.trip_name, c.id as contact_id, c.email, c.phone
            FROM passengers p
            JOIN contacts c ON p.contact_id = c.id
            WHERE p.trip_name IS NULL OR p.trip_name = ''
        """
        result = db.session.execute(db.text(query))
        passengers_missing = result.fetchall()
        
        print(f"\n=== Found {len(passengers_missing)} passengers with missing trip_name ===")
        
        if len(passengers_missing) == 0:
            print("No passengers need updating!")
            return
        
        # Create lookup dictionaries for fast matching
        passengers_by_ghl_id = {}
        passengers_by_email = {}
        passengers_by_phone = {}
        
        for row in passengers_missing:
            passenger_id = row[0]
            contact_id = row[2]
            email = row[3]
            phone = row[4]
            
            # Map by GHL contact ID
            passengers_by_ghl_id[contact_id] = passenger_id
            
            # Map by email
            if email:
                passengers_by_email[email.lower()] = passenger_id
            
            # Map by phone
            if phone:
                clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                passengers_by_phone[clean_phone] = passenger_id
        
        print(f"\nIndexed passengers by:")
        print(f"  - GHL ID: {len(passengers_by_ghl_id)} entries")
        print(f"  - Email: {len(passengers_by_email)} entries")
        print(f"  - Phone: {len(passengers_by_phone)} entries")
        
        # Track updates to batch commit
        updates = []  # List of (passenger_id, trip_name) tuples
        
        # Process CSV in chunks
        updated_count = 0
        total_rows = 0
        
        print(f"\n=== Processing CSV in chunks of {CHUNK_SIZE} ===")
        
        for chunk_num, chunk in enumerate(pd.read_csv(CSV_FILE, chunksize=CHUNK_SIZE), 1):
            total_rows += len(chunk)
            print(f"\nProcessing chunk {chunk_num} ({len(chunk)} rows, total processed: {total_rows})")
            
            # Process each row in the chunk
            for idx, row in chunk.iterrows():
                # Extract values from CSV
                csv_trip_name = row.get('trip_name', None)
                
                # Skip if no trip_name in CSV
                if pd.isna(csv_trip_name) or str(csv_trip_name).strip() == '':
                    continue
                
                csv_trip_name = str(csv_trip_name).strip()
                
                # Try to match by GHL ID first
                passenger_id = None
                csv_ghl_id = row.get('ghl_id', None)
                if not pd.isna(csv_ghl_id):
                    csv_ghl_id = str(csv_ghl_id).strip()
                    passenger_id = passengers_by_ghl_id.get(csv_ghl_id)
                
                # Try email if no match yet
                if not passenger_id:
                    csv_email = row.get('user_email', None)
                    if not pd.isna(csv_email):
                        csv_email = str(csv_email).strip().lower()
                        passenger_id = passengers_by_email.get(csv_email)
                
                # Try phone if still no match
                if not passenger_id:
                    csv_phone = row.get('user_phone', None)
                    if not pd.isna(csv_phone):
                        csv_phone = str(csv_phone).strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                        passenger_id = passengers_by_phone.get(csv_phone)
                
                # If we found a match, add to updates
                if passenger_id:
                    updates.append((passenger_id, csv_trip_name))
                    updated_count += 1
                    
                    if updated_count % 50 == 0:
                        print(f"  Matched {updated_count} passengers so far...")
        
        # Now do batch update using raw SQL
        if updates:
            print(f"\n=== Updating {len(updates)} passengers in database ===")
            
            for passenger_id, trip_name in updates:
                update_sql = """
                    UPDATE passengers 
                    SET trip_name = :trip_name, updated_at = NOW()
                    WHERE id = :passenger_id
                """
                db.session.execute(db.text(update_sql), {
                    'trip_name': trip_name,
                    'passenger_id': passenger_id
                })
            
            db.session.commit()
            print("✅ Database updated!")
        
        print(f"\n✅ SUCCESS!")
        print(f"  Total CSV rows processed: {total_rows}")
        print(f"  Passengers updated: {updated_count}")
        print(f"  Still missing: {len(passengers_missing) - updated_count}")


def show_statistics():
    """Show statistics about trip_name population"""
    with app.app_context():
        # Use raw SQL to avoid schema issues
        total_query = "SELECT COUNT(*) FROM passengers"
        with_trip_name_query = """
            SELECT COUNT(*) FROM passengers 
            WHERE trip_name IS NOT NULL AND trip_name != ''
        """
        
        total_passengers = db.session.execute(db.text(total_query)).scalar()
        with_trip_name = db.session.execute(db.text(with_trip_name_query)).scalar()
        without_trip_name = total_passengers - with_trip_name
        
        print(f"\n=== Trip Name Statistics ===")
        print(f"Total passengers: {total_passengers}")
        print(f"With trip_name: {with_trip_name} ({100*with_trip_name/total_passengers:.1f}%)")
        print(f"Missing trip_name: {without_trip_name} ({100*without_trip_name/total_passengers:.1f}%)")


if __name__ == '__main__':
    print("=" * 60)
    print("Update Missing Trip Names from CSV")
    print("=" * 60)
    
    # First analyze the CSV structure
    columns = analyze_csv_columns()
    
    # Check we have the expected columns
    required = ['trip_name']
    id_cols = ['ghl_id', 'user_email', 'user_phone']
    
    missing_required = [col for col in required if col not in columns]
    missing_id = [col for col in id_cols if col not in columns]
    
    if missing_required:
        print(f"\n❌ ERROR: Missing required columns: {missing_required}")
        exit(1)
    
    if len(missing_id) == len(id_cols):
        print(f"\n❌ ERROR: Need at least one ID column from: {id_cols}")
        exit(1)
    
    print("\n✅ CSV has required columns")
    
    # Show current statistics
    show_statistics()
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    response = input("Proceed with updating passengers? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        update_missing_trip_names()
        show_statistics()
    else:
        print("Operation cancelled.")
