# TripBuilder

**A Flask-based travel operations management system with bidirectional GoHighLevel CRM integration**

**Version:** 2.0  
**Status:** Production Active (90% Complete)  
**Build Location:** `tripbuilder/`

---

## 🎯 What is TripBuilder?

TripBuilder bridges your backend trip management with GoHighLevel CRM, creating a seamless workflow for:

- **Trip Management:** Create, manage, and track travel arrangements
- **Passenger Enrollment:** Enroll travelers and collect their details
- **Bidirectional Sync:** Auto-sync all data with GoHighLevel opportunities
- **Contact Management:** Smart contact handling with duplicate prevention
- **File Storage:** Passport photos, signatures, and documents (S3)
- **Search & Filter:** Find trips and passengers quickly

---

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- PostgreSQL 14+
- GoHighLevel account with API access
- AWS S3 bucket (for file storage - optional)

### Installation

```bash
# 1. Clone/Navigate to project
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
cd tripbuilder
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize database
createdb tripbuilder  # First time only
flask init-db

# 6. Sync data from GoHighLevel
flask sync-ghl

# 7. Run the application
python app.py
# Visit http://localhost:5269
```

**For detailed setup instructions:** See [`docs/QUICK-START.md`](docs/QUICK-START.md)

---

## 📁 Project Structure

```
claude_code_tripbuilder/
├── README.md                        # This file
├── .roomodes                        # Custom mode configurations
├── .clinerules                      # Roo Code project rules
├── .venv/                          # Python virtual environment
│
├── memory-bank/                     # 📖 ACTIVE DOCUMENTATION (Read First!)
│   ├── projectBrief.md             # Requirements & scope
│   ├── progress.md                 # Completed work & next steps
│   ├── activeContext.md            # Current focus
│   ├── techContext.md              # Technology stack
│   └── systemPatterns.md           # Code patterns & best practices
│
├── .roo/                           # 📋 ROO CODE RULES (Mandatory)
│   └── rules/
│       ├── START-HERE.md           # ⭐ READ BEFORE EVERY ACTION
│       ├── RULES-INDEX.md          # Complete rules reference
│       ├── project-rules.md        # TripBuilder-specific rules
│       ├── terminal-and-mode-efficiency.md  # Terminal/mode best practices
│       └── README.md               # Rules navigation guide
│
├── docs/                           # 📚 GUIDES & DOCUMENTATION
│   ├── ROO-CODE-GUIDE.md          # How to work with Roo Code
│   └── QUICK-START.md             # Setup & getting started
│
└── tripbuilder/                    # 🚀 APPLICATION CODE
    ├── app.py                      # Flask routes & CLI commands
    ├── models.py                   # Database models (9 tables)
    ├── ghl_api.py                  # GoHighLevel API wrapper
    ├── field_mapping.py            # DB ↔ GHL field mappings
    ├── services/
    │   ├── ghl_sync.py            # GHL → Local bulk sync
    │   ├── two_way_sync.py        # Local → GHL auto-sync
    │   └── file_manager.py        # S3 file operations (planned)
    ├── templates/                  # Jinja2 HTML templates
    ├── static/                     # CSS, JavaScript
    └── [completion docs]           # STAGE_*.md, *_COMPLETE.md
```

---

## 🎯 Core Features

### ✅ Currently Working

1. **Trip Management**
   - Create, edit, delete trips
   - Auto-create TripBooking opportunities in GHL
   - Track 30+ trip fields (dates, capacity, pricing, vendor)
   - Search & filter by destination, dates, vendor

2. **Passenger Enrollment**
   - Enroll contacts as passengers
   - Auto-create Passenger opportunities in GHL
   - Track 25+ passenger fields (passport, health, emergency contacts)
   - 85% automated trip-passenger linking

3. **Bidirectional GHL Sync**
   - Local → GHL: Auto-sync on create/update
   - GHL → Local: Bulk sync via CLI (`flask sync-ghl`)
   - Syncs 12,264 records (693 trips, 6,477 passengers, 5,453 contacts)
   - Graceful error handling with local fallback

4. **Contact Management**
   - Smart contact handling (check local → search GHL → create)
   - Prevents duplicates
   - Links to all associated trips

5. **Search & Filter**
   - Filter trips by destination, date range, vendor, status
   - Search passengers by name, trip, passport status
   - Date range queries for trip planning

### 🔄 In Progress

- Enhanced UI (trip/passenger detail pages)
- Stage progression UI
- Analytics dashboard

### 🔲 Planned

- **S3 File Storage** (passports, signatures, PDFs)
- **Digital Signature Capture**
- **PDF Document Generation** (confirmations, itineraries)
- **File Management Interface**

