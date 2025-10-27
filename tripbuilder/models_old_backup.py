"""
TripBuilder Database Models

SQLAlchemy models for all entities in the TripBuilder application.
These models map to both local database tables and GoHighLevel CRM entities.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Text, Integer, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Trip(db.Model):
    """
    Backend trip record that maps to TripBooking opportunities in GHL.
    
    One Trip = One TripBooking Opportunity (1:1 relationship)
    """
    __tablename__ = 'trips'
    
    id = db.Column(Integer, primary_key=True)
    destination = db.Column(String(200), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)
    notes = db.Column(Text)
    max_capacity = db.Column(Integer, default=10)
    
    # Link to GHL TripBooking opportunity
    ghl_opportunity_id = db.Column(String(100), unique=True)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    passengers = relationship('Passenger', back_populates='trip', cascade='all, delete-orphan')
    
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
    
    # Foreign keys
    contact_id = db.Column(String(100), ForeignKey('contacts.id'), nullable=False)
    trip_id = db.Column(Integer, ForeignKey('trips.id'), nullable=True)  # Now nullable - can link later
    stage_id = db.Column(String(100), ForeignKey('pipeline_stages.id'))
    
    # Custom field values cached from GHL
    custom_field_values = db.Column(JSON, default={})
    
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
