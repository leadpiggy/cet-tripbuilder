# System Patterns & Architecture

**Project:** TripBuilder
**Build Location:** tripbuilder/
**Last Updated:** October 27, 2025

---

## 🚨 Terminal & Mode Efficiency Patterns (MANDATORY)

**Status:** ✅ ACTIVE - These are STANDARD operating patterns
**Impact:** CRITICAL - All AI interactions MUST follow these rules
**Source:** Roo Code Best Practices

### Overview

Comprehensive rules to prevent terminal proliferation, mode confusion, and context awareness failures. **These patterns are MANDATORY and override any conflicting instructions.**

---

### 1. 🖥️ Terminal Management Pattern

**CRITICAL RULE:** Check `environment_details` BEFORE every command execution.

#### Pattern Requirements

**ALWAYS:**
- ✅ Check `environment_details` for "Actively Running Terminals" section
- ✅ Reuse existing terminals when they're in the correct directory
- ✅ Understand which terminal will execute your command
- ✅ Wait for user confirmation after each command

**NEVER:**
- ❌ Use `cd directory && command` syntax (creates new terminals!)
- ❌ Execute commands without checking environment_details first
- ❌ Assume command success without user confirmation
- ❌ Create multiple terminals for the same directory

#### Example Terminal Usage:
```bash
# WRONG - Creates new terminal every time
cd tripbuilder && flask sync-ghl
cd tripbuilder && python app.py
cd tripbuilder && psql -U ridiculaptop -d tripbuilder

# RIGHT - Use one terminal, sequential commands
# First command (creates terminal in workspace root)
cd tripbuilder

# Wait for confirmation, then:
flask sync-ghl

# Wait for confirmation, then:
python app.py
```

---

### 2. 🎯 Mode Selection Pattern

**CRITICAL RULE:** Verify current mode can edit target file types BEFORE editing.

#### Mode Capabilities Matrix

| Mode | Can Edit | Can Execute Commands | Purpose |
|------|----------|---------------------|---------|
| **Architect** | `*.md` only | Yes | Planning, documentation, strategy |
| **Code** | Python, JS, HTML, CSS | Yes | Implementation, bug fixes |
| **Debug** | All files | Yes | Troubleshooting, investigation |
| **Memory Manager** | `memory-bank/*.md`, `docs/*.md` | No | Documentation updates |

#### When to Use Each Mode:

**Architect Mode (Current):**
- ✅ Creating/updating `.md` documentation
- ✅ Planning features and architecture
- ✅ Breaking down complex tasks
- ✅ Creating diagrams and specifications
- ❌ Editing Python/JS/HTML code (switch to Code mode)

**Code Mode:**
- ✅ Implementing features in `app.py`, `models.py`, `ghl_api.py`
- ✅ Modifying templates (HTML)
- ✅ Updating CSS/JavaScript
- ✅ Bug fixes in application code
- ❌ Editing markdown documentation (stay in Architect or use Memory Manager)

**Debug Mode:**
- ✅ Investigating errors
- ✅ Adding logging statements
- ✅ Analyzing stack traces
- ✅ Testing hypotheses
- ❌ Major feature implementation (use Code mode)

**Memory Manager Mode:**
- ✅ Updating memory-bank files after completing work
- ✅ Documenting progress
- ✅ Recording decisions
- ❌ Any code changes (use Code mode)

---

### 3. 🧭 Context Awareness Pattern

**CRITICAL RULE:** Understand current working directory from `environment_details`.

#### Working Directory Mental Model

```
Workspace Root: /Users/ridiculaptop/Downloads/claude_code_tripbuilder
├── .venv/                    ← Python virtual environment
├── memory-bank/              ← Roo Code context tracking
├── .roo/                     ← Roo Code rules
├── tripbuilder/              ← APPLICATION CODE (most work happens here)
│   ├── app.py
│   ├── models.py
│   ├── ghl_api.py
│   ├── services/
│   ├── templates/
│   └── static/
└── [Old documentation files]  ← Outdated, use memory-bank instead
```

**Key Concept:**
- Workspace is `/Users/ridiculaptop/Downloads/claude_code_tripbuilder`
- Application code lives in `tripbuilder/` subdirectory
- Most commands should execute in `tripbuilder/` directory
- Virtual environment is in workspace root `.venv/`