---

## 🛠️ Technology Stack

### Backend
- **Python 3.x** with type hints
- **Flask 2.3+** for web framework
- **SQLAlchemy 2.0+** for ORM
- **PostgreSQL 14+** for production database

### Integrations
- **GoHighLevel API v2** for CRM operations
- **AWS S3** for file storage (planned)
- **boto3** for S3 operations (planned)

### Frontend
- **Jinja2** for server-side templates
- **Bootstrap 5** for responsive UI
- **JavaScript** for client interactions

### Development Tools
- **Roo Code** with custom modes
- **Flask CLI** for management commands
- **python-dotenv** for configuration

---

## 📖 Documentation Guide

### 🎯 Start Here (In Order):

1. **[`memory-bank/projectBrief.md`](memory-bank/projectBrief.md)** - Understand the project
2. **[`.roo/rules/START-HERE.md`](.roo/rules/START-HERE.md)** - ⭐ **READ BEFORE EVERY ACTION**
3. **[`memory-bank/activeContext.md`](memory-bank/activeContext.md)** - See what's happening now
4. **[`docs/ROO-CODE-GUIDE.md`](docs/ROO-CODE-GUIDE.md)** - Learn the workflow
5. **[`docs/QUICK-START.md`](docs/QUICK-START.md)** - Get set up

### 📚 Reference Documentation:

**Memory Bank (Living Docs - Always Current):**
- [`memory-bank/progress.md`](memory-bank/progress.md) - Completed milestones
- [`memory-bank/techContext.md`](memory-bank/techContext.md) - Tech stack details
- [`memory-bank/systemPatterns.md`](memory-bank/systemPatterns.md) - Code patterns

**Roo Code Rules (Mandatory):**
- [`.roo/rules/RULES-INDEX.md`](.roo/rules/RULES-INDEX.md) - Complete rules reference
- [`.roo/rules/project-rules.md`](.roo/rules/project-rules.md) - TripBuilder-specific rules
- [`.roo/rules/terminal-and-mode-efficiency.md`](.roo/rules/terminal-and-mode-efficiency.md) - Best practices

**TripBuilder Specific:**
- [`tripbuilder/README.md`](tripbuilder/README.md) - Application setup
- [`tripbuilder/TWO_WAY_SYNC_COMPLETE.md`](tripbuilder/TWO_WAY_SYNC_COMPLETE.md) - Sync system docs
- [`tripbuilder/PASSENGER_LINKING_COMPLETE.md`](tripbuilder/PASSENGER_LINKING_COMPLETE.md) - Linking process

### ⚠️ Outdated (Do Not Update):

Root-level `.md` files like `PROJECT_DESCRIPTION.md`, `TECH_STACK.md`, etc. are from earlier phases.  
**Use `memory-bank/` files instead.**

---

## 🎨 Working with Roo Code

TripBuilder uses **Roo Code** with 8 custom modes for efficient development:

### Custom Modes

- **🏗️ Architect** - Planning, documentation (`.md` files only)
- **💻 Code** - Implementation (Python, JS, HTML, CSS)
- **🪲 Debug** - Troubleshooting (all files)
- **📝 Memory Manager** - Doc updates (`memory-bank/*.md`)
- **🪃 Orchestrator** - Complex multi-step projects
- **🗄️ Database** - Schema changes, migrations
- **📁 File Manager** - S3 file operations
- **🔌 API Integration** - GHL API work

### Golden Rules

1. **Check `environment_details` before EVERY command**
2. **Never use `cd directory && command`** (creates new terminals)
3. **Read [`.roo/rules/START-HERE.md`](.roo/rules/START-HERE.md) before every action**
4. **Reuse terminals** (max 1-2 per session)
5. **Switch modes purposefully** (verify file type compatibility)
6. **Update `memory-bank/` files** after completing tasks

**For complete Roo Code guide:** See [`docs/ROO-CODE-GUIDE.md`](docs/ROO-CODE-GUIDE.md)

---

## 🔄 Common Workflows

### Creating a New Trip

```bash
# 1. Ensure app is running
cd tripbuilder
python app.py

# 2. Visit http://localhost:5269/trips/new
# 3. Fill out form and submit
# 4. Trip auto-syncs to GHL as TripBooking opportunity
```

### Enrolling a Passenger

```bash
# 1. From trip detail page, click "Enroll Passenger"
# 2. Enter passenger details
# 3. System:
#    - Checks local database for contact
#    - Searches GHL if not found
#    - Creates contact in GHL if needed
#    - Creates Passenger opportunity
#    - Links passenger to trip
```

### Syncing from GoHighLevel

