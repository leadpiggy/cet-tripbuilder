# TripBuilder

A Flask-based travel operations management system with bidirectional GoHighLevel CRM integration.

## ✅ Stage 1 Complete!

All foundation files have been created. The project structure is ready for Stage 2A implementation.

---

## Project Status

### Stage 1: Project Setup & Foundation ✅ COMPLETE
- [x] Create project directory structure
- [x] Create requirements.txt
- [x] Create .env.example
- [x] Create models.py (all database models)
- [x] Create ghl_api.py (GHL API wrapper)
- [x] Create app.py (Flask application with routes and CLI commands)
- [x] Create templates/base.html (Bootstrap 5 layout)
- [x] Create all template files (trips, passengers, contacts)
- [x] Create static files (CSS, JS)
- [x] Create services package structure
- [x] Database can initialize with `flask init-db`

### Stage 2A: GHL Data Sync & Seeding ⏳ NEXT
**Goal**: Sync all existing GHL data to local database

To be implemented:
- [ ] Complete services/ghl_sync.py implementation
- [ ] Implement sync_pipelines()
- [ ] Implement sync_custom_fields()
- [ ] Implement sync_contacts()
- [ ] Test `flask sync-ghl` command

---

## Quick Start

### 1. Install Dependencies

```bash
cd tripbuilder
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Get these from GoHighLevel Settings > Private Integrations
GHL_API_TOKEN=your_private_integration_token_here
GHL_LOCATION_ID=your_location_id_here

# Database
DATABASE_URL=sqlite:///tripbuilder.db

# Flask
SECRET_KEY=your_random_secret_key_here
```

### 3. Initialize Database

```bash
flask init-db
```

Expected output:
```
✅ Database tables created successfully!
```

### 4. Run Application

```bash
python app.py
```

Visit: http://localhost:5000

You should see:
- Dashboard with stats (all zeros since no data yet)
- Navigation to Trips, Contacts
- Ability to create trips (local DB only - GHL sync in Stage 2B)

---

## Project Structure

```
tripbuilder/
├── app.py                      # Flask application ✅
├── models.py                   # SQLAlchemy models ✅
├── ghl_api.py                  # GHL API wrapper ✅
├── requirements.txt            # Dependencies ✅
├── .env.example                # Environment template ✅
├── .gitignore                  # Git ignore rules ✅
├── README.md                   # This file ✅
├── services/
│   ├── __init__.py            # Package init ✅
│   └── ghl_sync.py            # Sync service (placeholder) ⏳
├── templates/
│   ├── base.html              # Base layout ✅
│   ├── index.html             # Dashboard ✅
│   ├── trips/
│   │   ├── list.html          # Trips list ✅
│   │   ├── detail.html        # Trip detail ✅
│   │   └── form.html          # Create/edit trip ✅
│   ├── passengers/
│   │   ├── enroll.html        # Passenger enrollment ✅
│   │   └── detail.html        # Passenger detail ✅
│   └── contacts/
│       ├── list.html          # Contacts list ✅
│       └── detail.html        # Contact detail ✅
└── static/
    ├── css/
    │   └── custom.css         # Custom styles ✅
    └── js/
        └── app.js             # Custom JS ✅
```

---

## What Works Right Now

### ✅ Working Features (Local DB Only)
1. **Dashboard**: View stats and recent trips
2. **Trip Creation**: Create trips via public form
3. **Trip List**: View all trips with details
4. **Trip Detail**: View trip info and passengers
5. **Trip Editing**: Update trip details
6. **Trip Deletion**: Remove trips (with confirmation)
7. **Passenger Enrollment**: Enroll passengers (creates contacts in GHL!)
8. **Contact List**: View all synced contacts
9. **Contact Detail**: View contact info and their trips
10. **Responsive UI**: Bootstrap 5 with mobile support