**Command Directory Strategy:**
```bash
# For application commands, cd to tripbuilder first:
cd tripbuilder
python app.py

# For virtual environment activation, use workspace root:
source .venv/bin/activate

# For database access (from tripbuilder directory):
psql -U ridiculaptop -d tripbuilder
```

---

## 🎯 TripBuilder-Specific Patterns

### Pattern 1: Bidirectional Sync Strategy

**When to use:** Any operation involving trips, passengers, or contacts

**Implementation:**
```python
# Creating a trip
trip = Trip(name="Hawaii 2025", destination="Honolulu")
db.session.add(trip)
db.session.flush()  # Get trip.id

# Auto-sync to GHL
from services.two_way_sync import TwoWaySyncService
sync_service = TwoWaySyncService(ghl_api)
sync_service.auto_sync_on_trip_create(trip)

db.session.commit()  # Commit after successful sync
```

**Pattern Rules:**
1. Always `flush()` before syncing (need ID)
2. Sync before `commit()` (rollback if sync fails)
3. Handle sync errors gracefully
4. Flash messages to inform user

---

### Pattern 2: Field Mapping Pattern

**When to use:** Reading or writing custom field data

**Implementation:**
```python
from field_mapping import (
    parse_ghl_custom_fields,
    map_trip_custom_fields,
    map_passenger_custom_fields
)

# Reading from GHL
custom_fields_list = opp_data.get('customFields', [])
custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
mapped_fields = map_trip_custom_fields(custom_fields_dict)

# Apply to model
for column, value in mapped_fields.items():
    if hasattr(trip, column) and value is not None:
        setattr(trip, column, value)

# Writing to GHL
ghl_api.update_custom_field(
    opp_id, 
    'opportunity.tripname', 
    trip.name
)
```

**Pattern Rules:**
1. Always use field mapping utilities
2. Never hardcode field keys in routes
3. Use `parse_ghl_custom_fields()` to normalize GHL responses
4. Check field existence with `hasattr()` before setting

---

### Pattern 3: Smart Contact Handling

**When to use:** Enrolling passengers or creating contacts

**Implementation:**
```python
# Step 1: Check local database
contact = Contact.query.filter_by(email=email).first()

if not contact:
    # Step 2: Search GHL
    ghl_contacts = ghl_api.search_contacts(email, location_id)
    
    if ghl_contacts:
        # Found in GHL, sync to local
        contact_data = ghl_contacts[0]
        contact = Contact(
            id=contact_data['id'],
            email=contact_data['email'],
            # ... other fields
        )
        db.session.add(contact)
    else:
        # Step 3: Create in GHL, then local
        ghl_contact = ghl_api.create_contact({
            'email': email,
            'firstName': firstname,
            # ... other fields
        }, location_id)
        
        contact = Contact(
            id=ghl_contact['id'],
            email=email,
            # ... other fields
        )
        db.session.add(contact)

db.session.commit()
```

**Pattern Rules:**
1. Always check local first (performance)
2. Search GHL before creating (avoid duplicates)
3. Sync GHL contact to local immediately
4. Use contact ID from GHL as primary key

---

### Pattern 4: Pagination Pattern

**When to use:** Fetching large datasets from GHL

**Implementation:**
```python
all_opportunities = []
next_page = None

while True:
    # Fetch page
    response = ghl_api.get(
        f'/opportunities/search',
        params={
            'location_id': location_id,
            'pipelineId': pipeline_id,
            'limit': 100,
            'startAfterId': next_page
        }
    )
    
    opportunities = response.get('opportunities', [])
    all_opportunities.extend(opportunities)
    
    # Check for next page
    meta = response.get('meta', {})
    next_page = meta.get('nextPageStartAfterId')
    
    if not next_page:
        break  # No more pages
    
    time.sleep(0.1)  # Rate limiting

return all_opportunities
```

**Pattern Rules:**
1. Use `startAfterId` for pagination (not offset)
2. Limit to 100 records per page (GHL max)
3. Add small delay between pages (rate limiting)
4. Always check `meta.nextPageStartAfterId` for continuation