```bash
cd tripbuilder
flask sync-ghl

# Syncs:
# - Pipelines & stages
# - Custom fields
# - All contacts
# - All trip opportunities
# - All passenger opportunities
```

---

## 🗄️ Database

**Database:** `tripbuilder`  
**User:** `ridiculaptop`  
**Tables:** 9 (trips, passengers, contacts, pipelines, stages, custom_fields, etc.)

**Quick Stats:**
- Trips: 693
- Passengers: 6,477 (5,518 linked to trips)
- Contacts: 5,453
- Custom Fields: 53

**Access:**
```bash
psql -U ridiculaptop -d tripbuilder
```

---

## 🔐 Configuration

**Environment Variables** (in `tripbuilder/.env`):

```bash
# GoHighLevel API
GHL_API_TOKEN=your_private_integration_token
GHL_LOCATION_ID=your_location_id

# Database
DATABASE_URL=postgresql://ridiculaptop@localhost:5432/tripbuilder

# Flask
SECRET_KEY=your_random_secret_key
PORT=5269

# AWS S3 (when implemented)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=tripbuilder-files
AWS_REGION=us-east-1
```

---

## 🚨 Important Notes

### Schema Compatibility

**Use current attribute names:**
- `trips.max_passengers` (NOT `max_capacity`)
- `trips.internal_trip_details` (NOT `notes`)
- `passengers.trip_name` (linking field)

### Contact Details Button

All detail pages MUST have "View in GHL" button:
```
https://app.gohighlevel.com/v2/location/dGKixXhucwniMwOQnZdr/contacts/detail/{contact_id}
```

### Pipeline IDs (Do Not Change)

- **TripBooking:** `IlWdPtOpcczLpgsde2KF`
- **Passenger:** `fnsdpRtY9o83Vr4z15bE`

---

## 🧪 Testing

```bash
# Run application
python app.py

# Test sync
flask sync-ghl

# Check database
psql -U ridiculaptop -d tripbuilder

# Verify counts
SELECT COUNT(*) FROM trips;
SELECT COUNT(*) FROM passengers;
SELECT COUNT(*) FROM contacts;
```

---

## 📊 Project Status

**Overall Progress:** 90% Complete

**Completed Stages:**
- ✅ Stage 1: Foundation & Setup
- ✅ Stage 2A: GHL Data Sync
- ✅ Stage 2B: Two-Way Sync System
- ✅ Stage 2C: Field Mapping Integration
- ✅ Stage 2D: Passenger-Trip Linking
- ✅ Stage 2E: Search & Filter

**Current Stage:**
- 🔄 Stage 3: UI Enhancements (70% complete)

**Planned:**
- 🔲 Stage 4: File Management (S3)
- 🔲 Stage 5: PDF Generation
- 🔲 Stage 6: Advanced Features

---

## 🤝 Contributing

### Before Making Changes

1. Read [`.roo/rules/START-HERE.md`](.roo/rules/START-HERE.md)
2. Check [`memory-bank/activeContext.md`](memory-bank/activeContext.md)
3. Review [`.roo/rules/project-rules.md`](.roo/rules/project-rules.md)
4. Choose appropriate mode for your task

### After Making Changes

1. Test thoroughly
2. Update `memory-bank/progress.md`
3. Update `memory-bank/activeContext.md`
4. Document decisions

---

## 📞 Support

### Quick Reference

- **Setup Issues:** [`docs/QUICK-START.md`](docs/QUICK-START.md)
- **Roo Code Help:** [`docs/ROO-CODE-GUIDE.md`](docs/ROO-CODE-GUIDE.md)
- **Terminal Problems:** [`.roo/rules/terminal-and-mode-efficiency.md`](.roo/rules/terminal-and-mode-efficiency.md)
- **GHL Sync Issues:** [`.roo/rules/project-rules.md`](.roo/rules/project-rules.md)
- **Database Errors:** [`memory-bank/techContext.md`](memory-bank/techContext.md)

---

## 📄 License

Proprietary - All Rights Reserved

---

## ✨ Key Features Highlight

- ✅ **12,264 Records Synced** from GoHighLevel
- ✅ **85% Automated** passenger-trip linking
- ✅ **Bidirectional Sync** on every create/update
- ✅ **55+ Custom Fields** mapped and syncing
- ✅ **Graceful Error Handling** with local fallback
- ✅ **Search & Filter** across all entities
- 🔄 **S3 File Storage** coming soon
- 🔄 **PDF Generation** coming soon

---

**Last Updated:** October 27, 2025

**Remember:** Read [`.roo/rules/START-HERE.md`](.roo/rules/START-HERE.md) before every action!

**Happy Building! 🎉**
