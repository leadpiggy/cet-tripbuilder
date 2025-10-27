# Project Brief: TripBuilder

**Mission:** Build a comprehensive Flask-based travel operations management system with bidirectional GoHighLevel CRM integration for managing trips, passengers, and contacts.

**Build Location:** `tripbuilder/` subdirectory

**Last Updated:** October 27, 2025

---

## Core Requirements

### 1. Trip Management System
- CRUD operations for trips with comprehensive details
- Trip fields: name, destination, dates, capacity, vendor info, pricing
- Link trips to GHL TripBooking pipeline opportunities
- Display trip status and passenger counts
- Support for trip-level custom fields
- **Search & Filter:** Filter trips by destination, date ranges, status, vendor
- **Date Range Views:** Show trips in progress during specific time periods

### 2. Passenger Enrollment & Tracking
- Enroll contacts as passengers on trips
- Create Passenger pipeline opportunities in GHL
- Track passenger progress through 6 stages (AddedToTrip → TripComplete)
- Capture extensive passenger details:
  - Passport information
  - Health details and medications
  - Emergency contacts
  - Room preferences
  - Legal forms and signatures
- Link passengers to trips via trip_name field (85% automated success rate)

### 3. S3 File Management System
- **Passport Photo Uploads:** Capture and store passport images in S3
- **Auto-Generated PDFs:** System-generated documents (confirmations, itineraries, legal forms)
- **Signature Capture:** Digital signature collection and secure storage
- **File Organization:** Hierarchical structure (trip → passenger → file type)
- **Opportunity Linking:** All files linked to specific opportunities (trips/passengers)
- **File Display:** Show all related files in trip/passenger detail views
- **Search & Navigate:** Browse and search through file management system
- **Directory Structure:**
  ```
  s3://bucket-name/
  ├── trips/
  │   └── {trip-name}/
  │       └── passengers/
  │           └── {passenger-name}/
  │               ├── passports/
  │               ├── signatures/
  │               └── documents/
  ```

### 4. Search & Filter System
- **Trip Search:** Filter by destination, date range, vendor, status, capacity
- **Passenger Search:** Filter by name, passport status, health details, trip
- **Date Range Queries:** Find trips in progress during specific periods
- **Advanced Filters:** Combine multiple criteria (e.g., "Hawaii trips in June with >10 passengers")
- **Quick Filters:** Pre-defined filters (upcoming trips, incomplete details, etc.)

### 5. Bidirectional GHL Synchronization
- **GHL → Local**: Bulk sync of pipelines, stages, custom fields, contacts, opportunities
- **Local → GHL**: Auto-sync on create/update operations
- Field mapping system for 30+ trip fields and 25+ passenger fields
- Pagination support for large datasets (6,477 passengers, 5,453 contacts)
- Comprehensive error handling and sync logging

### 6. Contact Management
- Sync all contacts from GoHighLevel
- Smart contact handling (check local → search GHL → create if needed)
- Display contact details and associated trips
- Track contact custom fields

### 7. Custom Field Integration
- 53 opportunity custom fields across 5 field groups
- Dynamic field mapping between database columns and GHL fields
- Type conversion (dates, integers, decimals, booleans, text)
- Support for dropdown/single options fields

---

## Project Structure

```
tripbuilder/
├── README.md
├── app.py                          # Flask application & routes
├── models.py                       # SQLAlchemy database models
├── ghl_api.py                      # GoHighLevel API wrapper
├── field_mapping.py                # Database ↔ GHL field mappings
├── requirements.txt
├── .env                            # Environment configuration
├── services/
│   ├── ghl_sync.py                # Bulk GHL → Local sync
│   └── two_way_sync.py            # Bidirectional sync service
├── templates/                      # Jinja2 HTML templates
├── static/                         # CSS, JavaScript
├── database_exports/               # Database snapshots
├── raw_ghl_responses/             # GHL API response cache
└── sync_captures/                 # Sync operation logs
```

