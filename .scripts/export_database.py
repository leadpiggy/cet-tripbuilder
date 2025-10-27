#!/usr/bin/env python3
"""
Export Database to JSON

Exports all trips, contacts, and passengers to JSON files
for easy debugging and inspection.
"""

import os
import json
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import app
from models import Trip, Contact, Passenger, Pipeline, PipelineStage

# JSON encoder for dates
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def model_to_dict(instance):
    """Convert SQLAlchemy model instance to dictionary"""
    result = {}
    for column in instance.__table__.columns:
        value = getattr(instance, column.name)
        result[column.name] = value
    return result

# Create export directory
export_dir = 'database_exports'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
export_path = os.path.join(export_dir, timestamp)
os.makedirs(export_path, exist_ok=True)

print("=" * 60)
print("Database Export to JSON")
print("=" * 60)
print(f"\n📁 Exporting to: {export_path}\n")

with app.app_context():
    # Export Trips
    print("🗺️  Exporting Trips...")
    trips = Trip.query.all()
    trips_data = [model_to_dict(trip) for trip in trips]
    
    trips_file = os.path.join(export_path, 'trips.json')
    with open(trips_file, 'w') as f:
        json.dump(trips_data, f, indent=2, cls=DateEncoder)
    print(f"   ✅ Exported {len(trips_data)} trips")
    
    # Export Contacts
    print("\n👥 Exporting Contacts...")
    contacts = Contact.query.all()
    contacts_data = [model_to_dict(contact) for contact in contacts]
    
    contacts_file = os.path.join(export_path, 'contacts.json')
    with open(contacts_file, 'w') as f:
        json.dump(contacts_data, f, indent=2, cls=DateEncoder)
    print(f"   ✅ Exported {len(contacts_data)} contacts")
    
    # Export Passengers
    print("\n🎫 Exporting Passengers...")
    passengers = Passenger.query.all()
    passengers_data = []
    
    for passenger in passengers:
        p_dict = model_to_dict(passenger)
        
        # Add contact info for readability
        contact = Contact.query.get(passenger.contact_id)
        if contact:
            p_dict['_contact_name'] = f"{contact.firstname} {contact.lastname}"
            p_dict['_contact_email'] = contact.email
        
        # Add trip info for readability
        if passenger.trip_id:
            trip = Trip.query.get(passenger.trip_id)
            if trip:
                p_dict['_trip_name'] = trip.name
                p_dict['_trip_destination'] = trip.destination
        
        passengers_data.append(p_dict)
    
    passengers_file = os.path.join(export_path, 'passengers.json')
    with open(passengers_file, 'w') as f:
        json.dump(passengers_data, f, indent=2, cls=DateEncoder)
    print(f"   ✅ Exported {len(passengers_data)} passengers")
    
    # Export Pipelines and Stages
    print("\n📊 Exporting Pipelines...")
    pipelines = Pipeline.query.all()
    pipelines_data = []
    
    for pipeline in pipelines:
        p_dict = model_to_dict(pipeline)
        
        # Add stages
        stages = PipelineStage.query.filter_by(pipeline_id=pipeline.id).order_by(PipelineStage.position).all()
        p_dict['stages'] = [model_to_dict(stage) for stage in stages]
        
        pipelines_data.append(p_dict)
    
    pipelines_file = os.path.join(export_path, 'pipelines.json')
    with open(pipelines_file, 'w') as f:
        json.dump(pipelines_data, f, indent=2, cls=DateEncoder)
    print(f"   ✅ Exported {len(pipelines_data)} pipelines")
    
    # Create summary
    summary = {
        'export_time': datetime.now().isoformat(),
        'counts': {
            'trips': len(trips_data),
            'contacts': len(contacts_data),
            'passengers': len(passengers_data),
            'pipelines': len(pipelines_data)
        },
        'trip_passenger_stats': {
            'passengers_with_trip': len([p for p in passengers if p.trip_id]),
            'passengers_without_trip': len([p for p in passengers if not p.trip_id])
        },
        'files': {
            'trips': 'trips.json',
            'contacts': 'contacts.json',
            'passengers': 'passengers.json',
            'pipelines': 'pipelines.json'
        }
    }
    
    summary_file = os.path.join(export_path, 'summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Export complete!")
    print(f"\n📁 Files saved to: {export_path}")
    print("\nSummary:")
    print(f"   Trips: {summary['counts']['trips']}")
    print(f"   Contacts: {summary['counts']['contacts']}")
    print(f"   Passengers: {summary['counts']['passengers']}")
    print(f"   Pipelines: {summary['counts']['pipelines']}")
    print(f"\nPassenger-Trip Links:")
    print(f"   With trip: {summary['trip_passenger_stats']['passengers_with_trip']}")
    print(f"   Without trip: {summary['trip_passenger_stats']['passengers_without_trip']}")
