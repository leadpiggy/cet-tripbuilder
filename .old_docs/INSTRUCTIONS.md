# TripBuilder - Claude Code Instructions

## Overview
This document provides comprehensive instructions for Claude Code to build the TripBuilder application—a Flask-based CRUD dashboard that manages **backend Trip records** and syncs them with **GoHighLevel (GHL) CRM** via **two opportunity pipelines** (TripBooking and Passenger).

---

## Application Purpose

TripBuilder is NOT a simple contact/task manager. It is a **travel operations management system** that:

1. **Manages backend Trip records** (destination, dates, capacity, notes)
2. **Syncs each Trip to a TripBooking opportunity** in GHL (one-to-one relationship)
3. **Links multiple Contacts to each Trip** as passengers
4. **Creates a Passenger opportunity** in GHL for each Contact-Trip link (many-to-many via junction)
5. **Tracks progress through two separate pipelines**:
   - **TripBooking Pipeline**: Trip-level workflow (FormSubmit → TripFinalized → TravelersAdded → TripScheduled → TripComplete)
   - **Passenger Pipeline**: Passenger-level workflow (AddedToTrip → DetailsSubmitted → TripDetailsSent → TripReady → TripInProgress → TripComplete)
6. **Manages extensive custom fields** for both pipelines (passport info, health details, vendor info, etc.)

---

## Key Architectural Concepts

### Data Flow
```
Backend DB (SQLite/PostgreSQL)          GoHighLevel CRM (via API)
─────────────────────────────────      ────────────────────────────
Trip (id, destination, dates)    ←→    TripBooking Opportunity (pipeline: TripBooking)
                                        ├─ Stage: FormSubmit/TripFinalized/etc.
                                        └─ Custom Fields: Vendor Info, Trip Details
        ↓
   Trip-Contact Links (many-to-many)
        ↓
Contact (firstname, lastname)    ←→    GHL Contact (synced from API)
        ↓
Passenger (junction record)      ←→    Passenger Opportunity (pipeline: Passenger)
                                        ├─ Stage: AddedToTrip/DetailsSubmitted/etc.
                                        ├─ Custom Fields: Passport, Health, Emergency Contact
                                        └─ Links to: Contact + Trip (via custom field or name)
```

### Two Pipeline System

**TripBooking Pipeline** (ID: `IlWdPtOpcczLpgsde2KF`):
- **Purpose**: Track overall trip from inquiry to completion
- **Scope**: One opportunity per Trip
- **Stages**: 5 stages (FormSubmit → TripComplete)
- **Custom Field Groups**: Opportunity Details, Vendor Info, Trip Details, Internal

**Passenger Pipeline** (ID: `fnsdpRtY9o83Vr4z15bE`):
- **Purpose**: Track each passenger's journey through trip preparation
- **Scope**: One opportunity per Contact-Trip pairing
- **Stages**: 6 stages (AddedToTrip → TripComplete)
- **Custom Field Groups**: Room Info, Passport Info, Health Details, Emergency Contact, Legal, Files

---

## Database Models (from base.py.txt)

### Key Models

**Trip**:
- `id` (Integer, PK)
- `destination` (String) - Trip destination
- `start_date` (Date) - Trip start
- `end_date` (Date) - Trip end
- `notes` (Text) - Trip notes
- `ghl_opportunity_id` (String) - Linked TripBooking opportunity ID in GHL
- `created_at`, `updated_at` (DateTime)

**Contact** (synced from GHL):
- `id` (Text, PK) - GHL contact ID
- `firstname`, `lastname` (String)
- `email` (String, unique)
- `phone` (String)
- `tags` (ARRAY[String])
- `business` (String)

**Passenger** (junction table):
- `id` (String, PK) - GHL Passenger opportunity ID
- `contact_id` (FK to Contact)
- `trip_id` (FK to Trip)
- `stage_id` (FK to PipelineStage) - Current stage in Passenger pipeline
- Custom fields stored in GHL, not locally

**Pipeline**:
- `id` (String, PK) - GHL pipeline ID
- `name` (String) - "TripBooking" or "Passenger"

**PipelineStage**:
- `id` (String, PK) - GHL stage ID
- `name` (String) - Stage name
- `position` (Integer) - Order in pipeline (0-indexed)
- `pipeline_id` (FK to Pipeline)

