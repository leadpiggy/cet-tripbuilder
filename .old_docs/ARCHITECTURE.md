# TripBuilder - Visual Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                    (Bootstrap 5 Templates)                      │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Dashboard  │  │   Trips     │  │  Contacts   │           │
│  │  /          │  │  /trips     │  │ /contacts   │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐                            │
│  │   Create    │  │   Enroll    │                            │
│  │   Trip      │  │  Passenger  │                            │
│  └─────────────┘  └─────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Application                          │
│                         (app.py)                                │
│                                                                 │
│  Routes:                                                        │
│  • GET  /                → Dashboard                           │
│  • GET  /trips           → List trips                          │
│  • POST /trips/new       → Create trip                         │
│  • GET  /trips/<id>      → Trip detail (TODO)                  │
│  • POST /trips/<id>/edit → Update trip                         │
│  • POST /trips/<id>/enroll → Enroll passenger                  │
│  • POST /admin/sync      → Trigger GHL sync                    │
│                                                                 │
│  CLI Commands:                                                  │
│  • flask init-db         → Initialize database                 │
│  • flask sync-ghl        → Sync from GoHighLevel               │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
    ┌───────────────────────┐   ┌───────────────────────┐
    │   SQLAlchemy Models   │   │   GHL Sync Service    │
    │     (models.py)       │   │ (services/ghl_sync.py)│
    │                       │   │                       │
    │  • Trip               │   │ • sync_pipelines()    │
    │  • Contact            │   │ • sync_stages()       │
    │  • Passenger          │   │ • sync_contacts()     │
    │  • Pipeline           │   │ • get_or_create_      │
    │  • PipelineStage      │   │   contact()           │
    │  • CustomField        │   │ • perform_full_sync() │
    │  • CustomFieldGroup   │   │                       │
    │  • SyncLog            │   │                       │
    └───────────────────────┘   └───────────────────────┘
                │                           │
                │                           │
                ▼                           ▼
    ┌───────────────────────┐   ┌───────────────────────┐
    │  Local Database       │   │   GHL API Wrapper     │
    │  (SQLite/PostgreSQL)  │   │    (ghl_api.py)       │
    │                       │   │                       │
    │  ┌─────────────────┐ │   │ • create_contact()    │
    │  │ trips           │ │   │ • search_contacts()   │
    │  │ contacts        │ │   │ • get_contact()       │
    │  │ passengers      │ │   │ • create_opportunity()│
    │  │ pipelines       │ │   │   (TODO)              │
    │  │ pipeline_stages │ │   │ • update_opportunity()│
    │  │ custom_fields   │ │   │   (TODO)              │
    │  │ sync_logs       │ │   │                       │
    │  └─────────────────┘ │   │                       │
    └───────────────────────┘   └───────────────────────┘
                                            │
                                            │
                                            ▼
                        ┌────────────────────────────────┐
                        │   GoHighLevel API v2           │
                        │   (services.leadconnectorhq.   │
                        │    com)                        │
                        │                                │
                        │  • Contacts                    │
                        │  • Opportunities               │
                        │    - TripBooking Pipeline      │
                        │    - Passenger Pipeline        │
                        │  • Custom Fields               │
                        │  • Pipelines & Stages          │
                        └────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Creating a Trip

```
User fills form → Flask route (POST /trips/new)
                         │
                         ▼
              Create Trip record in DB
                         │
                         ▼
              TODO: Create TripBooking opportunity in GHL
                         │
                         ▼
              Store opportunity ID in trip.ghl_opportunity_id
                         │
                         ▼
              Redirect to trip detail page
```

### 2. Enrolling a Passenger

```
User fills enrollment form → Flask route (POST /trips/<id>/enroll)
                                     │
                                     ▼
                          Check if contact exists locally
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                    Contact found      Contact not found
                          │                     │
                          │                     ▼
                          │          Search GHL by email
                          │                     │
                          │          ┌──────────┴──────────┐
                          │          ▼                     ▼
                          │     Found in GHL      Not in GHL
                          │          │                     │
                          │          │                     ▼
                          │          │          Create contact in GHL
                          │          │                     │
                          │          ▼                     │
                          │     Sync to local DB           │
                          │          │                     │
                          └──────────┴─────────────────────┘
                                     │
                                     ▼
                          TODO: Create Passenger opportunity
                                     │
                                     ▼
                          Create Passenger record in DB
                                     │
                                     ▼
                          Store opportunity ID
                                     │
                                     ▼
                          Link to Contact and Trip
                                     │
                                     ▼
                          Redirect to trip detail
```

