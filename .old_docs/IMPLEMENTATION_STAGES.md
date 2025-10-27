# TripBuilder - Implementation Stages

## Stage 1: Project Setup & Foundation
**Goal**: Establish development environment and core infrastructure

### Tasks:
1. **Initialize Flask Application**
   - Create `app.py` with Flask app instance
   - Configure Flask settings (secret key, debug mode)
   - Set up project folder structure

2. **Database Configuration**
   - Install Flask-SQLAlchemy, Flask-Migrate
   - Configure database URI (SQLite for dev)
   - Import models from `base.py.txt`
   - Initialize database with `flask db init`, `flask db migrate`, `flask db upgrade`

3. **Environment Configuration**
   - Create `.env` file with:
     - `GHL_API_TOKEN`
     - `GHL_LOCATION_ID`
     - `DATABASE_URL`
     - `SECRET_KEY`
   - Load environment variables with python-dotenv

4. **GHL API Wrapper Integration**
   - Add `ghl-api-wrapper-complete.py` to project
   - Initialize wrapper with API token
   - Create wrapper instance accessible to routes (app context or global)

5. **Seed Database**
   - Write script to import CSV data:
     - Pipelines (2 records)
     - Pipeline Stages (11 records)
     - Custom Field Groups (13 records)
     - Custom Fields (100+ records)
   - Run seed script

6. **Base Template**
   - Create `templates/base.html` with:
     - Bootstrap 5 CSS/JS from CDN
     - Navigation bar (Trips, Contacts, Dashboard)
     - Flash message display area
     - Content block for child templates

**Deliverables**: Working Flask app, initialized database, base template

---

## Stage 2: Trip Management (Backend to GHL)
**Goal**: CRUD for Trip records with TripBooking opportunity sync

### Tasks:
1. **Trip List Route** (`GET /trips`)
   - Query all Trip records from database
   - Fetch associated TripBooking opportunities from GHL
   - Render `trips/list.html` with trip data

2. **Trip List Template** (`trips/list.html`)
   - Table with columns: Destination, Start Date, End Date, Passengers, Stage, Actions
   - "New Trip" button
   - View/Edit/Delete buttons per row

3. **Create Trip Route** (`GET /trips/new`, `POST /trips/new`)
   - GET: Render form with fields (destination, start_date, end_date, notes)
   - POST:
     - Validate form data
     - Create Trip record in database
     - Create TripBooking opportunity in GHL via wrapper
     - Link opportunity ID to Trip record
     - Initialize opportunity at "FormSubmit" stage
     - Redirect to trip detail page

4. **Trip Detail Route** (`GET /trips/<trip_id>`)
   - Query Trip by ID
   - Fetch TripBooking opportunity from GHL
   - Query all Passenger records for this trip
   - Fetch Passenger opportunities from GHL
   - Render `trips/detail.html`

5. **Trip Detail Template** (`trips/detail.html`)
   - Display trip info (editable form)
   - Show TripBooking opportunity stage with stage progression buttons
   - List passengers with their stages
   - "Add Passenger" button
   - Section for trip custom fields (collapsed accordion)

6. **Update Trip Route** (`POST /trips/<trip_id>/edit`)
   - Update Trip record
   - Sync changes to TripBooking opportunity in GHL
   - Flash success message
   - Redirect to trip detail

7. **Delete Trip Route** (`POST /trips/<trip_id>/delete`)
   - Confirmation modal
   - Delete TripBooking opportunity from GHL
   - Delete all Passenger opportunities for this trip
   - Delete Trip record from database
   - Redirect to trip list

8. **Stage Progression Route** (`POST /opportunities/<opp_id>/progress`)
   - Get current stage
   - Determine next stage
   - Update opportunity stage via GHL API
   - Flash success message
   - Redirect back

**Deliverables**: Full Trip CRUD with GHL TripBooking sync

---

## Stage 3: Contact Management (GHL to Backend)
**Goal**: Manage GHL contacts within TripBuilder UI

### Tasks:
1. **Contact List Route** (`GET /contacts`)
   - Fetch contacts from GHL via search API
   - Optionally cache in local database
   - Render `contacts/list.html`

2. **Contact List Template** (`contacts/list.html`)
   - Table with: Name, Email, Phone, Tags, Trips Count, Actions
   - "New Contact" button
   - Search/filter bar