**CustomField**:
- `id` (Integer, PK)
- `name` (String) - Display name
- `field_key` (String) - API key (e.g., "opportunity.passport_number")
- `data_type` (String) - TEXT, LARGE_TEXT, SINGLE_OPTION, FILEUPLOAD, etc.
- `model` (String) - "opportunity" or "contact"
- `options` (ARRAY[String]) - For dropdown/checkbox fields
- `custom_field_group_id` (FK to CustomFieldGroup)

**CustomFieldGroup**:
- `id` (String, PK)
- `name` (String) - "Passport Info", "Vendor Info", etc.
- `model` (String) - "opportunity" or "contact"
- `pipeline_id` (FK to Pipeline) - Null for contact fields

---

## GHL API Wrapper Usage

The `ghl-api-wrapper-complete.py` file provides a Python class to interact with GHL API v2.

### Initialization
```python
from ghl_api_wrapper_complete import GoHighLevelAPI  # Adjust import based on actual class name

ghl = GoHighLevelAPI(
    api_key=os.getenv('GHL_API_TOKEN'),
    location_id=os.getenv('GHL_LOCATION_ID')
)
```

### Expected Wrapper Methods

**Contacts**:
- `ghl.contacts.search(location_id, query=None)` → List[Dict]
- `ghl.contacts.get(contact_id)` → Dict
- `ghl.contacts.create(contact_data)` → Dict
- `ghl.contacts.update(contact_id, contact_data)` → Dict
- `ghl.contacts.delete(contact_id)` → Success

**Opportunities**:
- `ghl.opportunities.create(opportunity_data)` → Dict
  - Required fields: `name`, `pipeline_id`, `stage_id`, `contact_id`, `location_id`
- `ghl.opportunities.get(opportunity_id)` → Dict
- `ghl.opportunities.update(opportunity_id, data)` → Dict
- `ghl.opportunities.update_stage(opportunity_id, stage_id)` → Dict
- `ghl.opportunities.upsert_custom_field(opportunity_id, field_key, value)` → Success
- `ghl.opportunities.delete(opportunity_id)` → Success

**Tasks**:
- `ghl.tasks.get_all(contact_id)` → List[Dict]
- `ghl.tasks.create(contact_id, task_data)` → Dict
- `ghl.tasks.update(contact_id, task_id, data)` → Dict
- `ghl.tasks.mark_complete(contact_id, task_id)` → Dict
- `ghl.tasks.delete(contact_id, task_id)` → Success

**Custom Fields**:
- `ghl.custom_fields.get_by_location(location_id)` → List[Dict]

---

## Critical Implementation Requirements

### 1. Trip-to-TripBooking Sync
When a Trip is created:
1. Insert Trip record in database
2. Call `ghl.opportunities.create()` with:
   - `name`: f"Trip: {trip.destination}"
   - `pipeline_id`: "IlWdPtOpcczLpgsde2KF" (TripBooking pipeline)
   - `stage_id`: Stage ID for "FormSubmit" (from pipeline_stages.csv)
   - `contact_id`: A default contact or trip organizer's contact ID
   - `location_id`: From environment variable
3. Store returned opportunity ID in `trip.ghl_opportunity_id`
4. Update Trip record in database

When Trip is updated:
- Update TripBooking opportunity via `ghl.opportunities.update()`

When Trip is deleted:
- Delete TripBooking opportunity via `ghl.opportunities.delete()`
- Delete all Passenger opportunities for this trip
- Delete Trip record

### 2. Contact-Trip Link via Passenger Opportunities
When adding a Contact to a Trip:
1. Verify Contact exists in GHL (or create if new)
2. Call `ghl.opportunities.create()` with:
   - `name`: f"Trip: {trip.destination} - {contact.firstname} {contact.lastname}"
   - `pipeline_id`: "fnsdpRtY9o83Vr4z15bE" (Passenger pipeline)
   - `stage_id`: Stage ID for "AddedToTrip"
   - `contact_id`: GHL contact ID
   - `location_id`: From environment
3. Store returned opportunity ID as Passenger record:
   - `id`: GHL opportunity ID
   - `contact_id`: Contact ID
   - `trip_id`: Trip ID
   - `stage_id`: Initial stage ID
