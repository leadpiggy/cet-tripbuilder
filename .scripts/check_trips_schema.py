#!/usr/bin/env python3
"""Check actual trips table schema"""

from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    
    print("=== Trips Table Columns ===")
    columns = inspector.get_columns('trips')
    for col in columns:
        print(f"  {col['name']}: {col['type']}")