---

### Pattern 5: Error Handling Pattern

**When to use:** All routes and sync operations

**Implementation:**
```python
@app.route('/trips/<int:id>/edit', methods=['POST'])
def trip_edit(id):
    trip = Trip.query.get_or_404(id)
    
    try:
        # Update trip
        trip.name = request.form['name']
        trip.destination = request.form['destination']
        # ... other fields
        
        # Attempt GHL sync
        try:
            sync_service.auto_sync_on_trip_update(trip)
            db.session.commit()
            flash('Trip updated and synced to GHL!', 'success')
        except Exception as sync_error:
            # Graceful degradation
            db.session.commit()  # Still save locally
            flash(f'Trip updated locally, but GHL sync failed: {sync_error}', 'warning')
            print(f"GHL sync error: {sync_error}")  # Log for debugging
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating trip: {e}', 'danger')
        print(f"Trip update error: {e}")
    
    return redirect(url_for('trip_detail', id=id))
```

**Pattern Rules:**
1. Outer try/catch for database errors
2. Inner try/catch for GHL sync errors
3. Always commit local changes (graceful degradation)
4. Flash appropriate messages to user
5. Log errors to console for debugging
6. Rollback on database errors

---

### Pattern 6: Trip-Passenger Linking Pattern

**When to use:** Creating or updating passenger records

**Implementation:**
```python
# When creating passenger
passenger = Passenger(
    id=ghl_opportunity_id,  # GHL Passenger opportunity ID
    contact_id=contact.id,
    trip_id=None,  # May not know yet
    trip_name=trip.name  # Use trip_name for linking
)

# Later, link by matching trip_name
trips = Trip.query.all()
trip_map = {trip.name.lower(): trip for trip in trips}

passenger_trip = trip_map.get(passenger.trip_name.lower())
if passenger_trip:
    passenger.trip_id = passenger_trip.id
```

**Pattern Rules:**
1. Always set `trip_name` on passenger creation
2. Use case-insensitive matching
3. Support partial matches for flexibility
4. Allow `trip_id` to be null initially
5. Provide script for batch linking

---

## 📚 Reference Documentation

**MANDATORY Reading Before ALL Work:**

1. **`memory-bank/projectBrief.md`** - Requirements and scope
2. **`memory-bank/progress.md`** - What's done, what's next
3. **`memory-bank/activeContext.md`** - Current work focus
4. **`memory-bank/techContext.md`** - Technology stack details
5. **`memory-bank/systemPatterns.md`** - This file

**Application Documentation:**
- [`tripbuilder/README.md`](tripbuilder/README.md) - Setup and usage
- [`tripbuilder/TWO_WAY_SYNC_COMPLETE.md`](tripbuilder/TWO_WAY_SYNC_COMPLETE.md) - Sync system
- [`tripbuilder/PASSENGER_LINKING_COMPLETE.md`](tripbuilder/PASSENGER_LINKING_COMPLETE.md) - Linking process

---

## 🔴 Common Anti-Patterns to Avoid

### Anti-Pattern 1: Multiple Terminal Syndrome
```bash
# WRONG - Creates 5 terminals!
cd tripbuilder && flask sync-ghl
cd tripbuilder && python app.py
cd tripbuilder && python verify_data.py
cd tripbuilder && psql -U ridiculaptop -d tripbuilder
cd tripbuilder && python test_two_way_sync.py

# RIGHT - Use one terminal
cd tripbuilder
flask sync-ghl
# Wait for completion...
python app.py
# etc.
```

### Anti-Pattern 2: Hardcoded Field Keys
```python
# WRONG
trip.destination = custom_fields['opportunity.tripname']  # Hardcoded!

# RIGHT
from field_mapping import map_trip_custom_fields
mapped_fields = map_trip_custom_fields(custom_fields)
trip.destination = mapped_fields.get('destination')
```

### Anti-Pattern 3: Ignoring Sync Errors
```python
# WRONG - Data loss if sync fails!
trip.name = new_name
sync_service.auto_sync_on_trip_update(trip)  # What if this fails?
db.session.commit()

# RIGHT - Graceful degradation
try:
    trip.name = new_name
    sync_service.auto_sync_on_trip_update(trip)
    db.session.commit()
    flash('Updated and synced!', 'success')
except Exception as e:
    db.session.commit()  # Save locally anyway
    flash(f'Updated locally, sync failed: {e}', 'warning')
```

