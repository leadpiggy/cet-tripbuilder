#!/usr/bin/env python3
"""Check actual database schema for passengers table"""

from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    
    print("=== Passengers Table Columns ===")
    columns = inspector.get_columns('passengers')
    for col in columns:
        print(f"  {col['name']}: {col['type']}")
