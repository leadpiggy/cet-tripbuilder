# TripBuilder Project-Specific Rules

**Last Updated:** October 27, 2025
**Status:** Production Active
**Build Location:** tripbuilder/

---

## 🎯 Core Project Rules

### Rule 1: Bidirectional Sync is Sacred
**All trip and passenger operations MUST sync with GoHighLevel**

**What this means:**
- Creating a trip → Auto-create TripBooking opportunity in GHL
- Updating a trip → Auto-sync changes to GHL custom fields
- Enrolling a passenger → Auto-create Passenger opportunity in GHL
- Updating passenger → Auto-sync to GHL custom fields

**Implementation:**
```python
# ALWAYS use TwoWaySyncService for create/update operations
from services.two_way_sync import TwoWaySyncService

sync_service = TwoWaySyncService(ghl_api)
sync_service.auto_sync_on_trip_create(trip)  # After trip creation
sync_service.auto_sync_on_passenger_create(passenger)  # After enrollment
```

**Error Handling:**
- If GHL sync fails, still save data locally (graceful degradation)
- Flash warning message to user
- Log error for debugging

---

### Rule 2: Field Mapping is Centralized
**NEVER hardcode GHL field keys in routes or templates**

**What this means:**
- All field mappings live in `field_mapping.py`
- Use mapping utilities for reading/writing custom fields
- Update mapping file when new fields are added

**Forbidden:**
```python
# ❌ WRONG - Hardcoded field key
trip.destination = custom_fields['opportunity.tripname']
```

**Correct:**
```python
# ✅ RIGHT - Use mapping utilities
from field_mapping import map_trip_custom_fields, parse_ghl_custom_fields

custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
mapped = map_trip_custom_fields(custom_fields_dict)
trip.destination = mapped.get('destination')
```

---

### Rule 3: Smart Contact Handling
**Always check local DB → GHL search → GHL create (in that order)**

**Implementation Pattern:**
```python
# Step 1: Check local database
contact = Contact.query.filter_by(email=email).first()

if not contact:
    # Step 2: Search GHL
    ghl_contacts = ghl_api.search_contacts(email, location_id)
    
    if ghl_contacts:
        # Found in GHL, sync to local
        contact = create_contact_from_ghl(ghl_contacts[0])
    else:
        # Step 3: Create in GHL, then local
        ghl_contact = ghl_api.create_contact(data, location_id)
        contact = create_contact_from_ghl(ghl_contact)

db.session.commit()
```

**Why:** Prevents duplicate contacts and ensures data consistency

---

### Rule 4: Passenger-Trip Linking via trip_name
**Use trip_name custom field as the linking mechanism**

**What this means:**
- Passengers link to trips through `trip_name` field (not trip_id directly)
- GHL Passenger opportunities store trip_name in custom field
- Multi-tier matching: exact → case-insensitive → partial

**Implementation:**
```python
# Set trip_name when creating passenger
passenger = Passenger(
    contact_id=contact.id,
    trip_name=trip.name  # This is the linking field
)

# Later, match passengers to trips
trips_by_name = {trip.name.lower(): trip for trip in Trip.query.all()}
if passenger.trip_name:
    trip = trips_by_name.get(passenger.trip_name.lower())
    if trip:
        passenger.trip_id = trip.id
```

**Why:** GHL opportunities can't have foreign keys to other opportunities

---

### Rule 5: Database Schema Must Match models.py
**Always verify schema before making changes**

**Verification Process:**
```bash
# Check actual database schema
psql -U ridiculaptop -d tripbuilder
\d trips
\d passengers
\d contacts

# Compare with models.py
```

**If schema doesn't match:**
1. Create migration script (e.g., `migrate_add_columns.py`)
2. Test migration on development database
3. Run migration
4. Verify schema again
5. Update models.py if needed

**Never:**
- Assume models.py matches database
- Edit database manually without migration script
- Change models.py without migrating database

---

## 🔐 Security & Credentials Rules

### GHL API Credentials
**Location:** `tripbuilder/.env` (gitignored)

**Required Variables:**
```bash
GHL_API_TOKEN=your_private_integration_token
GHL_LOCATION_ID=your_location_id
```

**Rules:**
- Never commit `.env` file
- Never hardcode tokens in code
- Use `os.getenv()` to access credentials
- Check credentials exist before API calls

---

### AWS S3 Credentials (When Implemented)
**Location:** `tripbuilder/.env`

