"""
TripBuilder Database Models

SQLAlchemy models for all entities in the TripBuilder application.
These models map to both local database tables and GoHighLevel CRM entities.

IMPORTANT: This file reflects the ACTUAL database schema.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Text, Integer, Date, DateTime, JSON, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Trip(db.Model):
    """
    Backend trip record that maps to TripBooking opportunities in GHL.
    
    One Trip = One TripBooking Opportunity (1:1 relationship)
    """
    __tablename__ = 'trips'
    
    # Primary key
    id = db.Column(Integer, primary_key=True)
    public_id = db.Column(String(36), unique=True)
    
    # Basic trip info
    name = db.Column(String(255))
    destination = db.Column(String(255))
    description = db.Column(Text)
    trip_description = db.Column(Text)
    cover_image = db.Column(String(500))
    
    # Dates
    start_date = db.Column(Date)
    end_date = db.Column(Date)
    arrival_date = db.Column(Date)
    return_date = db.Column(Date)
    deposit_date = db.Column(Date)
    final_payment = db.Column(Date)
    
    # Capacity and counts
    max_passengers = db.Column(Integer, default=10)
    current_passengers = db.Column(Integer, default=0)
    passenger_count = db.Column(Integer, default=0)
    
    # Pricing
    base_price = db.Column(Numeric(10, 2))
    currency = db.Column(String(3), default='USD')
    trip_standard_level_pricing = db.Column(Numeric(10, 2))
    
    # Vendor info
    trip_vendor = db.Column(String(255))  # Legacy field (keep for backwards compatibility)
    trip_vendor_id = db.Column(Integer, ForeignKey('trip_vendors.id'), nullable=True)
    vendor_terms = db.Column(Text)
    travel_business_used = db.Column(String(255))
    
    # Trip details
    travel_category = db.Column(String(255))
    nights_total = db.Column(Integer)
    lodging = db.Column(String(255))
    lodging_notes = db.Column(Text)
    internal_trip_details = db.Column(Text)
    
    # Status and visibility
    status = db.Column(String(50), default='draft')
    is_public = db.Column(Boolean, default=False)
    
    # Additional fields (from GHL mapping)
    birth_country = db.Column(String(255))
    passenger_id = db.Column(String(255))
    passenger_first_name = db.Column(String(255))
    passenger_last_name = db.Column(String(255))
    passenger_number = db.Column(Integer)
    trip_id_custom = db.Column(Integer)
    trip_name = db.Column(String(255))
    is_child = db.Column(Boolean)
    
    # Link to GHL TripBooking opportunity
    ghl_opportunity_id = db.Column(String(100), unique=True)
    contact_id = db.Column(String(100))
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    passengers = relationship('Passenger', back_populates='trip', cascade='all, delete-orphan')
    vendor = relationship('TripVendor', back_populates='trips')
    
    def __repr__(self):
        return f'<Trip {self.id}: {self.destination}>'


class Contact(db.Model):
    """
    Contact record synced from GoHighLevel.
    Cached locally for performance and offline access.
    """
    __tablename__ = 'contacts'
    
    # GHL contact ID is the primary key
    id = db.Column(String(100), primary_key=True)
    
    # Basic info
    firstname = db.Column(String(100))
    lastname = db.Column(String(100))
    email = db.Column(String(200), unique=True)
    phone = db.Column(String(50))
    
    # Address
    address = db.Column(String(200))
    city = db.Column(String(100))
    state = db.Column(String(50))
    postal_code = db.Column(String(20))
    country = db.Column(String(100))
    
    # Additional
    company_name = db.Column(String(200))
    website = db.Column(String(200))
    tags = db.Column(ARRAY(String), default=[])
    source = db.Column(String(100))
    
    # Custom fields stored as JSON
    custom_fields = db.Column(JSON, default={})
    
    # Sync tracking
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = db.Column(DateTime)
    
    # Relationships
    passengers = relationship('Passenger', back_populates='contact')
    
    def __repr__(self):
        return f'<Contact {self.id}: {self.firstname} {self.lastname}>'


class Passenger(db.Model):
    """
    Junction table linking Contacts to Trips.
    Maps to Passenger opportunities in GHL (one per Contact-Trip pairing).
    
    The id is the GHL Passenger opportunity ID.
    """
    __tablename__ = 'passengers'
    
    # GHL Passenger opportunity ID
    id = db.Column(String(100), primary_key=True)
    
    # Basic passenger info (denormalized for performance)
    firstname = db.Column(String(100))
    lastname = db.Column(String(100))
    email = db.Column(String(150))
    phone = db.Column(String(20))
    date_of_birth = db.Column(Date)
    gender = db.Column(String(20))
    
    # Status
    status = db.Column(String(50))
    registration_completed = db.Column(Boolean, default=False)
    documents_completed = db.Column(Boolean, default=False)
    
    # Foreign keys
    contact_id = db.Column(String(100), ForeignKey('contacts.id'), nullable=False)
    trip_id = db.Column(Integer, ForeignKey('trips.id'))
    stage_id = db.Column(String(100), ForeignKey('pipeline_stages.id'))
    
    # Documents
    reservation = db.Column(String(500))
    mou = db.Column(String(500))
    affidavit = db.Column(String(500))
    
    # Health information
    health_state = db.Column(Text)
    health_medical_info = db.Column(Text)
    primary_phy = db.Column(String(255))
    physician_phone = db.Column(String(255))
    medication_list = db.Column(Text)
    
    # Room preferences
    user_roomate = db.Column(String(255))
    room_occupancy = db.Column(String(255))
    
    # Emergency contact
    contact1_ulast_name = db.Column(String(255))
    contact1_ufirst_name = db.Column(String(255))
    contact1_urelationship = db.Column(String(255))
    contact1_umailing_address = db.Column(String(255))
    contact1_ucity = db.Column(String(255))
    contact1_uzip = db.Column(String(255))
    contact1_uemail = db.Column(String(255))
    contact1_uphone = db.Column(String(255))
    contact1_umob_number = db.Column(String(255))
    contact1_ustate = db.Column(String(255))
    
    # Passport information
    passport_number = db.Column(String(255))
    passport_expire = db.Column(Date)
    passport_file = db.Column(String(500))
    passport_country = db.Column(String(255))
    
    # Legal
    form_submitted_date = db.Column(Date)
    travel_category_license = db.Column(String(255))
    passenger_signature = db.Column(Text)
    
    # Trip linking
    trip_name = db.Column(String(255))
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = db.Column(DateTime)
    
    # Relationships
    contact = relationship('Contact', back_populates='passengers')
    trip = relationship('Trip', back_populates='passengers')
    stage = relationship('PipelineStage')
    
    def __repr__(self):
        return f'<Passenger {self.id}: Contact {self.contact_id} on Trip {self.trip_id}>'


class Pipeline(db.Model):
    """
    GHL Pipeline definition.
    Two pipelines: TripBooking and Passenger.
    """
    __tablename__ = 'pipelines'
    
    # GHL pipeline ID
    id = db.Column(String(100), primary_key=True)
    name = db.Column(String(100), nullable=False)
    
    # Relationships
    stages = relationship('PipelineStage', back_populates='pipeline', order_by='PipelineStage.position')
    custom_field_groups = relationship('CustomFieldGroup', back_populates='pipeline')
    
    def __repr__(self):
        return f'<Pipeline {self.name}>'


class PipelineStage(db.Model):
    """
    Stage within a pipeline.
    Defines workflow progression for opportunities.
    """
    __tablename__ = 'pipeline_stages'
    
    # GHL stage ID
    id = db.Column(String(100), primary_key=True)
    name = db.Column(String(100), nullable=False)
    position = db.Column(Integer, nullable=False)
    
    # Foreign key
    pipeline_id = db.Column(String(100), ForeignKey('pipelines.id'), nullable=False)
    
    # Relationships
    pipeline = relationship('Pipeline', back_populates='stages')
    
    def __repr__(self):
        return f'<PipelineStage {self.name} (pos {self.position})>'


class CustomFieldGroup(db.Model):
    """
    Grouping for custom fields (e.g., "Passport Info", "Health Details").
    """
    __tablename__ = 'custom_field_groups'
    
    # GHL group ID
    id = db.Column(String(100), primary_key=True)
    name = db.Column(String(100), nullable=False)
    model = db.Column(String(50), nullable=False)  # 'opportunity' or 'contact'
    
    # Optional: linked to specific pipeline
    pipeline_id = db.Column(String(100), ForeignKey('pipelines.id'))
    
    # Relationships
    pipeline = relationship('Pipeline', back_populates='custom_field_groups')
    custom_fields = relationship('CustomField', back_populates='group', order_by='CustomField.position')
    
    def __repr__(self):
        return f'<CustomFieldGroup {self.name}>'


class CustomField(db.Model):
    """
    Custom field definition from GHL.
    Defines field name, type, options, validation rules.
    """
    __tablename__ = 'custom_fields'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    
    # GHL field ID
    ghl_field_id = db.Column(String(100), unique=True, nullable=False)
    
    # Field definition
    name = db.Column(String(200), nullable=False)
    field_key = db.Column(String(200), nullable=False, unique=True)  # e.g., "opportunity.passportnumber"
    data_type = db.Column(String(50), nullable=False)  # TEXT, LARGETEXT, SINGLEOPTIONS, etc.
    model = db.Column(String(50), nullable=False)  # 'opportunity' or 'contact'
    
    # Additional metadata
    placeholder = db.Column(String(200))
    options = db.Column(ARRAY(String), default=[])  # For dropdown/checkbox fields
    position = db.Column(Integer, default=0)
    
    # Foreign key
    custom_field_group_id = db.Column(String(100), ForeignKey('custom_field_groups.id'))
    
    # Relationships
    group = relationship('CustomFieldGroup', back_populates='custom_fields')
    
    def __repr__(self):
        return f'<CustomField {self.name} ({self.field_key})>'


class FieldMap(db.Model):
    """
    Dynamic mapping between GHL custom fields and database columns.
    Maps GHL field IDs to specific table columns for flexible sync.
    """
    __tablename__ = 'field_maps'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    
    # GHL field identifier (the field ID from GHL)
    ghl_key = db.Column(String(100), unique=True, nullable=False)
    
    # Field key (e.g., "opportunity.trip_name")
    field_key = db.Column(String(200), nullable=False)
    
    # Database mapping
    table_column = db.Column(String(100), nullable=False)  # Column name
    tablename = db.Column(String(100), nullable=False)  # Table name
    data_type = db.Column(String(50), nullable=False)  # string, integer, date, etc.
    
    def __repr__(self):
        return f'<FieldMap {self.tablename}.{self.table_column} <- {self.field_key}>'


class SyncLog(db.Model):
    """
    Log of synchronization operations with GHL.
    Tracks success/failure, records synced, errors encountered.
    """
    __tablename__ = 'sync_logs'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    
    sync_type = db.Column(String(50), nullable=False)  # 'contacts', 'pipelines', 'opportunities', 'full'
    status = db.Column(String(20), nullable=False)  # 'success', 'partial', 'failed', 'in_progress'
    records_synced = db.Column(Integer, default=0)
    
    # Error details stored as JSON array
    errors = db.Column(JSON, default=[])
    
    # Timestamps
    started_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    
    def __repr__(self):
        return f'<SyncLog {self.id}: {self.sync_type} - {self.status}>'


class File(db.Model):
    """
    File storage record for S3-uploaded files.
    Tracks passports, signatures, PDFs, and other documents.
    Links files to trips and passengers.
    """
    __tablename__ = 'files'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    
    # File metadata
    filename = db.Column(String(255), nullable=False)
    s3_key = db.Column(String(500), nullable=False, unique=True)
    file_type = db.Column(String(50), nullable=False)  # passport, signature, document, pdf
    content_type = db.Column(String(100))  # MIME type (image/jpeg, application/pdf)
    file_size = db.Column(Integer)  # Size in bytes
    
    # Public access
    is_public = db.Column(Boolean, default=False)  # If True, has Public=yes tag
    
    # Link to opportunities (trips or passengers)
    opportunity_type = db.Column(String(20))  # 'trip' or 'passenger'
    
    # Foreign keys
    trip_id = db.Column(Integer, ForeignKey('trips.id'), nullable=True)
    passenger_id = db.Column(String(100), ForeignKey('passengers.id'), nullable=True)
    
    # Upload tracking
    uploaded_at = db.Column(DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(String(100))  # Contact ID or username
    
    # Relationships
    trip = relationship('Trip')
    passenger = relationship('Passenger')
    
    def __repr__(self):
        return f'<File {self.id}: {self.filename} ({self.file_type})>'
    
    @property
    def public_url(self):
        """Get public S3 URL if file is public"""
        if self.is_public:
            return f"https://cet-uploads.s3.amazonaws.com/{self.s3_key}"
        return None
    
    def get_download_url(self, expiration=3600):
        """Generate temporary download URL"""
        from services.file_manager import file_manager


class TripVendor(db.Model):
    """
    Trip vendor with bidirectional GHL sync.
    Vendors are stored locally and synced to GHL custom field dropdown options.
    
    When a vendor is created/deleted, SQLAlchemy event listeners
    automatically update the GHL opportunity.tripvendor dropdown.
    """
    __tablename__ = 'trip_vendors'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(200), nullable=False, unique=True)
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = relationship('Trip', back_populates='vendor')
    
    def __repr__(self):
        return f'<TripVendor {self.id}: {self.name}>'


class DropdownCache(db.Model):
    """
    Cache for GHL custom field dropdown values.
    Improves performance by caching dropdown options locally
    instead of making live API calls for every form render.
    
    Updated during GHL sync operations.
    """
    __tablename__ = 'dropdown_cache'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    field_key = db.Column(String(100), unique=True, nullable=False)  # e.g., 'opportunity.travelcategory'
    options = db.Column(JSON, nullable=False)  # List of option values
    last_synced = db.Column(DateTime, default=datetime.utcnow)
    
    @classmethod
    def get_options(cls, field_key):
        """Get cached options for a field"""
        cache = cls.query.filter_by(field_key=field_key).first()
        return cache.options if cache else []
    
    @classmethod
    def update_options(cls, field_key, options):
        """Update cached options for a field"""
        cache = cls.query.filter_by(field_key=field_key).first()
        if cache:
            cache.options = options
            cache.last_synced = datetime.utcnow()
        else:
            cache = cls(field_key=field_key, options=options)
            db.session.add(cache)
        db.session.commit()
    
    def __repr__(self):
        return f'<DropdownCache {self.field_key}: {len(self.options)} options>'


# =====================================================================
# SQLALCHEMY EVENT LISTENERS FOR VENDOR SYNC
# =====================================================================

from sqlalchemy import event

@event.listens_for(TripVendor, 'after_insert')
def vendor_after_insert(mapper, connection, target):
    """
    Auto-sync new vendor to GHL dropdown after commit.
    
    This event listener triggers after a TripVendor is inserted into the database.
    It adds the vendor name to the GHL opportunity.tripvendor dropdown options.
    """
    @event.listens_for(db.session, 'after_commit', once=True)
    def add_to_ghl(session):
        try:
            from services.vendor_sync import VendorSyncService
            from ghl_api import GoHighLevelAPI
            import os
            
            # Initialize GHL API and sync service
            ghl_api = GoHighLevelAPI(
                location_id=os.getenv('GHL_LOCATION_ID'),
                api_key=os.getenv('GHL_API_TOKEN')
            )
            vendor_sync = VendorSyncService(ghl_api)
            
            # Add vendor to GHL dropdown
            vendor_sync.add_vendor_to_ghl(target)
            print(f"✅ Event listener: Added vendor '{target.name}' to GHL dropdown")
            
        except Exception as e:
            print(f"⚠️  Event listener: Failed to add vendor to GHL: {e}")
            # Don't raise - we want the database operation to succeed even if GHL sync fails


@event.listens_for(TripVendor, 'before_delete')
def vendor_before_delete(mapper, connection, target):
    """
    Auto-sync vendor deletion to GHL dropdown before delete.
    
    This event listener triggers before a TripVendor is deleted from the database.
    It removes the vendor name from the GHL opportunity.tripvendor dropdown options.
    
    Note: We use 'before_delete' because we need access to target.name,
    which won't be available in 'after_delete'.
    """
    try:
        from services.vendor_sync import VendorSyncService
        from ghl_api import GoHighLevelAPI
        import os
        
        # Initialize GHL API and sync service
        ghl_api = GoHighLevelAPI(
            location_id=os.getenv('GHL_LOCATION_ID'),
            api_key=os.getenv('GHL_API_TOKEN')
        )
        vendor_sync = VendorSyncService(ghl_api)
        
        # Remove vendor from GHL dropdown
        vendor_sync.remove_vendor_from_ghl(target)
        print(f"✅ Event listener: Removed vendor '{target.name}' from GHL dropdown")
        
    except Exception as e:
        print(f"⚠️  Event listener: Failed to remove vendor from GHL: {e}")
        # Don't raise - we want the database operation to succeed even if GHL sync fails
        return f'<DropdownCache {self.field_key}: {len(self.options)} options>'
        return file_manager.generate_download_url(self.s3_key, expiration)