### 3. GHL Sync Process

```
User triggers sync (CLI or admin button)
                    │
                    ▼
        Create SyncLog entry (status: in_progress)
                    │
                    ▼
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
Sync Pipelines         Sync Pipeline Stages
(2 records)            (11 records)
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
            Sync Contacts
         (paginated, 100 per page)
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
For each contact:        Save to local DB
- Parse GHL data         - Update if exists
- Map fields             - Create if new
                                │
                                ▼
                    Update SyncLog
            (status: success/partial/failed)
                                │
                                ▼
                    Return results summary
```

## File Structure Tree

```
tripbuilder/
│
├── Core Application
│   ├── app.py                      [Flask app, routes, CLI commands]
│   ├── models.py                   [SQLAlchemy models]
│   ├── ghl_api.py                  [GHL API wrapper]
│   └── requirements.txt            [Python dependencies]
│
├── Configuration
│   ├── .env.example                [Environment template]
│   └── .env                        [Your credentials - gitignored]
│
├── Services
│   └── services/
│       ├── __init__.py
│       └── ghl_sync.py             [Sync logic]
│
├── Templates (Jinja2)
│   └── templates/
│       ├── base.html               [Base layout with navbar]
│       ├── index.html              [Dashboard]
│       │
│       ├── trips/
│       │   ├── list.html           [Trip cards view]
│       │   ├── form.html           [Create/edit trip]
│       │   └── detail.html         [TODO - Trip detail]
│       │
│       ├── passengers/
│       │   ├── enroll.html         [Enrollment form]
│       │   └── detail.html         [TODO - Passenger detail]
│       │
│       ├── contacts/
│       │   ├── list.html           [TODO - Contacts list]
│       │   └── detail.html         [TODO - Contact detail]
│       │
│       └── admin/
│           └── sync_logs.html      [TODO - Sync history]
│
├── Static Assets
│   └── static/
│       ├── css/
│       │   └── custom.css          [Custom styles]
│       └── js/
│           └── app.js              [Client-side JS]
│
└── Documentation
    ├── README.md                   [Setup & usage guide]
    ├── TESTING.md                  [Testing checklist]
    └── STAGE_2A_COMPLETE.md        [Completion summary]
```

## Database Relationships Diagram

```
┌────────────────┐
│     trips      │
│ ────────────── │
│ id (PK)        │◄─────────┐
│ destination    │          │
│ start_date     │          │
│ end_date       │          │
│ ghl_opp_id     │          │
└────────────────┘          │
                            │
                            │ trip_id (FK)
                            │
                  ┌─────────────────┐
                  │   passengers    │
                  │ ─────────────── │
                  │ id (PK)         │
                  │ contact_id (FK) │─────┐
                  │ trip_id (FK)    │     │
                  │ stage_id (FK)   │     │
                  └─────────────────┘     │
                            │             │
                            │             │
                  stage_id  │             │ contact_id
                            │             │
                            ▼             ▼
              ┌──────────────────┐  ┌──────────────────┐
              │ pipeline_stages  │  │    contacts      │
              │ ──────────────── │  │ ──────────────── │
              │ id (PK)          │  │ id (PK)          │
              │ name             │  │ firstname        │
              │ position         │  │ lastname         │
              │ pipeline_id (FK) │  │ email            │
              └──────────────────┘  │ phone            │
                       │            │ tags             │
                       │            │ custom_fields    │
           pipeline_id │            └──────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    pipelines     │
              │ ──────────────── │
              │ id (PK)          │
              │ name             │
              └──────────────────┘
                       │
                       │ pipeline_id (FK)
                       │
                       ▼
       ┌──────────────────────────┐
       │ custom_field_groups      │
       │ ────────────────────────│
       │ id (PK)                  │
       │ name                     │
       │ model                    │
       │ pipeline_id (FK)         │
       └──────────────────────────┘
                       │
                       │ custom_field_group_id (FK)
                       │
                       ▼
       ┌──────────────────────────┐
       │    custom_fields         │
       │ ────────────────────────│
       │ id (PK)                  │
       │ ghl_field_id             │
       │ name                     │
       │ field_key                │
       │ data_type                │
       │ options                  │
       │ custom_field_group_id    │
       └──────────────────────────┘
```

