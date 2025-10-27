"""
Database Migration: Add files table

This script adds the files table to track S3-uploaded documents.
Run this script to update your database schema.

Usage:
    python migrate_add_files_table.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import models
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

from models import db, File
from app import app

def migrate():
    """Create the files table"""
    with app.app_context():
        print("🔄 Creating files table...")
        
        # Create the table
        db.create_all()
        
        print("✅ Files table created successfully!")
        print("\nTable: files")
        print("Columns:")
        print("  - id (Primary Key)")
        print("  - filename")
        print("  - s3_key (unique)")
        print("  - file_type")
        print("  - content_type")
        print("  - file_size")
        print("  - is_public")
        print("  - opportunity_type")
        print("  - trip_id (Foreign Key)")
        print("  - passenger_id (Foreign Key)")
        print("  - uploaded_at")
        print("  - uploaded_by")
        
        print("\n✅ Migration complete!")

if __name__ == '__main__':
    migrate()