### ⏳ Not Yet Implemented
1. **GHL Pipeline Sync**: Sync pipeline and stage definitions
2. **GHL Custom Field Sync**: Sync field definitions
3. **GHL Contact Sync**: Pull all contacts from GHL
4. **Trip → TripBooking Opportunity**: Auto-create opportunities when creating trips
5. **Passenger → Passenger Opportunity**: Auto-create opportunities when enrolling
6. **Custom Field Forms**: Dynamic forms based on GHL field definitions
7. **Stage Progression**: Move opportunities through workflow stages

These will be implemented in Stages 2A-2D.

---

## Database Models

All models are defined and ready to use:

- **Trip**: Destination, dates, capacity, notes
- **Contact**: Synced from GHL (firstname, lastname, email, phone, address)
- **Passenger**: Junction table (Contact ↔ Trip)
- **Pipeline**: TripBooking and Passenger pipelines
- **PipelineStage**: 11 stages across both pipelines
- **CustomFieldGroup**: Field organization (13 groups)
- **CustomField**: Field definitions (100+ fields)
- **SyncLog**: Track sync operations

---

## CLI Commands

### Available Now

```bash
# Initialize database (create all tables)
flask init-db
```

### Coming in Stage 2A

```bash
# Sync all data from GoHighLevel
flask sync-ghl
```

---

## GHL Integration Status

### ✅ Working
- **API Wrapper**: Complete with all essential endpoints
- **Contact Creation**: `get_or_create_contact()` in sync service
- **Smart Contact Handling**: Checks GHL before creating

### ⏳ To Implement (Stage 2A)
- Pipeline sync
- Custom field sync
- Bulk contact sync

### ⏳ To Implement (Stage 2B-2C)
- Trip → TripBooking opportunity creation
- Passenger → Passenger opportunity creation
- Opportunity updates and deletions

---

## Next Steps

### For Stage 2A Implementation:

1. **Implement `sync_pipelines()` in services/ghl_sync.py**
   - Fetch pipelines from GHL API
   - Upsert Pipeline and PipelineStage records

2. **Implement `sync_custom_fields()` in services/ghl_sync.py**
   - Fetch custom fields from GHL API
   - Upsert CustomFieldGroup and CustomField records

3. **Implement `sync_contacts()` in services/ghl_sync.py**
   - Fetch all contacts from GHL with pagination
   - Upsert Contact records

4. **Implement `perform_full_sync()` in services/ghl_sync.py**
   - Orchestrate all sync operations
   - Create SyncLog entries
   - Handle errors gracefully

5. **Test `flask sync-ghl` command**
   - Verify all data syncs correctly
   - Check sync logs

---

## Testing Checklist for Stage 1

- [x] Project structure created
- [x] All files present and syntactically valid
- [x] Virtual environment can be created
- [x] Requirements can be installed
- [x] Database can be initialized
- [x] Application starts without errors
- [x] Dashboard loads
- [x] Can navigate between pages
- [x] Can create a trip (local DB)
- [x] Can view trip list
- [x] Can view trip detail
- [x] Can enroll passenger (creates contact in GHL)
- [x] Flash messages work
- [x] Forms validate
- [x] Responsive design works

---

## Documentation

See project documentation files:
- `PROJECT_DESCRIPTION.md` - Full application overview
- `TECH_STACK.md` - Technology details
- `FEATURES.md` - Feature descriptions
- `IMPLEMENTATION_PLAN_V2.md` - Complete build plan (**CURRENT**)
- `ARCHITECTURE.md` - System architecture
- `PIPELINE_CUSTOM_FIELD_DATA.md` - GHL data reference

---

## Support

For issues or questions:
1. Check the implementation plan in `IMPLEMENTATION_PLAN_V2.md`
2. Review the architecture in `ARCHITECTURE.md`
3. Check GHL API reference in `PIPELINE_CUSTOM_FIELD_DATA.md`

---

## License

Proprietary - All rights reserved

---

**Stage 1 Status: ✅ COMPLETE**

Foundation is solid! Ready to proceed to Stage 2A: GHL Data Sync & Seeding.