## Pipeline Structure

```
GoHighLevel Pipelines
│
├─ TripBooking Pipeline (IlWdPtOpcczLpgsde2KF)
│  │
│  ├─ Stage 0: FormSubmit (027508e9-939c-4646-bb59-66970fe674fe)
│  │            ↓ Initial stage for new TripBooking opportunities
│  │
│  ├─ Stage 1: TripFinalized (8927d13e-bdd8-45db-a55a-96b9057d3676)
│  │            ↓ Trip details confirmed
│  │
│  ├─ Stage 2: TravelersAdded (635ba2fa-9270-40ac-8ff9-259a5487ce72)
│  │            ↓ Passengers enrolled
│  │
│  ├─ Stage 3: TripScheduled (19d3c6b2-cc55-40cb-973c-4ba603e6d19a)
│  │            ↓ Logistics finalized
│  │
│  └─ Stage 4: TripComplete (56c0708d-48ef-4cb5-873a-c7785b566448)
│               ↓ Trip concluded
│
└─ Passenger Pipeline (fnsdpRtY9o83Vr4z15bE)
   │
   ├─ Stage 0: AddedToTrip (62c0b80d-6e56-4775-9d93-fbc96fda92e7)
   │            ↓ Initial stage for new Passenger opportunities
   │
   ├─ Stage 1: DetailsSubmitted (5019844d-b9bd-43ef-b027-e966f279bf96)
   │            ↓ Personal/passport/health info collected
   │
   ├─ Stage 2: TripDetailsSent (b55fba98-5ca4-4b5a-8c75-97c43ae1bab0)
   │            ↓ Trip info sent to passenger
   │
   ├─ Stage 3: TripReady (d63f1360-81db-40ce-8a4c-ca00516f64d8)
   │            ↓ Fully prepared for travel
   │
   ├─ Stage 4: TripInProgress (4b4a6f25-853d-487d-8db1-48371d427573)
   │            ↓ Currently traveling
   │
   └─ Stage 5: TripComplete (dfca0535-a466-4ded-af60-6c0c3a677b8c)
                ↓ Trip finished
```

## Custom Field Groups Hierarchy

```
Passenger Pipeline Custom Fields
│
├─ Room Info (SgWPJJ0uHrmPR90kDv8R)
│  ├─ Roomate (TEXT)
│  └─ Preferred Occupancy (SINGLEOPTIONS)
│
├─ Passport Info (lKQQhGL4xhpd9Lpfnu1k)
│  ├─ Passport Number (TEXT)
│  ├─ Passport Expiration (DATE)
│  ├─ Passport Image (FILEUPLOAD)
│  └─ Passport Country (SINGLEOPTIONS)
│
├─ Health Details (QlF3XC2zKJk6yepcGeCw)
│  ├─ General State of Health (LARGETEXT)
│  ├─ Medical Limitations (LARGETEXT)
│  ├─ Primary Physician (TEXT)
│  ├─ Physician Phone (TEXT)
│  └─ Medications (LARGETEXT)
│
├─ Emergency Contact (d88EO8Sfm0E9h825Xhog)
│  ├─ First Name, Last Name (TEXT)
│  ├─ Relationship (TEXT)
│  ├─ Address, City, State, ZIP (TEXT)
│  └─ Phone, Email, Mobile (TEXT)
│
├─ Legal (phpeRQgIExMgunGsnIMK)
│  ├─ Form Submitted Date (DATE)
│  ├─ Travel Category License (SINGLEOPTIONS)
│  └─ Signature (SIGNATURE)
│
└─ Files (C6JkkidhL39BMTCsKFqh)
   ├─ Reservation (FILEUPLOAD - PDF)
   ├─ MOU (FILEUPLOAD - PDF)
   └─ Affidavit (FILEUPLOAD - PDF)

TripBooking Pipeline Custom Fields
│
├─ Opportunity Details (soiG10b9GQuVzF4B7aMK)
│  ├─ Trip ID, Trip Name (TEXT, SINGLEOPTIONS)
│  ├─ Passenger details
│  ├─ Dates, pricing
│  └─ Lodging info
│
├─ Vendor Info (AsK8LH2JAKUGckXSCABk)
│  ├─ Trip Vendor (SINGLEOPTIONS)
│  └─ Vendor Terms (LARGETEXT)
│
├─ Trip Details (iz2R5sVQnICgJApeIleV)
│  ├─ Arrival/Return Dates (DATE)
│  ├─ Max Passengers (NUMERICAL)
│  ├─ Travel Category (SINGLEOPTIONS)
│  └─ Pricing (MONETORY)
│
└─ Internal (mnGyltuJPG90Z4DZiJtd)
   └─ Internal trip notes
```

