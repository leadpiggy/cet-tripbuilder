# TripBuilder Application - Project Description

## Overview
TripBuilder is a comprehensive CRUD dashboard application designed to manage travel operations through GoHighLevel (GHL) CRM. The application serves as an internal tool to coordinate **Trips** (backend database objects) with **Contacts** (GHL CRM records) via **two distinct opportunity pipelines**, creating a complete workflow for travel booking and passenger management.

## Core Concept
The TripBuilder application bridges the gap between:
- **Backend Trip Records**: Database entities representing travel arrangements (destination, dates, vendor details)
- **GHL Contacts**: Individual travelers and trip organizers in the CRM
- **Two Opportunity Pipelines**: 
  1. **TripBooking Pipeline** (ID: IlWdPtOpcczLpgsde2KF) - Manages the overall trip creation and finalization workflow
  2. **Passenger Pipeline** (ID: fnsdpRtY9o83Vr4z15bE) - Manages individual passenger/traveler enrollment and details for each trip

## Application Architecture

### Data Model Relationships
```
Trip (Backend DB)
  ↓
  ├─→ TripBooking Opportunity (GHL) - One per trip
  │   └─→ Stages: FormSubmit → TripFinalized → TravelersAdded → TripScheduled → TripComplete
  │
  └─→ Passenger Opportunities (GHL) - Multiple per trip, one per traveler/contact
      └─→ Stages: AddedToTrip → DetailsSubmitted → TripDetailsSent → TripReady → TripInProgress → TripComplete
```

### Two Pipeline System

#### 1. TripBooking Pipeline (Trip-Level)
Manages the overall trip lifecycle:
- **FormSubmit** (Stage 0): Initial trip inquiry/booking form submitted
- **TripFinalized** (Stage 1): Trip details confirmed (destination, dates, vendor)
- **TravelersAdded** (Stage 2): Passengers/contacts linked to the trip
- **TripScheduled** (Stage 3): All logistics confirmed and scheduled
- **TripComplete** (Stage 4): Trip concluded

**Purpose**: One TripBooking opportunity exists per Trip, tracking the master trip record through GHL.

#### 2. Passenger Pipeline (Passenger-Level)
Manages individual traveler enrollment and details:
- **AddedToTrip** (Stage 0): Contact added as passenger to a trip
- **DetailsSubmitted** (Stage 1): Personal/passport/health details collected
- **TripDetailsSent** (Stage 2): Trip information sent to passenger
- **TripReady** (Stage 3): Passenger fully prepared for travel
- **TripInProgress** (Stage 4): Passenger actively on trip
- **TripComplete** (Stage 5): Passenger completed trip

**Purpose**: Each Contact traveling on a Trip has a Passenger opportunity tracking their individual journey through the workflow.

### Custom Field Groups
The application manages extensive custom field groups across both pipelines and contact records:

**TripBooking Pipeline Fields**:
- Opportunity Details
- Vendor Info
- Trip Details
- Internal

**Passenger Pipeline Fields**:
- Room Info
- Passport Info
- Health Details
- Emergency Contact
- Legal
- Files

**Contact Fields**:
- Additional Info
- Trip Inquiry
- Legal

## Key Features
1. **Trip Management**: Create, view, edit backend Trip records (destination, dates, capacity)
2. **TripBooking Opportunity Sync**: Automatically create/update GHL opportunities for each Trip
3. **Passenger Enrollment**: Add Contacts as passengers to Trips, creating Passenger opportunities
4. **Pipeline Stage Management**: Move opportunities through workflow stages as processes complete
5. **Custom Field Data Entry**: Capture extensive traveler details via custom field forms
6. **Contact-Trip Mapping**: Visualize which contacts are on which trips and their status
7. **Dual-View Interface**: 
   - Trip-centric view (see all passengers for a trip)
   - Contact-centric view (see all trips for a contact)

## Technical Foundation
- **Backend**: Python Flask with SQLAlchemy ORM for Trip database
- **GHL Integration**: Python API wrapper for all CRM operations
- **Data Sync**: Bidirectional sync between backend Trips and GHL opportunities
- **Authentication**: Private Integration API token (Bearer auth)
- **Frontend**: Jinja2 templates with Bootstrap 5

## User Workflows

### Creating a New Trip
1. Create Trip record in backend (destination, dates)
2. System creates TripBooking opportunity in GHL
3. TripBooking starts at "FormSubmit" stage
4. Progress to "TripFinalized" when details confirmed

### Adding Passengers to Trip
1. Search/select existing Contacts or create new ones
2. Link Contact to Trip
3. System creates Passenger opportunity for each Contact
4. Passenger opportunity starts at "AddedToTrip" stage
5. Collect passenger details (passport, health, etc.) via custom fields
6. Progress through stages as passenger completes requirements

### Managing Trip Lifecycle
1. View Trip with all linked passengers
2. Track stage progression for TripBooking and each Passenger
3. Update custom fields as information is gathered
4. Move opportunities through pipeline stages
5. Complete trip and archive

## Data Sources (CSV Files)
- `pipelines.csv`: Two pipeline definitions
- `pipeline_stages.csv`: 11 stages across both pipelines
- `custom_fields.csv`: 100+ custom field definitions
- `custom_field_groups.csv`: 13 field group configurations
- `base.py.txt`: SQLAlchemy models for Trip, Contact, Pipeline entities

## Success Criteria
- Seamless mapping between backend Trips and GHL opportunities
- Clear visibility into trip and passenger status
- Efficient data entry for passenger details
- Automated opportunity creation and stage progression
- Reliable sync between systems
- User-friendly interface for non-technical staff