4. Insert Passenger record in database

When removing a Contact from a Trip:
- Delete Passenger opportunity from GHL
- Delete Passenger record from database

### 3. Custom Field Management
For Passenger opportunities:
1. Query CustomField records filtered by:
   - `model = 'opportunity'`
   - `custom_field_group.pipeline_id = 'fnsdpRtY9o83Vr4z15bE'` (Passenger pipeline)
2. Group fields by `custom_field_group.name`
3. Render forms grouped by CustomFieldGroup
4. On form submit, for each field:
   - Call `ghl.opportunities.upsert_custom_field(passenger.id, field.field_key, value)`

For TripBooking opportunities:
- Same process but filter by TripBooking pipeline ID

### 4. Stage Progression
To move an opportunity to the next stage:
1. Query current stage
2. Find next stage (current.position + 1)
3. Call `ghl.opportunities.update_stage(opportunity_id, next_stage_id)`
4. Update local Passenger record's `stage_id` if applicable

---

## Required Routes & Templates

### Routes

**Trips**:
- `GET /trips` - List all trips
- `GET /trips/new` - New trip form
- `POST /trips/new` - Create trip + TripBooking opportunity
- `GET /trips/<trip_id>` - Trip detail with passengers
- `POST /trips/<trip_id>/edit` - Update trip + sync to GHL
- `POST /trips/<trip_id>/delete` - Delete trip + opportunities

**Passengers**:
- `GET /trips/<trip_id>/add-passenger` - Form to add passenger
- `POST /trips/<trip_id>/add-passenger` - Create Passenger opportunity
- `POST /passengers/<passenger_id>/remove` - Remove passenger
- `GET /passengers/<passenger_id>` - Passenger detail with custom fields
- `POST /passengers/<passenger_id>/custom-fields` - Update custom fields

**Contacts**:
- `GET /contacts` - List contacts from GHL
- `GET /contacts/new` - New contact form
- `POST /contacts/new` - Create contact in GHL
- `GET /contacts/<contact_id>` - Contact detail with trips
- `POST /contacts/<contact_id>/edit` - Update contact in GHL
- `POST /contacts/<contact_id>/delete` - Delete contact

**Opportunities**:
- `POST /opportunities/<opportunity_id>/progress` - Move to next stage

**Tasks**:
- `POST /contacts/<contact_id>/tasks/new` - Create task
- `POST /tasks/<task_id>/complete` - Mark complete
- `POST /tasks/<task_id>/delete` - Delete task

### Templates

**Base**:
- `templates/base.html` - Layout with navbar, flash messages, Bootstrap

**Trips**:
- `templates/trips/list.html` - Table of trips
- `templates/trips/detail.html` - Trip info, passengers list, add passenger button
- `templates/trips/form.html` - Create/edit trip form

**Contacts**:
- `templates/contacts/list.html` - Table of contacts
- `templates/contacts/detail.html` - Contact info, trips list, tasks
- `templates/contacts/form.html` - Create/edit contact form

**Passengers**:
- `templates/passengers/add_to_trip.html` - Select contact, add to trip
- `templates/passengers/detail.html` - Custom field groups (collapsible sections)

**Dashboard**:
- `templates/dashboard.html` - Overview of trips, passengers, stages

---

## Seeding Database from CSV Files

Create a script (`seed.py`) to import CSV data:

```python
import csv
from app import db
from models import Pipeline, PipelineStage, CustomFieldGroup, CustomField

# Pipelines
with open('data/pipelines.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pipeline = Pipeline(id=row['id'], name=row['name'])
        db.session.add(pipeline)
    db.session.commit()

# Pipeline Stages
with open('data/pipeline_stages.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stage = PipelineStage(
            id=row['id'],
            name=row['name'],
            position=int(row['position']),
            pipeline_id=row['pipelineid']
        )
        db.session.add(stage)
    db.session.commit()

# Custom Field Groups
with open('data/custom_field_groups.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group = CustomFieldGroup(
            id=row['id'],
            name=row['name'],
            model=row['model'],
            pipeline_id=row['pipelineid'] if row['pipelineid'] else None
        )
        db.session.add(group)
    db.session.commit()

# Custom Fields
with open('data/custom_fields.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Parse options if present
        options = row['picklistOptions'].split(',') if row.get('picklistOptions') else []
        
        field = CustomField(
            name=row['name'],
            field_key=row['fieldKey'],
            data_type=row['dataType'],
            model=row['model'],
            placeholder=row.get('placeholder'),
            options=options,
            custom_field_group_id=row.get('parentId')
        )
        db.session.add(field)
    db.session.commit()
```