---

## Success Criteria

- ✅ Create and manage trips with full custom field support
- ✅ Enroll passengers and track through workflow stages
- ✅ Automatic bidirectional sync with GoHighLevel
- ✅ 85%+ automated passenger-trip linking success rate
- ✅ Support 5,000+ contacts and 6,000+ passengers
- ✅ Handle 690+ trips with complete field mapping
- ✅ Real-time sync on create/update operations
- ✅ Comprehensive error handling and logging
- ✅ Clean, responsive Bootstrap 5 UI
- ✅ Search and filter trips by destination, dates, vendor
- 🔄 S3 file storage for passports, PDFs, and signatures
- 🔄 File organization by trip → passenger hierarchy
- 🔄 Digital signature capture and storage
- 🔄 Auto-generated PDF documents
- 🔄 File search and navigation interface

---

## Out of Scope (NOT building these)

- ❌ Mobile application (web-only interface)
- ❌ Email service (using GHL's built-in email)
- ❌ Payment processing (handled externally)
- ❌ Calendar integration (future enhancement)
- ❌ Document generation (using GHL files)
- ❌ SMS/messaging (using GHL)
- ❌ Multi-tenant support (single location only)

---

## Technology Stack

### Backend
- **Python:** 3.x with type hints
- **Flask:** Web framework with Jinja2 templating
- **SQLAlchemy:** ORM for database operations
- **PostgreSQL:** Primary database (production)
- **Why:** Mature ecosystem, excellent ORM, scalable database

### File Storage
- **AWS S3:** Cloud object storage for files
- **Boto3:** Python AWS SDK for S3 operations
- **File Types:** Passport photos (JPEG/PNG), PDFs, digital signatures (PNG)
- **Organization:** Hierarchical by trip/passenger
- **Why:** Scalable, secure, cost-effective, industry standard

### GHL Integration
- **GoHighLevel API v2:** REST API with Bearer token auth
- **Pipelines:** TripBooking (IlWdPtOpcczLpgsde2KF), Passenger (fnsdpRtY9o83Vr4z15bE)
- **Custom Fields:** 53 opportunity fields across 5 groups
- **Sync Strategy:** Bidirectional with automatic conflict resolution
- **Why:** Native CRM integration, workflow automation, custom fields

### Frontend
- **Bootstrap 5:** Responsive UI framework
- **Jinja2:** Server-side templating
- **Minimal JavaScript:** Form validation, confirmations
- **Why:** Fast development, professional UI, accessible

### Document Generation
- **ReportLab or WeasyPrint:** PDF generation
- **PIL/Pillow:** Image processing for passport photos
- **Why:** Generate trip confirmations, itineraries, legal forms

### Development Tools
- **python-dotenv:** Environment configuration
- **requests:** HTTP client for GHL API
- **Flask CLI:** Custom management commands
- **boto3:** AWS S3 integration

---

## Key Architectural Decisions

### 1. Bidirectional Sync Architecture
**Why:** Ensures data consistency between local database and GHL CRM
**Impact:** Users can work in either system with automatic propagation
**Implementation:** 
- TwoWaySyncService handles Local → GHL sync
- GHLSyncService handles GHL → Local bulk sync
- Auto-sync on create/update operations

### 2. Field Mapping System
**Why:** Centralize mapping logic for 55+ custom fields
**Impact:** Easy to extend, maintain, and debug field synchronization
**Implementation:**
- `field_mapping.py` contains TRIP_FIELD_MAP and PASSENGER_FIELD_MAP
- Type conversion utilities handle dates, numbers, booleans
- parse_ghl_custom_fields() normalizes GHL API responses

### 3. Trip-Passenger Linking via trip_name
**Why:** GHL opportunities don't support foreign keys to other opportunities
**Impact:** 85% automated linking success, 15% requires manual review
**Implementation:**
- Use trip_name custom field as shared identifier
- Multi-tier matching (exact → case-insensitive → partial)
- Sync trip names to GHL dropdown for data consistency

### 4. S3 File Storage Architecture
**Why:** Centralized, secure storage for all trip-related documents
**Impact:** Compliance with record-keeping requirements, easy file access
**Implementation:**
- S3 bucket with hierarchical structure (trip → passenger)
- Pre-signed URLs for secure temporary access
- File metadata stored in PostgreSQL with S3 path references
- Automatic file organization on upload

### 5. PostgreSQL for Production
**Why:** Handle 12,000+ records with complex relationships
**Impact:** Better performance, ACID compliance, JSON field support
**Implementation:**
- SQLAlchemy models with proper indexes
- Connection pooling for API sync operations
- Database migrations for schema changes

---

## Stakeholders

- **Trip Organizers:** Create trips, manage passengers, view analytics
- **Passengers:** Enroll in trips, submit details (future self-service)
- **Administrators:** Sync data, manage system, resolve conflicts

---

## Timeline (Current Progress)

- **Stage 1 (Foundation):** ✅ COMPLETE (Oct 2025)
  - Project structure, models, basic routes
  - Trip CRUD with name field
  - Template organization
  
- **Stage 2A (GHL Sync):** ✅ COMPLETE (Oct 2025)
  - Pipeline and stage sync
  - Custom field definitions sync
  - Contact bulk sync with pagination
  - Trip opportunity sync
  - Passenger opportunity sync

- **Stage 2B (Two-Way Sync):** ✅ COMPLETE (Oct 2025)
  - Local → GHL trip creation
  - Local → GHL trip updates
  - Local → GHL passenger creation
  - Auto-sync integration in routes

- **Stage 2C (Field Mapping):** ✅ COMPLETE (Oct 2025)
  - Centralized field mapping system
  - 30+ trip field mappings
  - 25+ passenger field mappings
  - Type conversion utilities

- **Stage 2D (Passenger Linking):** ✅ COMPLETE (Oct 2025)
  - Export all passenger data from GHL
  - Extract trip_name from custom fields
  - Link 5,518 of 6,477 passengers (85%)
  - Sync trip names to GHL dropdown

- **Stage 2E (Search & Filter):** ✅ COMPLETE (Oct 2025)
  - Trip search by destination, date range, vendor
  - Passenger search and filtering
  - Date range queries for trip planning
  - Quick filter presets

- **Stage 3 (UI Enhancements):** 🔄 IN PROGRESS
  - Trip detail page improvements
  - Passenger detail view
  - Stage progression UI
  - Analytics dashboard

- **Stage 4 (File Management):** 🔲 PLANNED
  - S3 bucket integration
  - Passport photo upload
  - Digital signature capture
  - PDF generation
  - File organization and search

**Total Estimated Completion:** December 2025 (90% complete)

---

## Current Status

**What's Working:**
- ✅ Full trip CRUD operations
- ✅ Passenger enrollment with smart contact handling
- ✅ Bidirectional GHL sync (automatic on create/update)
- ✅ Field mapping for 55+ custom fields
- ✅ Pagination for large datasets
- ✅ 85% automated passenger-trip linking
- ✅ Comprehensive error handling
- ✅ PostgreSQL production database
- ✅ Bootstrap 5 responsive UI
- ✅ Search and filter functionality (trips and passengers)

**In Progress:**
- 🔄 UI enhancements (detail pages, analytics)
- 🔄 Resolving 959 unlinked passengers (manual review needed)

**Next Up:**
- 🔲 S3 file storage integration
- 🔲 Passport photo upload functionality
- 🔲 Digital signature capture
- 🔲 PDF document generation
- 🔲 File management interface
- 🔲 Stage progression UI for opportunities
- 🔲 Custom field forms for passenger details
- 🔲 Analytics dashboard

---

**This is the foundation. Read this first before building anything.**

Last Updated: October 27, 2025