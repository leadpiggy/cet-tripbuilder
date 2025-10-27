#!/usr/bin/env python3
"""Check what trip-related custom fields exist"""

from app import app, db
from models import CustomField

with app.app_context():
    # Query all custom fields that contain "trip" in the field key
    trip_fields = CustomField.query.filter(
        CustomField.field_key.like('%trip%')
    ).all()
    
    print("Trip-related custom fields in database:")
    print("=" * 80)
    for field in trip_fields:
        print(f"  Field Key: {field.field_key}")
        print(f"  GHL ID: {field.ghl_field_id}")
        print(f"  Name: {field.name}")
        print(f"  Model: {field.model}")
        print()
    
    if not trip_fields:
        print("No trip-related fields found!")
        print("\nShowing all opportunity fields instead:")
        opp_fields = CustomField.query.filter_by(model='opportunity').limit(10).all()
        for field in opp_fields:
            print(f"  {field.field_key} = {field.name}")