## User Journey Map

### Trip Organizer Journey
```
1. Create Account/Login (future)
   │
   ├─ View Dashboard
   │  └─ See stats: trips, contacts, passengers
   │
   ├─ Create Trip
   │  ├─ Fill form (destination, dates, capacity)
   │  ├─ Submit
   │  └─ → Trip created in DB
   │      → TODO: TripBooking opportunity created in GHL
   │
   ├─ View Trip Detail
   │  ├─ See trip info
   │  ├─ See enrolled passengers
   │  ├─ See current stage
   │  └─ Options:
   │      ├─ Edit trip
   │      ├─ Delete trip
   │      ├─ Enroll passenger
   │      └─ TODO: Progress to next stage
   │
   └─ Manage Passengers
      ├─ View all passengers
      ├─ TODO: View passenger details
      └─ TODO: Update custom fields
```

### Passenger Journey
```
1. Receive Trip Link
   │
   ├─ Click "Enroll in Trip"
   │  ├─ Fill personal info (name, email, phone)
   │  ├─ Fill address (optional)
   │  ├─ Submit
   │  └─ → Contact created/found in GHL
   │      → TODO: Passenger opportunity created
   │      → Stage: AddedToTrip
   │
   ├─ Receive Confirmation
   │  └─ Email with next steps (future)
   │
   ├─ TODO: Submit Additional Details
   │  ├─ Passport info
   │  ├─ Health details
   │  ├─ Emergency contact
   │  ├─ Legal forms
   │  └─ → Stage progresses to DetailsSubmitted
   │
   ├─ TODO: Receive Trip Details
   │  └─ Stage: TripDetailsSent
   │
   ├─ TODO: Confirm Ready
   │  └─ Stage: TripReady
   │
   ├─ TODO: During Trip
   │  └─ Stage: TripInProgress
   │
   └─ TODO: Post-Trip
      └─ Stage: TripComplete
```

## Stage 2A Completion Checklist

### ✅ Completed Features
- [x] Database models for all entities
- [x] Flask application structure
- [x] GHL API wrapper integration
- [x] Sync service with logging
- [x] CLI commands (init-db, sync-ghl)
- [x] Dashboard with statistics
- [x] Trip list view
- [x] Trip creation (public form)
- [x] Trip editing
- [x] Passenger enrollment (public form)
- [x] Smart contact handling (GHL check)
- [x] Contact sync from GHL
- [x] Pipeline and stage sync
- [x] Bootstrap 5 responsive UI
- [x] Flash messages for feedback
- [x] Error handling
- [x] Comprehensive documentation

### ⏳ Next Stage (2B)
- [ ] Add opportunity methods to API wrapper
- [ ] Implement Trip → TripBooking opportunity creation
- [ ] Implement Trip → TripBooking opportunity update
- [ ] Implement Trip → TripBooking opportunity deletion
- [ ] Add trip detail page
- [ ] Display opportunity stage on trip detail
- [ ] Add stage progression UI

### 🔮 Future Stages (2C-2D)
- [ ] Implement Passenger → Passenger opportunity creation
- [ ] Sync custom field definitions from GHL
- [ ] Dynamic custom field form generation
- [ ] Custom field value updates via GHL API
- [ ] Passenger detail page with all custom fields
- [ ] Contact detail page
- [ ] Admin sync logs page
- [ ] Batch operations
- [ ] Advanced reporting

---

**Stage 2A Status: ✅ COMPLETE**

Foundation established for bidirectional GHL sync.
Ready to proceed to Stage 2B: Trip-to-Opportunity integration.
