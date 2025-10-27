# TripBuilder - Features & Functionality

## Core Features

### 1. Trip Management
**Objective**: Manage backend Trip records and sync with GHL TripBooking opportunities

#### Features:
- **Trip List View**: Display all trips with key details (destination, dates, passenger count, status)
- **Create Trip**: Form to create new trip with destination, dates, capacity, notes
- **Edit Trip**: Modify trip details
- **Delete Trip**: Remove trip and associated opportunities (with confirmation)
- **Trip Detail View**: Comprehensive trip page showing:
  - Trip information (editable)
  - Associated TripBooking opportunity with current stage
  - List of all passengers enrolled
  - Option to add passengers
  - Custom field values for trip-level data

#### GHL Integration:
- Auto-create TripBooking opportunity when Trip is created
- Initialize at "FormSubmit" stage
- Sync trip changes to opportunity
- Store GHL opportunity ID in Trip record

---

### 2. Contact Management
**Objective**: Sync and manage GHL contacts within TripBuilder interface

#### Features:
- **Contact List View**: Display all contacts from GHL with search/filter
- **Contact Detail View**: Show contact information and all associated trips
- **Create Contact**: Form to add new contact to GHL
- **Edit Contact**: Update contact details
- **Delete Contact**: Remove contact from GHL (with cascade considerations)
- **Contact-Trip Association**: View which trips a contact is enrolled in

#### GHL Integration:
- Pull contacts from GHL via Search API
- Create/update/delete contacts via GHL API
- Cache contact data locally for performance
- Periodic sync to keep local data current

---

### 3. Passenger Enrollment (Core Feature)
**Objective**: Link Contacts to Trips via Passenger opportunities

#### Features:
- **Add Passenger to Trip**: 
  - Select from existing contacts or create new
  - Create Passenger opportunity in GHL
  - Initialize at "AddedToTrip" stage
  - Link passenger to trip in backend
- **Remove Passenger from Trip**: Unlink and optionally delete opportunity
- **View Passengers by Trip**: List all passengers for a given trip
- **View Trips by Contact**: List all trips for a given contact

#### GHL Integration:
- Create Passenger opportunity with:
  - `contact_id`: Linked contact
  - `pipeline_id`: Passenger pipeline ID
  - `stage_id`: Initial stage (AddedToTrip)
  - Custom field to link to backend Trip ID
- Store Passenger opportunity ID in backend

---

### 4. Pipeline Stage Management
**Objective**: Move opportunities through workflow stages

#### Features:
- **Visual Stage Indicators**: Display current stage for each opportunity
- **Stage Progression Buttons**: One-click buttons to advance to next stage
- **Stage History**: Track when opportunities moved through stages
- **Batch Stage Updates**: Move multiple passengers to same stage simultaneously

#### TripBooking Stages:
1. FormSubmit → 2. TripFinalized → 3. TravelersAdded → 4. TripScheduled → 5. TripComplete

#### Passenger Stages:
1. AddedToTrip → 2. DetailsSubmitted → 3. TripDetailsSent → 4. TripReady → 5. TripInProgress → 6. TripComplete

#### GHL Integration:
- Update opportunity stage via `opportunities.update_stage(opp_id, stage_id)`
- Validate stage transitions
- Log stage changes

---

### 5. Custom Field Data Entry
**Objective**: Capture extensive passenger and trip details via GHL custom fields

#### Features:
- **Dynamic Forms**: Generate forms based on custom field definitions
- **Field Grouping**: Organize fields by custom field groups (Passport Info, Health Details, etc.)
- **Data Type Support**:
  - Text (single line)
  - Large Text (textarea)
  - Single Option (dropdown)
  - Multiple Options (checkboxes)
  - File Upload
  - Date/DateTime
- **Field Validation**: Required fields, format validation, option constraints
- **Bulk Field Updates**: Update multiple fields in one transaction

#### Custom Field Groups (Passenger Pipeline):
- Room Info
- Passport Info
- Health Details
- Emergency Contact
- Legal
- Files (reservations, MOU, affidavit)

#### Custom Field Groups (TripBooking Pipeline):
- Opportunity Details
- Vendor Info
- Trip Details
- Internal

#### GHL Integration:
- Fetch field definitions from GHL
- Update field values via `opportunities.upsert_custom_field()`
- Validate against field constraints

---

### 6. Dual-View Interface
**Objective**: Provide both trip-centric and contact-centric perspectives

