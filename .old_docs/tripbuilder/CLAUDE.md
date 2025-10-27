# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TripBuilder is a Flask-based travel operations management system with bidirectional GoHighLevel (GHL) CRM integration. It manages trips, passengers, and contacts through two separate GHL opportunity pipelines:
- **TripBooking Pipeline** (`IlWdPtOpcczLpgsde2KF`): Trip-level workflow (1 opportunity per trip)
- **Passenger Pipeline** (`fnsdpRtY9o83Vr4z15bE`): Individual passenger workflow (1 opportunity per contact-trip pairing)

## Development Commands

### Database Operations
```bash
# Initialize database (create tables)
flask init-db

# Sync all data from GoHighLevel
flask sync-ghl

# Database migrations (if using Flask-Migrate)
flask db migrate -m "Description"
flask db upgrade
```

### Running the Application
```bash
# Development server (runs on http://localhost:5269)
python app.py

# Or using Flask CLI
flask run --host=0.0.0.0 --port=5269
```

### Testing
```bash
# Run specific debug/test scripts
python debug_sync.py          # Test GHL sync operations
python test_opp_api.py        # Test opportunity API calls
python check_trip_fields.py   # Verify trip field mapping
python verify_data.py         # Verify database contents
```

## Architecture

### Data Flow: Local DB ↔ GoHighLevel CRM

**Trip Creation Flow:**
1. Trip created in local database (models.py: Trip table)
2. TripBooking opportunity created in GHL via `ghl_api.py`
3. Opportunity ID stored in `trip.ghl_opportunity_id`

**Passenger Enrollment Flow:**
1. Contact lookup/creation via `services/ghl_sync.py::get_or_create_contact()`
   - Checks local DB first
   - Searches GHL by email
   - Creates in GHL if not found
2. Passenger opportunity created in GHL Passenger pipeline
3. Passenger record created locally with opportunity ID

**Sync Flow:**
- `services/ghl_sync.py::perform_full_sync()` coordinates all sync operations
- Syncs: Pipelines → Stages → Custom Fields → Contacts → Trips → Passengers
- All sync operations logged to `sync_logs` table

### Key File Relationships

```
app.py (Flask routes & CLI commands)
  ├─→ models.py (SQLAlchemy models: Trip, Contact, Passenger, etc.)
  ├─→ ghl_api.py (GHL API wrapper)
  └─→ services/ghl_sync.py (bidirectional sync logic)
        └─→ field_mapping.py (custom field translation utilities)
```

### Database Models

**Trip** - Backend trip records
- Maps 1:1 to TripBooking opportunities in GHL
- All GHL custom fields mapped to specific columns (see `TRIP_FIELD_MAP` in field_mapping.py)
- Key columns: `destination`, `start_date`, `end_date`, `ghl_opportunity_id`

**Contact** - Cached GHL contacts
- Primary key is GHL contact ID (String)
- Fields: `firstname`, `lastname`, `email`, `phone`, address fields, `tags`

**Passenger** - Junction table (Contact × Trip)
- Primary key is GHL Passenger opportunity ID
- Maps 1:1 to Passenger opportunities in GHL
- All GHL custom fields mapped to specific columns (see `PASSENGER_FIELD_MAP` in field_mapping.py)
- Foreign keys: `contact_id`, `trip_id`, `stage_id`

**Pipeline & PipelineStage** - Pipeline workflow definitions
- 2 pipelines, 11 stages total (see PIPELINE_CUSTOM_FIELD_DATA.md)

**CustomField & CustomFieldGroup** - GHL field metadata
- Defines field types, options, validation rules
- Used to dynamically generate forms (future feature)

**SyncLog** - Audit trail for sync operations
- Tracks success/failure, records synced, errors

## GHL API Integration

### API Wrapper (`ghl_api.py`)

The `GoHighLevelAPI` class provides methods organized by resource:

**Contacts:**
```python
ghl_api.create_contact(firstname=..., lastname=..., email=...)
ghl_api.get_contact(contact_id)
ghl_api.search_contacts(query="email@example.com", limit=100)
ghl_api.update_contact(contact_id, **kwargs)
ghl_api.delete_contact(contact_id)
```

**Opportunities:**
```python
ghl_api.create_opportunity(data={
    'name': 'Trip Name',
    'pipelineId': 'IlWdPtOpcczLpgsde2KF',
    'stageId': '027508e9-939c-4646-bb59-66970fe674fe',
    'contactId': contact_id,
    'locationId': location_id
})
ghl_api.get_opportunity(opportunity_id)
ghl_api.search_opportunities(pipeline_id=..., stage_id=..., limit=100, page=1)
ghl_api.update_opportunity(opportunity_id, data={...})
ghl_api.update_opportunity_stage(opportunity_id, stage_id)
ghl_api.upsert_opportunity_custom_field(opportunity_id, 'opportunity.fieldkey', value)
```

**Pipelines & Custom Fields:**
```python
ghl_api.get_pipelines()  # Returns pipelines with stages
ghl_api.get_custom_fields(model='opportunity')
```

### Pipeline & Stage IDs

**TripBooking Pipeline** (`IlWdPtOpcczLpgsde2KF`):
- FormSubmit: `027508e9-939c-4646-bb59-66970fe674fe` (position 0)
- TripFinalized: `8927d13e-bdd8-45db-a55a-96b9057d3676` (position 1)
- TravelersAdded: `635ba2fa-9270-40ac-8ff9-259a5487ce72` (position 2)
- TripScheduled: `19d3c6b2-cc55-40cb-973c-4ba603e6d19a` (position 3)
- TripComplete: `56c0708d-48ef-4cb5-873a-c7785b566448` (position 4)