3. **Create Contact Route** (`GET /contacts/new`, `POST /contacts/new`)
   - GET: Render form (firstname, lastname, email, phone)
   - POST:
     - Validate data
     - Create contact in GHL via wrapper
     - Optionally cache in local Contact table
     - Redirect to contact detail

4. **Contact Detail Route** (`GET /contacts/<contact_id>`)
   - Fetch contact from GHL
   - Query all Passenger records for this contact
   - Fetch Passenger opportunities
   - Render `contacts/detail.html`

5. **Contact Detail Template** (`contacts/detail.html`)
   - Display contact info (editable)
   - List all trips contact is enrolled in
   - Show passenger stage for each trip
   - "Enroll in Trip" button
   - Tasks section for contact

6. **Update Contact Route** (`POST /contacts/<contact_id>/edit`)
   - Update contact in GHL
   - Update local cache if applicable
   - Redirect to contact detail

7. **Delete Contact Route** (`POST /contacts/<contact_id>/delete`)
   - Confirmation modal (warn about trip associations)
   - Delete from GHL
   - Delete local record
   - Redirect to contact list

**Deliverables**: Full Contact CRUD integrated with GHL

---

## Stage 4: Passenger Enrollment (Core Link)
**Goal**: Link Contacts to Trips via Passenger opportunities

### Tasks:
1. **Add Passenger Route** (`GET /trips/<trip_id>/add-passenger`, `POST /trips/<trip_id>/add-passenger`)
   - GET:
     - Fetch all contacts
     - Render form with contact selector dropdown
     - Option to create new contact inline
   - POST:
     - Get selected contact_id
     - Create Passenger opportunity in GHL:
       - `contact_id`: Selected contact
       - `pipeline_id`: Passenger pipeline ID (fnsdpRtY9o83Vr4z15bE)
       - `stage_id`: AddedToTrip stage ID
       - `name`: "Trip: {destination} - {contact_name}"
       - Custom field linking to backend Trip ID
     - Create Passenger record in database:
       - `id`: GHL opportunity ID
       - `contact_id`, `trip_id`, `stage_id`
     - Redirect to trip detail

2. **Remove Passenger Route** (`POST /passengers/<passenger_id>/remove`)
   - Delete Passenger opportunity from GHL
   - Delete Passenger record from database
   - Redirect to trip detail

3. **Passenger Detail Route** (`GET /passengers/<passenger_id>`)
   - Fetch Passenger opportunity from GHL
   - Fetch custom field values
   - Group fields by CustomFieldGroup
   - Render `passengers/detail.html`

4. **Passenger Detail Template** (`passengers/detail.html`)
   - Display passenger info (contact name, trip name)
   - Show current stage with progression buttons
   - Custom field groups as collapsible sections:
     - Passport Info
     - Health Details
     - Emergency Contact
     - Room Info
     - Legal
     - Files
   - Each field group has form to update fields
   - Save button per group

**Deliverables**: Functional passenger enrollment system

---

## Stage 5: Custom Field Management
**Goal**: Dynamic forms for custom field data entry

### Tasks:
1. **Fetch Custom Fields**
   - Query CustomField and CustomFieldGroup from database
   - Filter by model (`opportunity`) and pipeline

2. **Generate Dynamic Forms**
   - Helper function to render form field based on data type:
     - TEXT → `<input type="text">`
     - LARGE_TEXT → `<textarea>`
     - SINGLE_OPTION → `<select>` with options
     - MULTIPLE_SELECT_OPTIONS → `<select multiple>` or checkboxes
     - FILEUPLOAD → `<input type="file">`
     - DATE → `<input type="date">`
   - Use field placeholder, validation rules

3. **Update Custom Fields Route** (`POST /opportunities/<opp_id>/custom-fields`)
   - Receive field_key → value mappings from form
   - For each field:
     - Call `ghl.opportunities.upsert_custom_field(opp_id, field_key, value)`
   - Handle errors (invalid values, type mismatches)
   - Flash success message
   - Redirect to passenger detail

4. **Custom Field Validation**
   - Required fields enforcement
   - Format validation (email, phone, date)
   - Option constraints (value must be in picklist)
   - File size/type validation

**Deliverables**: Dynamic custom field forms with GHL sync