Run: `python seed.py`

---

## Pipeline Stage IDs (from pipeline_stages.csv)

**TripBooking Pipeline** (IlWdPtOpcczLpgsde2KF):
- FormSubmit: `027508e9-939c-4646-bb59-66970fe674fe` (position 0)
- TripFinalized: `8927d13e-bdd8-45db-a55a-96b9057d3676` (position 1)
- TravelersAdded: `635ba2fa-9270-40ac-8ff9-259a5487ce72` (position 2)
- TripScheduled: `19d3c6b2-cc55-40cb-973c-4ba603e6d19a` (position 3)
- TripComplete: `56c0708d-48ef-4cb5-873a-c7785b566448` (position 4)

**Passenger Pipeline** (fnsdpRtY9o83Vr4z15bE):
- AddedToTrip: `62c0b80d-6e56-4775-9d93-fbc96fda92e7` (position 0)
- DetailsSubmitted: `5019844d-b9bd-43ef-b027-e966f279bf96` (position 1)
- TripDetailsSent: `b55fba98-5ca4-4b5a-8c75-97c43ae1bab0` (position 2)
- TripReady: `d63f1360-81db-40ce-8a4c-ca00516f64d8` (position 3)
- TripInProgress: `4b4a6f25-853d-487d-8db1-48371d427573` (position 4)
- TripComplete: `dfca0535-a466-4ded-af60-6c0c3a677b8c` (position 5)

---

## Environment Variables (.env)

```
GHL_API_TOKEN=your_ghl_private_integration_token
GHL_LOCATION_ID=your_ghl_location_id
DATABASE_URL=sqlite:///tripbuilder.db
SECRET_KEY=your_flask_secret_key_for_sessions
```

---

## Testing Workflow

1. **Create a Trip**:
   - Navigate to `/trips/new`
   - Enter destination, dates
   - Submit → Trip created in DB, TripBooking opportunity created in GHL

2. **Add Passengers**:
   - On trip detail page, click "Add Passenger"
   - Select existing contact or create new
   - Submit → Passenger opportunity created in GHL, linked to trip

3. **Update Passenger Details**:
   - Click passenger name → Passenger detail page
   - Expand "Passport Info" section
   - Fill fields (passport number, expiry, etc.)
   - Save → Fields updated in GHL

4. **Progress Stages**:
   - Click "Move to DetailsSubmitted" button
   - Passenger opportunity stage updated in GHL

5. **Complete Trip**:
   - Progress all passengers to "TripComplete"
   - Progress TripBooking to "TripComplete"

---

## Success Criteria

✅ Trips can be created, updated, deleted  
✅ Each Trip automatically creates a TripBooking opportunity in GHL  
✅ Contacts can be fetched from GHL and displayed  
✅ Contacts can be added to Trips, creating Passenger opportunities  
✅ Custom fields display dynamically based on pipeline  
✅ Custom field values can be updated and synced to GHL  
✅ Opportunities can progress through stages  
✅ UI is responsive and intuitive  
✅ Error handling for API failures  
✅ Confirmation dialogs for destructive actions  

---

## Additional Context

Refer to these documents for comprehensive details:
- **PROJECT_DESCRIPTION.md**: Full application overview and data model
- **TECH_STACK.md**: Technology choices, API wrapper methods, database schema
- **FEATURES.md**: Detailed feature descriptions and user workflows
- **IMPLEMENTATION_STAGES.md**: Step-by-step build plan with deliverables

Files provided:
- `base.py.txt`: SQLAlchemy models
- `gohighlevel-complete-api.py.txt`: API wrapper implementation
- `pipelines.csv`, `pipeline_stages.csv`, `custom_fields.csv`, `custom_field_groups.csv`: Seed data

---

**This is a complex, multi-pipeline CRM integration application. The key is understanding the Trip → TripBooking Opportunity (1:1) and Trip ← Passenger → Contact (many-to-many via Passenger opportunities) relationships.**