### Anti-Pattern 4: Assuming Successful Contact Creation
```python
# WRONG
ghl_contact = ghl_api.create_contact(data, location_id)
contact = Contact(id=ghl_contact['id'])  # What if create failed?

# RIGHT
try:
    ghl_contact = ghl_api.create_contact(data, location_id)
    if ghl_contact and 'id' in ghl_contact:
        contact = Contact(id=ghl_contact['id'])
    else:
        raise ValueError("GHL did not return contact ID")
except Exception as e:
    flash(f'Failed to create contact: {e}', 'danger')
    return redirect(url_for('trips'))
```

---

## 🎓 Learning Progression

### Stage 1: Understanding the Codebase
1. Read memory-bank files (all 5)
2. Review database models in `models.py`
3. Understand sync services (`ghl_sync.py`, `two_way_sync.py`)
4. Examine field mappings in `field_mapping.py`

### Stage 2: Making Changes
1. Use Code mode for Python/HTML/CSS changes
2. Use Architect mode for planning and documentation
3. Follow patterns documented here
4. Test changes locally before committing

### Stage 3: Mastery
1. Patterns become second nature
2. Efficient terminal and mode usage
3. Clean, maintainable code
4. Comprehensive error handling

---

**These patterns guide all implementation decisions.**

Last Updated: October 27, 2025

---

### Pattern 7: S3 File Upload Pattern (PLANNED)

**When to use:** Uploading passports, signatures, or documents

**Implementation:**
```python
from services.file_manager import S3FileManager
from werkzeug.utils import secure_filename

@app.route('/passengers/<passenger_id>/upload-passport', methods=['POST'])
def upload_passport(passenger_id):
    passenger = Passenger.query.get_or_404(passenger_id)
    trip = Trip.query.get(passenger.trip_id)
    
    if 'passport' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('passenger_detail', id=passenger_id))
    
    file = request.files['passport']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('passenger_detail', id=passenger_id))
    
    # Secure filename
    filename = secure_filename(file.filename)
    
    # S3 path structure
    s3_path = f"trips/{trip.name}/passengers/{passenger.firstname}_{passenger.lastname}/passports/{filename}"
    
    try:
        # Upload to S3
        file_manager = S3FileManager()
        file_manager.upload_file(file.stream, s3_path)
        
        # Save metadata
        file_record = File(
            filename=filename,
            s3_path=s3_path,
            file_type='passport',
            content_type=file.content_type,
            file_size=file.content_length,
            passenger_id=passenger_id,
            trip_id=trip.id
        )
        db.session.add(file_record)
        db.session.commit()
        
        flash('Passport uploaded successfully!', 'success')
    except Exception as e:
        flash(f'Upload failed: {e}', 'danger')
    
    return redirect(url_for('passenger_detail', id=passenger_id))
```

**Pattern Rules:**
1. Always use `secure_filename()` to sanitize filenames
2. Follow hierarchical S3 structure (trip → passenger → file type)
3. Save file metadata to database for quick access
4. Use pre-signed URLs for downloads (temporary, secure)
5. Handle upload errors gracefully
6. Link files to both passenger and trip for easy navigation

---

### Pattern 8: File Download Pattern (PLANNED)

**When to use:** Allowing users to download uploaded files

**Implementation:**
```python
@app.route('/files/<int:file_id>/download')
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)
    
    try:
        # Generate pre-signed URL (expires in 1 hour)
        file_manager = S3FileManager()
        download_url = file_manager.get_presigned_url(
            file_record.s3_path,
            expiration=3600
        )
        
        # Redirect to S3 URL
        return redirect(download_url)
        
    except Exception as e:
        flash(f'Download failed: {e}', 'danger')
        return redirect(request.referrer or url_for('index'))
```

**Pattern Rules:**
1. Use pre-signed URLs instead of direct S3 access
2. Set appropriate expiration time (default 1 hour)
3. Never expose S3 credentials to frontend
4. Log download attempts for auditing
5. Return to previous page if download fails