**Passenger Pipeline** (`fnsdpRtY9o83Vr4z15bE`):
- AddedToTrip: `62c0b80d-6e56-4775-9d93-fbc96fda92e7` (position 0)
- DetailsSubmitted: `5019844d-b9bd-43ef-b027-e966f279bf96` (position 1)
- TripDetailsSent: `b55fba98-5ca4-4b5a-8c75-97c43ae1bab0` (position 2)
- TripReady: `d63f1360-81db-40ce-8a4c-ca00516f64d8` (position 3)
- TripInProgress: `4b4a6f25-853d-487d-8db1-48371d427573` (position 4)
- TripComplete: `dfca0535-a466-4ded-af60-6c0c3a677b8c` (position 5)

## Custom Field Mapping

GHL custom fields use format: `[{"id": "field_id", "fieldValue": "value"}, ...]`

Use utility functions in `field_mapping.py`:

```python
from field_mapping import parse_ghl_custom_fields, map_trip_custom_fields, map_passenger_custom_fields

# Convert GHL list format to dict
custom_fields_dict = parse_ghl_custom_fields(opportunity['customFields'])

# Map to database columns
trip_fields = map_trip_custom_fields(custom_fields_dict)
passenger_fields = map_passenger_custom_fields(custom_fields_dict)
```

**Important field mappings:**
- Trip ID: `opportunity.tripid` → `trip.trip_id_custom`
- Trip Name: `opportunity.tripname` → `trip.trip_name` or `trip.destination`
- Passport fields: `opportunity.passportnumber`, `opportunity.passportexpire`, etc.
- Emergency contact: `opportunity.contact1ufirstname`, `opportunity.contact1ulastname`, etc.

Full mappings in `TRIP_FIELD_MAP` and `PASSENGER_FIELD_MAP` in field_mapping.py

## Common Tasks

### Adding a New Route
1. Define route function in `app.py`
2. Use appropriate decorators: `@app.route('/path', methods=['GET', 'POST'])`
3. Create corresponding Jinja2 template in `templates/`
4. Use `flash()` for user feedback messages
5. Handle errors with try/except and `db.session.rollback()`

### Syncing GHL Data
```python
from services.ghl_sync import GHLSyncService

sync_service = GHLSyncService(ghl_api)
results = sync_service.perform_full_sync()  # Full sync
# Or individual syncs:
sync_service.sync_contacts()
sync_service.sync_trip_opportunities()
sync_service.sync_passenger_opportunities()
```

### Creating Opportunities in GHL
Always include required fields:
- `name`: Opportunity title
- `pipelineId`: Pipeline UUID
- `stageId`: Initial stage UUID
- `contactId`: Associated contact ID
- `locationId`: GHL location ID

Custom fields go in `customFields` dict with field keys like `opportunity.fieldname`.

### Working with Passengers
Passengers must have:
1. A valid `contact_id` (Contact must exist in local DB)
2. A `trip_id` (if linking to a specific trip)
3. A `stage_id` from the Passenger pipeline

When creating passenger opportunities, the GHL opportunity ID becomes the passenger's primary key.

## Important Conventions

### Date Handling
- Database dates are Python `date` objects
- GHL API expects ISO format strings: `YYYY-MM-DD`
- Convert with `.isoformat()` for API, `datetime.strptime()` for parsing

### Error Handling
- Always wrap database operations in try/except
- Call `db.session.rollback()` on errors
- Use `flash(message, category)` for user notifications
- Categories: 'success', 'error', 'warning', 'info'

### Database Sessions
- Changes require `db.session.commit()`
- Use `db.session.flush()` to get auto-generated IDs before commit
- Always rollback on exceptions to prevent partial commits

### GHL API Rate Limiting
The API wrapper (`ghl_api.py`) includes automatic rate limiting (100ms between requests). No additional throttling needed in application code.

## Environment Variables

Required in `.env`:
```
GHL_API_TOKEN=your_private_integration_token
GHL_LOCATION_ID=your_location_id
DATABASE_URL=sqlite:///tripbuilder.db  # or PostgreSQL URL
SECRET_KEY=your_flask_secret_key
DEBUG=True  # for development only
```

## Documentation Files

- **PROJECT_DESCRIPTION.md** - Detailed feature descriptions and use cases
- **ARCHITECTURE.md** - Visual diagrams of data flow and relationships
- **TECH_STACK.md** - Technology choices and dependencies
- **PIPELINE_CUSTOM_FIELD_DATA.md** - Complete reference for all GHL fields
- **README.md** - Setup instructions and project status
- **IMPLEMENTATION_STAGES.md** - Development roadmap

## Current Stage

**Stage 2A Complete** - GHL sync and basic CRUD operations implemented
- ✅ Database models with full custom field mapping
- ✅ GHL API wrapper
- ✅ Bidirectional sync service
- ✅ Trip creation (local DB only, GHL sync TODO)
- ✅ Passenger enrollment (local DB only, GHL sync TODO)
- ✅ Contact smart lookup/creation

**Next Steps:**
- Implement Trip → TripBooking opportunity creation in app.py:trip_new()
- Implement Passenger → Passenger opportunity creation in app.py:enroll_passenger()
- Add trip detail page with passenger list
- Add opportunity stage progression controls

## Debugging Tips

1. **Sync issues**: Check `sync_logs` table for error details
2. **Missing contacts**: Run `flask sync-ghl` to pull from GHL
3. **Field mapping errors**: Verify field keys in PIPELINE_CUSTOM_FIELD_DATA.md
4. **API errors**: GHL returns detailed error messages in response JSON
5. **Database issues**: Reset with `flask init-db` (WARNING: deletes data)
