"""
Two-Way Sync Service for TripBuilder <-> GoHighLevel

Handles bidirectional synchronization:
1. Push: Local Database → GHL (when we create/update locally)
2. Pull: GHL → Local Database (when syncing from GHL)
3. Automatic sync hooks for Trip and Passenger operations

Usage:
    from services.two_way_sync import TwoWaySyncService
    
    sync_service = TwoWaySyncService(ghl_api)
    
    # Push local changes to GHL
    sync_service.push_trip_to_ghl(trip)
    sync_service.push_passenger_to_ghl(passenger)
    
    # Pull GHL changes to local
    trip = sync_service.pull_trip_from_ghl(ghl_opportunity_id)
    passenger = sync_service.pull_passenger_from_ghl(ghl_opportunity_id)
"""

from datetime import datetime, date
from typing import Dict, Optional, Any
from models import db, Trip, Passenger, Contact
from field_mapping import (
    parse_ghl_custom_fields, 
    map_trip_custom_fields, 
    map_passenger_custom_fields,
    TRIP_FIELD_MAP,
    PASSENGER_FIELD_MAP
)


# Pipeline IDs from PIPELINE_CUSTOM_FIELD_DATA.md
TRIPBOOKING_PIPELINE_ID = "IlWdPtOpcczLpgsde2KF"
PASSENGER_PIPELINE_ID = "fnsdpRtY9o83Vr4z15bE"