---

### Pattern 9: PDF Generation Pattern (PLANNED)

**When to use:** Creating trip confirmations, itineraries, or legal forms

**Implementation:**
```python
from services.pdf_generator import PDFGenerator

@app.route('/trips/<int:trip_id>/generate-confirmation/<passenger_id>')
def generate_confirmation(trip_id, passenger_id):
    trip = Trip.query.get_or_404(trip_id)
    passenger = Passenger.query.get_or_404(passenger_id)
    
    try:
        # Generate PDF
        pdf_gen = PDFGenerator()
        s3_path = pdf_gen.generate_trip_confirmation(trip, passenger)
        
        # Save metadata
        file_record = File(
            filename=f'confirmation_{trip.id}_{passenger.id}.pdf',
            s3_path=s3_path,
            file_type='pdf',
            content_type='application/pdf',
            passenger_id=passenger_id,
            trip_id=trip_id
        )
        db.session.add(file_record)
        db.session.commit()
        
        flash('Confirmation generated successfully!', 'success')
        
        # Download immediately
        return redirect(url_for('download_file', file_id=file_record.id))
        
    except Exception as e:
        flash(f'PDF generation failed: {e}', 'danger')
        return redirect(url_for('trip_detail', id=trip_id))
```

**Pattern Rules:**
1. Generate PDFs server-side (not client-side)
2. Save to S3 immediately after generation
3. Create database record for tracking
4. Link to both trip and passenger
5. Offer immediate download after generation
6. Handle generation errors gracefully

---

### Pattern 10: Search & Filter Pattern

**When to use:** Implementing search functionality for trips or passengers

**Implementation:**
```python
@app.route('/trips/search')
def search_trips():
    # Get query parameters
    destination = request.args.get('destination', '').strip()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vendor = request.args.get('vendor', '').strip()
    min_capacity = request.args.get('min_capacity', type=int)
    
    # Build query
    query = Trip.query
    
    # Apply filters
    if destination:
        query = query.filter(Trip.destination.ilike(f'%{destination}%'))
    
    if start_date:
        query = query.filter(Trip.arrival_date >= start_date)
    
    if end_date:
        query = query.filter(Trip.return_date <= end_date)
    
    if vendor:
        query = query.filter(Trip.trip_vendor.ilike(f'%{vendor}%'))
    
    if min_capacity:
        query = query.filter(Trip.max_passengers >= min_capacity)
    
    # Execute query
    trips = query.order_by(Trip.arrival_date.desc()).all()
    
    return render_template('trips/search_results.html', 
                         trips=trips,
                         filters={
                             'destination': destination,
                             'start_date': start_date,
                             'end_date': end_date,
                             'vendor': vendor,
                             'min_capacity': min_capacity
                         })
```

**Pattern Rules:**
1. Use `ilike()` for case-insensitive text search
2. Strip whitespace from text inputs
3. Validate date formats before querying
4. Return empty results (not error) for no matches
5. Pass filter values back to template for display
6. Support combining multiple filters
7. Order results logically (e.g., by date)

---

### Pattern 11: Date Range Query Pattern

**When to use:** Finding trips in progress during a specific period

**Implementation:**
```python
@app.route('/trips/in-progress')
def trips_in_progress():
    # Get date range
    range_start = request.args.get('start', default=date.today().isoformat())
    range_end = request.args.get('end', default=(date.today() + timedelta(days=30)).isoformat())
    
    # Convert to date objects
    start = date.fromisoformat(range_start)
    end = date.fromisoformat(range_end)
    
    # Query trips where range overlaps with trip dates
    trips = Trip.query.filter(
        Trip.arrival_date <= end,
        Trip.return_date >= start
    ).order_by(Trip.arrival_date).all()
    
    return render_template('trips/in_progress.html',
                         trips=trips,
                         range_start=range_start,
                         range_end=range_end)
```

**Pattern Rules:**
1. Use date ranges with overlap logic (not exact match)
2. Default to reasonable range (e.g., next 30 days)
3. Validate date inputs and handle errors
4. Allow flexible range specification
5. Order by start date for chronological view