**Required Variables:**
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=tripbuilder-files
AWS_REGION=us-east-1
```

**Rules:**
- Use IAM user with minimum required permissions
- Never expose S3 URLs directly (use pre-signed URLs)
- Set appropriate expiration times (default 1 hour)

---

## 📁 File Organization Rules

### Application Code Location
**All application code MUST be in `tripbuilder/` subdirectory**

```
tripbuilder/
├── app.py              # Flask routes and CLI commands
├── models.py           # Database models
├── ghl_api.py          # GHL API wrapper
├── field_mapping.py    # Field mappings
├── services/           # Business logic
│   ├── ghl_sync.py
│   ├── two_way_sync.py
│   └── file_manager.py (planned)
├── templates/          # Jinja2 templates
└── static/             # CSS, JavaScript
```

### Documentation Location
**Use memory-bank/ for active documentation**

```
memory-bank/
├── projectBrief.md     # Requirements and scope
├── progress.md         # What's done, what's next
├── activeContext.md    # Current work focus
├── techContext.md      # Technology details
└── systemPatterns.md   # Best practices
```

**Old Documentation:**
- Root-level `.md` files (PROJECT_DESCRIPTION.md, etc.) are OUTDATED
- Do not update them
- Use memory-bank/ as source of truth

---

## 🗄️ Database Rules

### PostgreSQL Connection
**Database:** `tripbuilder`
**User:** `ridiculaptop`
**Host:** `localhost`
**Port:** `5432`

**Connection String:**
```
postgresql://ridiculaptop@localhost:5432/tripbuilder
```

### Table Relationships
**Understand these before making schema changes:**

```
trips (1) ←→ (many) passengers
passengers (many) ←→ (1) contacts
passengers (many) ←→ (1) pipeline_stages
passengers (many) ←→ (1) trips (via trip_name fallback)
```

### Required Columns
**Never remove these columns without migration:**

**trips:**
- `id` (PK)
- `name` (unique trip identifier)
- `ghl_opportunity_id` (link to GHL TripBooking)

**passengers:**
- `id` (PK, also GHL Passenger opportunity ID)
- `contact_id` (FK to contacts)
- `trip_id` (FK to trips, nullable)
- `trip_name` (linking field)

**contacts:**
- `id` (PK, also GHL contact ID)
- `email` (unique)

---

## 🔄 GHL Sync Rules

### Pipeline IDs (DO NOT CHANGE)
```python
TRIPBOOKING_PIPELINE_ID = "IlWdPtOpcczLpgsde2KF"
PASSENGER_PIPELINE_ID = "fnsdpRtY9o83Vr4z15bE"
```

### Stage IDs (REFERENCE ONLY)
**TripBooking Stages:**
- FormSubmit: `027508e9-939c-4646-bb59-66970fe674fe`
- TripFinalized: `8927d13e-bdd8-45db-a55a-96b9057d3676`
- TravelersAdded: `635ba2fa-9270-40ac-8ff9-259a5487ce72`
- TripScheduled: `19d3c6b2-cc55-40cb-973c-4ba603e6d19a`
- TripComplete: `56c0708d-48ef-4cb5-873a-c7785b566448`

**Passenger Stages:**
- AddedToTrip: `62c0b80d-6e56-4775-9d93-fbc96fda92e7`
- DetailsSubmitted: `5019844d-b9bd-43ef-b027-e966f279bf96`
- TripDetailsSent: `b55fba98-5ca4-4b5a-8c75-97c43ae1bab0`
- TripReady: `d63f1360-81db-40ce-8a4c-ca00516f64d8`
- TripInProgress: `4b4a6f25-853d-487d-8db1-48371d427573`
- TripComplete: `dfca0535-a466-4ded-af60-6c0c3a677b8c`

### Custom Field Format
**Always use lowercase with prefix:**
```
opportunity.fieldname
```

**Examples:**
- `opportunity.tripname`
- `opportunity.passportnumber`
- `opportunity.healthstate`

---

## 📝 Error Handling Rules

### Flask Route Error Pattern
```python
@app.route('/example')
def example():
    try:
        # Database operations
        record = Model.query.get_or_404(id)
        record.field = new_value
        
        try:
            # GHL sync (inner try/catch)
            sync_service.auto_sync(record)
            db.session.commit()
            flash('Success!', 'success')
        except Exception as sync_error:
            # Graceful degradation
            db.session.commit()  # Still save locally
            flash(f'Saved locally, sync failed: {sync_error}', 'warning')
            print(f"Sync error: {sync_error}")
    
    except Exception as e:
        # Database errors
        db.session.rollback()
        flash(f'Error: {e}', 'danger')
        print(f"Error: {e}")
    
    return redirect(url_for('index'))
```

**Rules:**
1. Outer try/catch for database errors
2. Inner try/catch for GHL sync errors
3. Always commit local changes (graceful degradation)
4. Flash appropriate messages
5. Log to console for debugging
6. Rollback only on database errors

---

## 🧪 Testing Rules

### Before Committing Code
1. Run local tests
2. Check database for data integrity
3. Verify GHL sync works
4. Test error cases
5. Check console for errors

### Test Data
- Use test trips with "TEST" prefix
- Create test passengers with test email addresses
- Clean up test data after testing
- Never test with production contact data

---

## 📊 Data Volume Expectations

**Current Production Scale:**
- Trips: ~693
- Passengers: ~6,477
- Contacts: ~5,453
- Custom Fields: 53
- Pipelines: 2
- Stages: 11

**Performance Considerations:**
- Pagination for large datasets (100 records/page)
- Rate limiting for GHL API (100ms delay between requests)
- Database indexing on frequently queried fields

---

## 🚀 Deployment Rules

### Environment Configuration
**Development:** 
- Database: Local PostgreSQL
- Server: Flask development server (port 5269)
- Debug: Enabled

**Production:**
- Database: Hosted PostgreSQL
- Server: Gunicorn + Nginx
- Debug: Disabled
- HTTPS: Required
- Environment variables: From secure storage

---

## ✅ Code Review Checklist

Before submitting changes:
- [ ] No hardcoded credentials
- [ ] No hardcoded field keys
- [ ] Error handling in place
- [ ] GHL sync working
- [ ] Database migrations created (if schema changed)
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Console logs removed (except debug)
- [ ] Code follows project patterns
- [ ] No duplicate code

---

**These are the non-negotiable rules for TripBuilder development.**

Last Updated: October 27, 2025