class TwoWaySyncService:
    """
    Bidirectional sync between TripBuilder database and GoHighLevel.
    """
    
    def __init__(self, ghl_api):
        """
        Initialize two-way sync service.
        
        Args:
            ghl_api: GoHighLevelAPI instance
        """
        self.api = ghl_api
    
    # =====================================================================
    # PUSH TO GHL (Local → GHL)
    # =====================================================================
    
    def push_trip_to_ghl(self, trip: Trip, force_create: bool = False) -> Dict:
        """
        Push a Trip record to GHL as a TripBooking opportunity.
        Creates if doesn't exist, updates if it does.
        
        Args:
            trip: Trip instance
            force_create: If True, always create new opportunity
        
        Returns:
            dict: GHL API response with opportunity data
        """
        print(f"📤 Pushing Trip '{trip.name}' to GHL...")
        
        # Build custom fields data from trip
        custom_fields_data = {}
        
        # Map trip fields to GHL custom field keys
        reverse_map = {v: k for k, v in TRIP_FIELD_MAP.items()}
        
        # Get all trip attributes that map to GHL fields
        for column_name, field_key in reverse_map.items():
            value = getattr(trip, column_name, None)
            
            if value is not None:
                # Convert dates to ISO format
                if isinstance(value, date):
                    value = value.isoformat()
                # Convert boolean to string
                elif isinstance(value, bool):
                    value = str(value).lower()
                
                custom_fields_data[field_key] = value
        
        # Build opportunity data
        opp_data = {
            'name': trip.name or f"{trip.destination} - {trip.start_date}",
            'pipelineId': TRIPBOOKING_PIPELINE_ID,
            'locationId': self.api.location_id,
        }
        
        # Decide: create or update
        if trip.ghl_opportunity_id and not force_create:
            # Update existing opportunity
            print(f"   Updating existing opportunity {trip.ghl_opportunity_id}")
            
            try:
                # Update basic fields
                response = self.api.update_opportunity(trip.ghl_opportunity_id, opp_data)
                
                # Update custom fields one by one
                for field_key, value in custom_fields_data.items():
                    try:
                        self.api.upsert_opportunity_custom_field(
                            trip.ghl_opportunity_id,
                            field_key,
                            value
                        )
                    except Exception as e:
                        print(f"   ⚠️  Failed to update {field_key}: {e}")
                
                print(f"   ✅ Updated opportunity {trip.ghl_opportunity_id}")
                return response
                
            except Exception as e:
                print(f"   ❌ Error updating opportunity: {e}")
                raise
            
        else:
            # Create new opportunity
            print(f"   Creating new TripBooking opportunity")
            
            # Get first stage of TripBooking pipeline
            try:
                pipelines = self.api.get_pipelines()
                for pipeline in pipelines.get('pipelines', []):
                    if pipeline['id'] == TRIPBOOKING_PIPELINE_ID:
                        stages = pipeline.get('stages', [])
                        if stages:
                            opp_data['stageId'] = stages[0]['id']
                        break
                
                if 'stageId' not in opp_data:
                    raise Exception("Could not find default stage for TripBooking pipeline")
                
                # Add custom fields to creation data
                if custom_fields_data:
                    opp_data['customFields'] = custom_fields_data
                
                response = self.api.create_opportunity(opp_data)
                
                # Store GHL opportunity ID
                trip.ghl_opportunity_id = response.get('id')
                trip.updated_at = datetime.utcnow()
                db.session.commit()
                
                print(f"   ✅ Created opportunity {trip.ghl_opportunity_id}")
                return response
                
            except Exception as e:
                print(f"   ❌ Error creating opportunity: {e}")
                raise
    
    def push_passenger_to_ghl(self, passenger: Passenger, force_create: bool = False) -> Dict:
        """
        Push a Passenger record to GHL as a Passenger opportunity.
        Creates if doesn't exist, updates if it does.
        
        Args:
            passenger: Passenger instance
            force_create: If True, always create new opportunity
        
        Returns:
            dict: GHL API response with opportunity data
        """
        # Ensure contact exists
        if not passenger.contact_id:
            raise Exception("Passenger must have a contact_id")
        
        contact = passenger.contact
        if not contact:
            raise Exception(f"Contact {passenger.contact_id} not found")
        
        print(f"📤 Pushing Passenger '{contact.firstname} {contact.lastname}' to GHL...")
        
        # Build custom fields data from passenger
        custom_fields_data = {}
        
        # Map passenger fields to GHL custom field keys
        reverse_map = {v: k for k, v in PASSENGER_FIELD_MAP.items()}
        
        # Get all passenger attributes that map to GHL fields
        for column_name, field_key in reverse_map.items():
            value = getattr(passenger, column_name, None)
            
            if value is not None:
                # Convert dates to ISO format
                if isinstance(value, date):
                    value = value.isoformat()
                # Convert boolean to string
                elif isinstance(value, bool):
                    value = str(value).lower()
                
                custom_fields_data[field_key] = value
        
        # Add trip_name if we have a trip linked
        if passenger.trip_name:
            custom_fields_data['opportunity.tripname'] = passenger.trip_name
        
        # Build opportunity data
        opp_data = {
            'name': f"{contact.firstname} {contact.lastname} - {passenger.trip_name or 'Passenger'}",
            'pipelineId': PASSENGER_PIPELINE_ID,
            'contactId': passenger.contact_id,
            'locationId': self.api.location_id,
        }
        
        # Decide: create or update
        if passenger.id and not force_create:
            # Update existing opportunity
            print(f"   Updating existing opportunity {passenger.id}")
            
            try:
                # Update basic fields
                response = self.api.update_opportunity(passenger.id, opp_data)
                
                # Update custom fields one by one
                for field_key, value in custom_fields_data.items():
                    try:
                        self.api.upsert_opportunity_custom_field(
                            passenger.id,
                            field_key,
                            value
                        )
                    except Exception as e:
                        print(f"   ⚠️  Failed to update {field_key}: {e}")
                
                print(f"   ✅ Updated opportunity {passenger.id}")
                return response
                
            except Exception as e:
                print(f"   ❌ Error updating opportunity: {e}")
                raise
            
        else:
            # Create new opportunity
            print(f"   Creating new Passenger opportunity")
            
            # Get first stage of Passenger pipeline
            try:
                pipelines = self.api.get_pipelines()
                for pipeline in pipelines.get('pipelines', []):
                    if pipeline['id'] == PASSENGER_PIPELINE_ID:
                        stages = pipeline.get('stages', [])
                        if stages:
                            opp_data['stageId'] = stages[0]['id']
                        break
                
                if 'stageId' not in opp_data:
                    raise Exception("Could not find default stage for Passenger pipeline")
                
                # Add custom fields to creation data
                if custom_fields_data:
                    opp_data['customFields'] = custom_fields_data
                
                response = self.api.create_opportunity(opp_data)
                
                # Store GHL opportunity ID as passenger ID
                old_id = passenger.id
                passenger.id = response.get('id')
                passenger.updated_at = datetime.utcnow()
                
                # If passenger had a temporary ID, we need to handle that
                if old_id:
                    print(f"   Updated passenger ID from {old_id} to {passenger.id}")
                
                db.session.commit()
                
                print(f"   ✅ Created opportunity {passenger.id}")
                return response
                
            except Exception as e:
                print(f"   ❌ Error creating opportunity: {e}")
                raise
    
    def push_contact_to_ghl(self, contact: Contact) -> Dict:
        """
        Push a Contact record to GHL.
        Updates if exists, creates if new.
        
        Args:
            contact: Contact instance
        
        Returns:
            dict: GHL API response
        """
        print(f"📤 Pushing Contact '{contact.firstname} {contact.lastname}' to GHL...")
        
        contact_data = {
            'firstName': contact.firstname,
            'lastName': contact.lastname,
            'email': contact.email,
            'phone': contact.phone,
            'address1': contact.address,
            'city': contact.city,
            'state': contact.state,
            'postalCode': contact.postal_code,
            'country': contact.country or 'United States',
            'companyName': contact.company_name,
            'website': contact.website,
        }
        
        # Add tags if present
        if contact.tags:
            contact_data['tags'] = contact.tags if isinstance(contact.tags, list) else []
        
        # Clean None values
        contact_data = {k: v for k, v in contact_data.items() if v is not None}
        
        try:
            if contact.id:
                # Try to update existing
                response = self.api.update_contact(contact.id, **contact_data)
                print(f"   ✅ Updated contact {contact.id}")
            else:
                # Create new
                response = self.api.create_contact(**contact_data)
                contact.id = response.get('contact', {}).get('id')
                db.session.commit()
                print(f"   ✅ Created contact {contact.id}")
            
            return response
            
        except Exception as e:
            print(f"   ❌ Error syncing contact: {e}")
            raise
    
    # =====================================================================
    # PULL FROM GHL (GHL → Local)
    # =====================================================================
    
    def pull_trip_from_ghl(self, ghl_opportunity_id: str) -> Trip:
        """
        Pull a TripBooking opportunity from GHL and sync to local database.
        
        Args:
            ghl_opportunity_id: GHL opportunity ID
        
        Returns:
            Trip instance
        """
        print(f"📥 Pulling Trip {ghl_opportunity_id} from GHL...")
        
        # Fetch from GHL
        response = self.api.get_opportunity(ghl_opportunity_id)
        opp_data = response
        
        # Check if trip already exists
        trip = Trip.query.filter_by(ghl_opportunity_id=ghl_opportunity_id).first()
        
        if not trip:
            trip = Trip()
            trip.ghl_opportunity_id = ghl_opportunity_id
            print(f"   Creating new Trip")
        else:
            print(f"   Updating existing Trip {trip.id}")
        
        # Parse custom fields
        custom_fields_list = opp_data.get('customFields', [])
        custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
        mapped_fields = map_trip_custom_fields(custom_fields_dict)
        
        # Update trip with mapped fields
        for column_name, value in mapped_fields.items():
            if hasattr(trip, column_name):
                setattr(trip, column_name, value)
        
        # Update basic fields
        trip.name = opp_data.get('name')
        trip.updated_at = datetime.utcnow()
        
        db.session.add(trip)
        db.session.commit()
        
        print(f"   ✅ Synced Trip {trip.id}")
        return trip
    
    def pull_passenger_from_ghl(self, ghl_opportunity_id: str) -> Passenger:
        """
        Pull a Passenger opportunity from GHL and sync to local database.
        
        Args:
            ghl_opportunity_id: GHL opportunity ID
        
        Returns:
            Passenger instance
        """
        print(f"📥 Pulling Passenger {ghl_opportunity_id} from GHL...")
        
        # Fetch from GHL
        response = self.api.get_opportunity(ghl_opportunity_id)
        opp_data = response
        
        contact_id = opp_data.get('contactId')
        if not contact_id:
            raise Exception("Passenger opportunity missing contactId")
        
        # Ensure contact exists locally
        contact = Contact.query.get(contact_id)
        if not contact:
            raise Exception(f"Contact {contact_id} not found in local database. Sync contacts first.")
        
        # Check if passenger already exists
        passenger = Passenger.query.get(ghl_opportunity_id)
        
        if not passenger:
            passenger = Passenger()
            passenger.id = ghl_opportunity_id
            passenger.contact_id = contact_id
            print(f"   Creating new Passenger")
        else:
            print(f"   Updating existing Passenger {passenger.id}")
        
        # Parse custom fields
        custom_fields_list = opp_data.get('customFields', [])
        custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
        mapped_fields = map_passenger_custom_fields(custom_fields_dict)
        
        # Update passenger with mapped fields
        for column_name, value in mapped_fields.items():
            if hasattr(passenger, column_name):
                setattr(passenger, column_name, value)
        
        # Extract trip_name from custom fields
        trip_name = custom_fields_dict.get('opportunity.tripname')
        if trip_name:
            passenger.trip_name = trip_name
        
        # Update stage
        stage_id = opp_data.get('stageId')
        if stage_id:
            passenger.stage_id = stage_id
        
        passenger.updated_at = datetime.utcnow()
        passenger.last_synced_at = datetime.utcnow()
        
        db.session.add(passenger)
        db.session.commit()
        
        print(f"   ✅ Synced Passenger {passenger.id}")
        return passenger
    
    # =====================================================================
    # AUTO-SYNC HELPERS
    # =====================================================================
    
    def auto_sync_on_trip_create(self, trip: Trip):
        """
        Automatically sync a newly created trip to GHL.
        Call this after creating a trip locally.
        """
        if not trip.ghl_opportunity_id:
            self.push_trip_to_ghl(trip, force_create=True)
    
    def auto_sync_on_trip_update(self, trip: Trip):
        """
        Automatically sync trip updates to GHL.
        Call this after updating a trip locally.
        """
        if trip.ghl_opportunity_id:
            self.push_trip_to_ghl(trip, force_create=False)
    
    def auto_sync_on_passenger_create(self, passenger: Passenger):
        """
        Automatically sync a newly created passenger to GHL.
        Call this after enrolling a passenger locally.
        """
        # Ensure contact is synced first
        if passenger.contact:
            try:
                self.push_contact_to_ghl(passenger.contact)
            except:
                pass  # Contact might already exist
        
        # Create passenger opportunity
        if not passenger.id:
            self.push_passenger_to_ghl(passenger, force_create=True)
    
    def auto_sync_on_passenger_update(self, passenger: Passenger):
        """
        Automatically sync passenger updates to GHL.
        Call this after updating a passenger locally.
        """
        if passenger.id:
            self.push_passenger_to_ghl(passenger, force_create=False)
