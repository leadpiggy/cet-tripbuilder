"""
GoHighLevel Sync Service

Handles bidirectional synchronization between local database and GHL CRM.
Implementation will be completed in Stage 2A.
"""

from datetime import datetime, date, timedelta
import uuid
from models import db, Pipeline, PipelineStage, CustomField, CustomFieldGroup, Contact, Trip, Passenger, SyncLog


class GHLSyncService:
    """
    Service for syncing data between local DB and GoHighLevel CRM.
    
    Sync operations:
    - Pipelines and stages
    - Custom field definitions
    - Contacts
    - Opportunities (TripBooking and Passenger)
    """
    
    def __init__(self, ghl_api):
        """
        Initialize sync service.
        
        Args:
            ghl_api: GoHighLevelAPI instance
        """
        self.api = ghl_api
    
    def sync_pipelines(self):
        """
        Sync pipeline definitions from GHL.
        
        Fetches pipelines and their stages from GHL and upserts to local DB.
        
        Returns:
            dict: {'pipelines': count, 'stages': count}
        """
        print("📊 Syncing pipelines...")
        
        # Fetch pipelines from GHL
        response = self.api.get_pipelines()
        pipelines_data = response.get('pipelines', [])
        
        pipeline_count = 0
        stage_count = 0
        
        for pipeline_data in pipelines_data:
            # Upsert pipeline
            pipeline = Pipeline.query.get(pipeline_data['id']) or Pipeline(id=pipeline_data['id'])
            pipeline.name = pipeline_data.get('name', 'Unnamed Pipeline')
            
            db.session.add(pipeline)
            pipeline_count += 1
            
            # Upsert stages
            stages_data = pipeline_data.get('stages', [])
            for stage_data in stages_data:
                stage = PipelineStage.query.get(stage_data['id']) or PipelineStage(id=stage_data['id'])
                stage.name = stage_data.get('name', 'Unnamed Stage')
                stage.pipeline_id = pipeline.id
                stage.position = stage_data.get('position', 0)
                
                db.session.add(stage)
                stage_count += 1
        
        db.session.commit()
        
        print(f"   ✅ Synced {pipeline_count} pipelines, {stage_count} stages")
        return {'pipelines': pipeline_count, 'stages': stage_count}
    
    def sync_custom_fields(self):
        """
        Sync custom field definitions from GHL.
        
        Returns:
            dict: {'groups': count, 'fields': count}
        """
        print("🔧 Syncing custom fields...")
        
        # Fetch custom fields for opportunities
        response = self.api.get_custom_fields(model='opportunity')
        fields_data = response.get('customFields', [])
        
        group_count = 0
        field_count = 0
        
        # Track unique groups
        groups_seen = set()
        
        for field_data in fields_data:
            # Get or create field group
            group_id = field_data.get('groupId')
            group_name = field_data.get('groupName', 'Ungrouped')
            
            if group_id and group_id not in groups_seen:
                group = CustomFieldGroup.query.get(group_id) or CustomFieldGroup(id=group_id)
                group.name = group_name
                db.session.add(group)
                groups_seen.add(group_id)
                group_count += 1
            
            # Upsert custom field
            field_id = field_data.get('id')
            if field_id:
                # Query by ghl_field_id instead of primary key
                field = CustomField.query.filter_by(ghl_field_id=field_id).first() or CustomField()
                field.ghl_field_id = field_id
                field.field_key = field_data.get('fieldKey', '')
                field.name = field_data.get('name', '')
                field.data_type = field_data.get('dataType', 'TEXT')
                field.model = field_data.get('model', 'opportunity')
                field.placeholder = field_data.get('placeholder', '')
                field.position = field_data.get('position', 0)
                field.custom_field_group_id = group_id
                
                # Store options if present (for dropdown/radio/checkbox fields)
                if 'options' in field_data:
                    field.options = field_data['options']
                
                db.session.add(field)
                field_count += 1
        
        db.session.commit()
        
        print(f"   ✅ Synced {group_count} field groups, {field_count} custom fields")
        return {'groups': group_count, 'fields': field_count}
    
    def sync_contacts(self, limit=100):
        """
        Sync contacts from GHL to local DB.
        
        Args:
            limit: Number of contacts per page
        
        Returns:
            int: Total contacts synced
        """
        print("👥 Syncing contacts...")
        
        contact_count = 0
        start_after_id = None
        start_after = None
        
        while True:
            # Build parameters - GHL needs BOTH startAfter (timestamp) AND startAfterId
            params = {'limit': limit, 'locationId': self.api.location_id}
            if start_after_id and start_after:
                params['startAfterId'] = start_after_id
                params['startAfter'] = start_after
            
            # Fetch page of contacts
            try:
                response = self.api._make_request("GET", "contacts/", params=params)
                contacts_data = response.get('contacts', [])
                
                if not contacts_data:
                    break  # No more contacts
                
                # Upsert each contact
                for contact_data in contacts_data:
                    contact_id = contact_data.get('id')
                    if not contact_id:
                        continue
                    
                    contact = Contact.query.get(contact_id) or Contact(id=contact_id)
                    contact.firstname = contact_data.get('firstName')
                    contact.lastname = contact_data.get('lastName')
                    contact.email = contact_data.get('email')
                    contact.phone = contact_data.get('phone')
                    contact.address = contact_data.get('address1')
                    contact.city = contact_data.get('city')
                    contact.state = contact_data.get('state')
                    contact.postal_code = contact_data.get('postalCode')
                    contact.country = contact_data.get('country')
                    contact.company_name = contact_data.get('companyName')
                    contact.website = contact_data.get('website')
                    contact.tags = contact_data.get('tags', [])
                    contact.source = contact_data.get('source')
                    contact.custom_fields = contact_data.get('customFields', {})
                    contact.last_synced_at = datetime.utcnow()
                    
                    db.session.add(contact)
                    contact_count += 1
                
                # Commit this batch
                try:
                    db.session.commit()
                    print(f"   📦 Synced batch: {len(contacts_data)} contacts (total: {contact_count})")
                except Exception as commit_error:
                    db.session.rollback()
                    print(f"   ⚠️  Error committing batch: {commit_error}")
                
                # Get pagination info from meta
                meta = response.get('meta', {})
                total_contacts = meta.get('total', 0)
                
                # GHL returns BOTH startAfterId and startAfter for pagination
                start_after_id = meta.get('startAfterId')
                start_after = meta.get('startAfter')
                
                if not start_after_id or not start_after:
                    print(f"   ℹ️  No more pagination data")
                    break
                
                # Check if we've synced all contacts
                if contact_count >= total_contacts:
                    print(f"   ℹ️  Synced all {total_contacts} contacts")
                    break
                
            except Exception as e:
                print(f"   ⚠️  Error syncing contacts: {e}")
                break
        
        print(f"   ✅ Total contacts synced: {contact_count}")
        return contact_count
    
    def sync_trip_opportunities(self, limit=100):
        """
        Sync TripBooking opportunities from GHL → trips table.
        
        Fetches all opportunities from TripBooking pipeline (IlWdPtOpcczLpgsde2KF)
        and creates/updates Trip records in local database.
        
        Args:
            limit: Number of opportunities per page
        
        Returns:
            int: Total trips synced
        """
        print("🗺️  Syncing TripBooking opportunities...")
        
        # TripBooking pipeline ID from PIPELINE_CUSTOM_FIELD_DATA.md
        TRIPBOOKING_PIPELINE_ID = "IlWdPtOpcczLpgsde2KF"
        
        trip_count = 0
        page = 1
        
        while True:
            # Use the API's search_opportunities method with pagination
            try:
                response = self.api.search_opportunities(
                    pipeline_id=TRIPBOOKING_PIPELINE_ID,
                    limit=limit,
                    page=page
                )
                opportunities_data = response.get('opportunities', [])
                total = response.get('total', 0)
                
                if not opportunities_data:
                    break
                
                print(f"   📦 Page {page}: Processing {len(opportunities_data)} opportunities (total so far: {trip_count})")
                
                # Process each trip using dynamic mapping
                for opp_data in opportunities_data:
                    opp_id = opp_data.get('id')
                    if not opp_id:
                        continue
                    
                    # Check if trip already exists with this GHL opportunity ID
                    trip = Trip.query.filter_by(ghl_opportunity_id=opp_id).first()
                    
                    if trip:
                        # Update existing trip
                        trip.update_from_ghl(opp_data)
                    else:
                        # Create new trip using dynamic mapping
                        trip = Trip.from_ghl_opportunity(opp_data)
                    
                    # Ensure required fields have defaults
                    if not trip.start_date:
                        trip.start_date = date.today()
                    if not trip.end_date:
                        trip.end_date = trip.start_date + timedelta(days=7)
                    if not trip.max_passengers:
                        trip.max_passengers = 10
                    
                    db.session.add(trip)
                    trip_count += 1
                
                # Commit this page
                try:
                    db.session.commit()
                except Exception as commit_error:
                    db.session.rollback()
                    print(f"   ⚠️  Error committing trips: {commit_error}")
                
                # Check if we've gotten all opportunities
                if trip_count >= total or len(opportunities_data) < limit:
                    print(f"   ℹ️  Reached end of results (synced {trip_count} of {total} total)")
                    break
                
                # Move to next page
                page += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error syncing trip opportunities: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"   ✅ Total trips synced: {trip_count}")
        return trip_count
    
    def sync_passenger_opportunities(self, limit=100):
        """
        Sync Passenger opportunities from GHL → passengers table.
        
        Fetches all opportunities from Passenger pipeline (fnsdpRtY9o83Vr4z15bE)
        and creates/updates Passenger records in local database.
        
        Args:
            limit: Number of opportunities per page
        
        Returns:
            int: Total passengers synced
        """
        print("👥 Syncing Passenger opportunities...")
        
        # Passenger pipeline ID from PIPELINE_CUSTOM_FIELD_DATA.md
        PASSENGER_PIPELINE_ID = "fnsdpRtY9o83Vr4z15bE"
        
        passenger_count = 0
        skipped_no_trip = 0
        skipped_no_contact = 0
        page = 1
        
        while True:
            # Use the API's search_opportunities method with pagination
            try:
                response = self.api.search_opportunities(
                    pipeline_id=PASSENGER_PIPELINE_ID,
                    limit=limit,
                    page=page
                )
                opportunities_data = response.get('opportunities', [])
                total = response.get('total', 0)
                
                if not opportunities_data:
                    break
                
                print(f"   📦 Page {page}: Processing {len(opportunities_data)} opportunities (total so far: {passenger_count})")
                
                # Process each passenger using dynamic mapping
                for opp_data in opportunities_data:
                    opp_id = opp_data.get('id')
                    contact_id = opp_data.get('contactId')
                    
                    if not opp_id or not contact_id:
                        continue
                    
                    # Check if contact exists locally
                    contact = Contact.query.get(contact_id)
                    if not contact:
                        # Skip passengers whose contact hasn't been synced
                        skipped_no_contact += 1
                        continue
                    
                    # Check if passenger already exists
                    passenger = Passenger.query.get(opp_id)
                    
                    if passenger:
                        # Update existing passenger
                        passenger.update_from_ghl(opp_data)
                    else:
                        # Create new passenger using dynamic mapping
                        passenger = Passenger.from_ghl_opportunity(opp_data)
                    
                    # Count passengers without trip link
                    # Trip linking will be handled separately via backpopulate script
                    if not passenger.trip_id:
                        skipped_no_trip += 1
                    
                    db.session.add(passenger)
                    passenger_count += 1
                
                # Commit this page
                try:
                    db.session.commit()
                except Exception as commit_error:
                    db.session.rollback()
                    print(f"   ⚠️  Error committing passengers: {commit_error}")
                
                # Check if this was the last page (got fewer results than limit)
                if len(opportunities_data) < limit:
                    print(f"   ℹ️  Reached end of results (synced {passenger_count} of {total} total)")
                    break
                
                # Move to next page
                page += 1
                    
            except Exception as e:
                print(f"   ⚠️  Error syncing passenger opportunities: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"   ℹ️  Synced without trip link (will match later): {skipped_no_trip}")
        print(f"   ℹ️  Skipped (contact not synced): {skipped_no_contact}")
        print(f"   ✅ Total passengers synced: {passenger_count}")
        return passenger_count
    
    def get_or_create_contact(self, contact_data):
        """
        Smart contact handling: check local DB, search GHL, create if needed.
        
        This is the core logic for passenger enrollment.
        
        Args:
            contact_data: Dict with firstname, lastname, email, phone, etc.
        
        Returns:
            Contact: Contact instance (from local DB)
        
        Steps:
            1. Check if contact exists in local DB by email
            2. If not, search GHL by email
            3. If found in GHL, sync to local DB
            4. If not in GHL, create in GHL, then sync to local DB
        """
        email = contact_data.get('email')
        
        # Step 1: Check local DB
        contact = Contact.query.filter_by(email=email).first()
        if contact:
            return contact
        
        # Step 2: Search GHL
        try:
            ghl_contacts = self.api.search_contacts(query=email, limit=1)
            
            if ghl_contacts.get('contacts'):
                # Found in GHL - sync to local
                ghl_contact = ghl_contacts['contacts'][0]
                contact = Contact(
                    id=ghl_contact['id'],
                    firstname=ghl_contact.get('firstName'),
                    lastname=ghl_contact.get('lastName'),
                    email=ghl_contact.get('email'),
                    phone=ghl_contact.get('phone'),
                    address=ghl_contact.get('address1'),
                    city=ghl_contact.get('city'),
                    state=ghl_contact.get('state'),
                    postal_code=ghl_contact.get('postalCode'),
                    country=ghl_contact.get('country'),
                    tags=ghl_contact.get('tags', []),
                    last_synced_at=datetime.utcnow()
                )
                db.session.add(contact)
                db.session.commit()
                return contact
        
        except Exception as e:
            print(f"Error searching GHL: {e}")
        
        # Step 3: Create in GHL
        try:
            ghl_response = self.api.create_contact(
                firstname=contact_data.get('firstname'),
                lastname=contact_data.get('lastname'),
                email=email,
                phone=contact_data.get('phone'),
                address=contact_data.get('address'),
                city=contact_data.get('city'),
                state=contact_data.get('state'),
                postal_code=contact_data.get('postal_code'),
                country=contact_data.get('country', 'United States'),
                tags=['trip-passenger']
            )
            
            # Sync to local DB
            ghl_contact = ghl_response['contact']
            contact = Contact(
                id=ghl_contact['id'],
                firstname=contact_data.get('firstname'),
                lastname=contact_data.get('lastname'),
                email=email,
                phone=contact_data.get('phone'),
                address=contact_data.get('address'),
                city=contact_data.get('city'),
                state=contact_data.get('state'),
                postal_code=contact_data.get('postal_code'),
                country=contact_data.get('country', 'United States'),
                tags=['trip-passenger'],
                last_synced_at=datetime.utcnow()
            )
            db.session.add(contact)
            db.session.commit()
            
            return contact
        
        except Exception as e:
            raise Exception(f"Failed to create contact in GHL: {str(e)}")
    
    def perform_full_sync(self):
        """
        Perform a complete sync of all data from GHL.
        
        Returns:
            dict: Summary of records synced
        """
        print("\n🔄 Starting full GHL sync...")
        print("=" * 60)
        
        results = {
            'pipelines': 0,
            'stages': 0,
            'groups': 0,
            'fields': 0,
            'contacts': 0,
            'trips': 0,
            'passengers': 0,
            'vendors': 0
        }
        
        # Create sync log
        sync_log = SyncLog(
            sync_type='full',
            status='in_progress',
            started_at=datetime.utcnow()
        )
        db.session.add(sync_log)
        db.session.commit()
        
        try:
            # Sync pipelines
            print("\n1️⃣  Syncing Pipelines & Stages...")
            pipeline_result = self.sync_pipelines()
            results['pipelines'] = pipeline_result['pipelines']
            results['stages'] = pipeline_result['stages']
            
            # Sync custom fields
            print("\n2️⃣  Syncing Custom Fields...")
            field_result = self.sync_custom_fields()
            results['groups'] = field_result['groups']
            results['fields'] = field_result['fields']
            
            # Sync contacts
            print("\n3️⃣  Syncing Contacts...")
            results['contacts'] = self.sync_contacts()
            
            # Sync trip opportunities
            print("\n4️⃣  Syncing Trip Opportunities...")
            results['trips'] = self.sync_trip_opportunities()
            
            # Sync passenger opportunities
            print("\n5️⃣  Syncing Passenger Opportunities...")
            
            # Sync vendors from GHL dropdown
            print("\n6️⃣  Syncing Vendors from GHL...")
            try:
                from services.vendor_sync import VendorSyncService
                vendor_sync = VendorSyncService(self.api)
                vendors_imported = vendor_sync.sync_vendors_from_ghl()
                results['vendors'] = vendors_imported
                print(f"   ✅ Imported {vendors_imported} new vendors from GHL")
            except Exception as vendor_error:
                print(f"   ⚠️  Vendor sync failed (non-critical): {vendor_error}")
                results['vendors'] = 0
            results['passengers'] = self.sync_passenger_opportunities()
            
            # Update sync log
            sync_log.status = 'success'
            sync_log.records_synced = sum(results.values())
            sync_log.completed_at = datetime.utcnow()
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ Sync complete!")
            print(f"   Pipelines: {results['pipelines']}")
            print(f"   Stages: {results['stages']}")
            print(f"   Custom Field Groups: {results['groups']}")
            print(f"   Custom Fields: {results['fields']}")
            print(f"   Contacts: {results['contacts']}")
            print(f"   Trips: {results['trips']}")
            print(f"   Passengers: {results['passengers']}")
            print(f"   Vendors: {results['vendors']}")
            print(f"   Total Records: {sync_log.records_synced}")
            
        except Exception as e:
            print(f"\n❌ Sync failed: {e}")
            sync_log.status = 'failed'
            sync_log.errors = [str(e)]
            sync_log.completed_at = datetime.utcnow()
            db.session.commit()
            raise
        
        return results
