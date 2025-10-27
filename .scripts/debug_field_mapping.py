#!/usr/bin/env python3
"""Debug script to see what GHL is actually returning"""

from app import app, ghl_api
from models import db, CustomField

with app.app_context():
    print("\n" + "="*70)
    print("DEBUG: GHL API RESPONSE")
    print("="*70)
    
    # Get one trip opportunity to see its structure
    print("\n1️⃣  Fetching a sample trip opportunity...")
    response = ghl_api.search_opportunities(
        pipeline_id="IlWdPtOpcczLpgsde2KF",
        limit=1,
        page=1
    )
    
    if response.get('opportunities'):
        opp = response['opportunities'][0]
        print(f"\nOpportunity ID: {opp.get('id')}")
        print(f"Name: {opp.get('name')}")
        print(f"\nCustom Fields ({len(opp.get('customFields', []))}):")
        
        for field in opp.get('customFields', [])[:10]:  # Show first 10
            field_id = field.get('id')
            field_value = field.get('fieldValue')
            
            # Look up in our database
            custom_field_def = CustomField.query.filter_by(ghl_field_id=field_id).first()
            field_key = custom_field_def.field_key if custom_field_def else "NOT FOUND IN DB"
            
            print(f"   - ID: {field_id}")
            print(f"     Key: {field_key}")
            print(f"     Value: {field_value}")
            print()
    
    # Check our custom fields database
    print("\n2️⃣  Checking custom_fields table...")
    total_fields = CustomField.query.count()
    opportunity_fields = CustomField.query.filter_by(model='opportunity').count()
    
    print(f"   Total custom fields in DB: {total_fields}")
    print(f"   Opportunity fields: {opportunity_fields}")
    
    # Show some field mappings
    print("\n   Sample field mappings:")
    sample_fields = CustomField.query.filter(
        CustomField.field_key.like('opportunity.%')
    ).limit(10).all()
    
    for field in sample_fields:
        print(f"   - {field.field_key}")
        print(f"     GHL ID: {field.ghl_field_id}")
        print(f"     Name: {field.name}")
        print()
    
    print("="*70)