#### Trip-Centric View:
- Focus: "For this trip, who are the passengers and what's their status?"
- Entry point: Trip list → Trip detail
- Shows: All passengers, their stages, custom field completion status
- Actions: Add passengers, progress stages, update trip details

#### Contact-Centric View:
- Focus: "For this contact, what trips are they on and what's their status?"
- Entry point: Contact list → Contact detail
- Shows: All trips contact is enrolled in, their passenger stages
- Actions: Enroll in new trips, update contact info, complete passenger details

---

### 7. Tasks Integration
**Objective**: Manage follow-up tasks for contacts

#### Features:
- **View Tasks**: Display tasks for a contact
- **Create Task**: Add new task with title, due date, assignee
- **Complete Task**: Mark task as done
- **Delete Task**: Remove task
- **Task Filtering**: Filter by status (pending/completed)

#### GHL Integration:
- Tasks are GHL native feature tied to contacts
- Use wrapper methods: `tasks.create()`, `tasks.mark_complete()`, `tasks.delete()`

---

### 8. Sync & Data Integrity
**Objective**: Maintain consistency between backend DB and GHL CRM

#### Features:
- **Bi-directional Sync**: Changes in either system reflected in the other
- **Conflict Resolution**: Handle cases where data differs between systems
- **Orphan Detection**: Identify opportunities without backend Trip records
- **Manual Sync Trigger**: Button to force full sync
- **Sync Status Indicators**: Show when last sync occurred, any errors

#### Sync Operations:
- **Trip → TripBooking Opportunity**: On trip create/update
- **Passenger Link → Passenger Opportunity**: On passenger enrollment
- **Contact Changes**: Pull from GHL periodically or on-demand
- **Custom Field Updates**: Push to GHL immediately or batch

---

### 9. Reporting & Analytics
**Objective**: Provide insights into trips and passengers

#### Features:
- **Trip Dashboard**: Overview of all trips, passengers, completion rates
- **Stage Funnel**: Visualize how many opportunities are in each stage
- **Passenger Status Report**: List passengers by stage
- **Incomplete Details Report**: Identify passengers with missing custom fields
- **Trip Capacity Tracking**: Show available spots per trip

---

### 10. User Experience Features

#### Navigation:
- Top navbar with links: Trips, Contacts, Dashboard
- Breadcrumbs for context
- Search bars on list views

#### Feedback:
- Flash messages for success/error/info
- Confirmation modals for destructive actions
- Loading indicators for API calls
- Inline validation on forms

#### Responsive Design:
- Mobile-friendly layouts
- Collapsible sections for dense information
- Touch-friendly buttons and forms

#### Accessibility:
- Semantic HTML
- ARIA labels
- Keyboard navigation support

---

## User Workflows

### Workflow 1: Create Trip and Add Passengers
1. Navigate to Trip list
2. Click "New Trip"
3. Fill trip form (destination, dates)
4. Submit → Trip created, TripBooking opportunity auto-created at "FormSubmit"
5. On Trip detail page, click "Add Passenger"
6. Search and select existing contact OR create new contact
7. Click "Add" → Passenger opportunity created at "AddedToTrip"
8. Repeat for additional passengers
9. Progress TripBooking to "TravelersAdded" stage

### Workflow 2: Collect Passenger Details
1. From Trip detail, click on passenger name
2. View Passenger detail page with custom field groups
3. Expand "Passport Info" section
4. Fill passport fields (number, expiry, nationality)
5. Save fields → Values pushed to GHL
6. Repeat for other groups (Health Details, Emergency Contact)
7. Once all required fields completed, progress Passenger to "DetailsSubmitted"

### Workflow 3: Finalize Trip
1. Verify all passengers at "TripReady" or later stage
2. Progress TripBooking to "TripScheduled"
3. Update trip custom fields (vendor info, itinerary)
4. Send confirmation tasks to all passengers
5. As trip occurs, progress passengers to "TripInProgress"
6. After trip, progress all to "TripComplete"
7. Progress TripBooking to "TripComplete"

---

## Security Features
- User authentication via Flask-Login
- Role-based access (admin vs. standard user)
- Secure API token storage in environment
- Input validation and sanitization
- CSRF protection on forms
- Confirm before deletions

---

## Future Enhancements
- Email notifications for stage changes
- Document upload to GHL files
- Automated stage progression based on rules
- Integration with payment processing
- Calendar view of trips
- Export reports to CSV/PDF