---

## Stage 6: Stage Progression & Workflow
**Goal**: Move opportunities through pipeline stages

### Tasks:
1. **Stage Indicator Component**
   - Visual display of current stage (badge, progress bar)
   - Show stage name and position

2. **Stage Progression Logic**
   - Function to get next stage given current stage and pipeline
   - Validation: Can only progress forward (or allow backwards for corrections)

3. **Batch Stage Updates**
   - On Trip detail page, checkboxes to select multiple passengers
   - "Progress Selected to [Stage]" button
   - Updates all selected passenger opportunities

4. **Stage History Tracking** (optional enhancement)
   - Store stage changes in local database
   - Show timeline of stage transitions

**Deliverables**: Full stage management system

---

## Stage 7: Tasks Integration
**Goal**: Manage GHL tasks for contacts

### Tasks:
1. **View Tasks** (on Contact detail page)
   - Fetch tasks via `ghl.tasks.get_all(contact_id)`
   - Display in table (Title, Due Date, Status)

2. **Create Task Route** (`POST /contacts/<contact_id>/tasks/new`)
   - Form with title, due_date
   - Create task via wrapper
   - Redirect to contact detail

3. **Complete Task Route** (`POST /tasks/<task_id>/complete`)
   - Mark task complete via wrapper
   - Redirect back

4. **Delete Task Route** (`POST /tasks/<task_id>/delete`)
   - Delete task via wrapper
   - Redirect back

**Deliverables**: Task management integrated

---

## Stage 8: Sync & Data Integrity
**Goal**: Maintain consistency between systems

### Tasks:
1. **Sync Service Module**
   - Functions to sync Trips ↔ TripBooking opportunities
   - Functions to sync Passengers ↔ Passenger opportunities
   - Functions to sync Contacts ↔ GHL contacts

2. **Manual Sync Route** (`POST /sync`)
   - Trigger full sync
   - Compare database records with GHL data
   - Update/create/delete as needed
   - Log sync results

3. **Orphan Detection**
   - Identify GHL opportunities without backend records
   - Identify backend records without GHL opportunities
   - Provide UI to resolve (link or delete)

**Deliverables**: Reliable sync system

---

## Stage 9: UI/UX Polish
**Goal**: Enhance user experience

### Tasks:
1. **Responsive Design**
   - Test on mobile, tablet, desktop
   - Adjust layouts for smaller screens

2. **Loading Indicators**
   - Show spinners during API calls
   - Disable buttons to prevent double-clicks

3. **Improved Navigation**
   - Breadcrumbs
   - Back buttons
   - Contextual links

4. **Enhanced Flash Messages**
   - Toast notifications (auto-dismiss)
   - Color-coded by type (success=green, error=red)

5. **Confirmation Modals**
   - Replace `confirm()` with Bootstrap modals
   - More descriptive warnings

**Deliverables**: Polished, user-friendly interface

---

## Stage 10: Testing & Documentation
**Goal**: Ensure reliability and maintainability

### Tasks:
1. **Manual Testing**
   - Test all user workflows
   - Test error handling (API failures, invalid data)
   - Test edge cases (empty lists, deleted records)

2. **Code Documentation**
   - Docstrings for all functions
   - Inline comments for complex logic
   - README with setup instructions

3. **User Documentation**
   - User guide for common workflows
   - Screenshot walkthroughs
   - FAQ section

4. **Deployment Preparation**
   - Production config (disable debug)
   - Database migration scripts
   - Deployment checklist

**Deliverables**: Fully tested, documented application ready for deployment

---

## Implementation Timeline

**Estimated Duration: 6-8 weeks**

- Stage 1: 1 week
- Stage 2: 1 week
- Stage 3: 1 week
- Stage 4: 1 week
- Stage 5: 1 week
- Stage 6: 3 days
- Stage 7: 3 days
- Stage 8: 1 week
- Stage 9: 3 days
- Stage 10: 1 week

---

## Success Criteria

- All Trip CRUD operations functional with GHL sync
- All Contact CRUD operations functional with GHL sync
- Passengers can be enrolled and removed from trips
- Custom fields display and update correctly
- Stage progression works for both pipelines
- No data loss or inconsistencies between systems
- UI is responsive and intuitive
- Error handling is robust