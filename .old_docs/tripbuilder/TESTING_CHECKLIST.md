# Testing Checklist - Stage 1 + 2A

Use this checklist to verify everything is working correctly.

---

## Pre-Testing Setup

### 1. Environment Configuration
```bash
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder
cat .env
```

**Verify**:
- [ ] `GHL_API_TOKEN` is set to your actual token
- [ ] `GHL_LOCATION_ID` is set to your actual location ID
- [ ] `DATABASE_URL` is set (sqlite:///tripbuilder.db is fine)
- [ ] `SECRET_KEY` is set (any string)

### 2. Virtual Environment
```bash
source venv/bin/activate
pip list | grep -E "Flask|requests|SQLAlchemy"
```

**Verify**:
- [ ] Flask installed
- [ ] Flask-SQLAlchemy installed
- [ ] requests installed

### 3. Database Migration (if needed)
```bash
# If you have existing database with trips
ls tripbuilder.db
sqlite3 tripbuilder.db < migration_add_trip_name.sql

# OR start fresh
rm tripbuilder.db
flask init-db
```

**Verify**:
- [ ] Command runs without errors
- [ ] See "✅ Database tables created successfully!"

---

## Stage 1 Testing: Trip Name Field

### Test 1: Create New Trip
```bash
python app.py
# Visit http://localhost:5269/trips/new
```

**Steps**:
1. Fill in "Trip Name": `"Test Family Summer 2025"`
2. Fill in "Destination": `"Test Destination"`
3. Set dates (start < end)
4. Set capacity: `10`
5. Add notes (optional)
6. Click "Create Trip"

**Verify**:
- [ ] Form shows "Trip Name" field at the top
- [ ] Form has helpful placeholder text
- [ ] Form submission works
- [ ] Success message appears
- [ ] Redirects to trip list

### Test 2: View Trip List
```bash
# Visit http://localhost:5269/trips
```

**Verify**:
- [ ] Trip card shows name as header ("Test Family Summer 2025")
- [ ] Card shows destination, dates, capacity
- [ ] Progress bar displays correctly
- [ ] "View Details" and "Enroll Passenger" buttons work

### Test 3: View Trip Detail
```bash
# Click "View Details" on a trip
```

**Verify**:
- [ ] Trip name displays prominently at top
- [ ] All trip information shows correctly
- [ ] Capacity progress bar displays
- [ ] Statistics card shows correct values
- [ ] Quick actions sidebar present

### Test 4: Edit Trip
```bash
# Click "Edit Trip" button
```

**Verify**:
- [ ] Form pre-fills with current values (including name)
- [ ] Can change name
- [ ] Changes save correctly
- [ ] Success message appears
- [ ] Trip detail page reflects changes

### Test 5: Delete Trip
```bash
# Click "Delete Trip" in danger zone
```

**Verify**:
- [ ] Confirmation dialog appears
- [ ] Trip deletes successfully
- [ ] Redirects to trip list
- [ ] Trip no longer appears in list

---

## Stage 2A Testing: GHL Sync

### Test 6: Run Full Sync
```bash
flask sync-ghl
```

**Verify**:
- [ ] Command runs without errors
- [ ] See "🔄 Starting full GHL sync..."
- [ ] See "1️⃣ Syncing Pipelines & Stages..."
- [ ] See "✅ Synced X pipelines, Y stages"
- [ ] See "2️⃣ Syncing Custom Fields..."
- [ ] See "✅ Synced X field groups, Y custom fields"
- [ ] See "3️⃣ Syncing Contacts..."
- [ ] See batch progress messages
- [ ] See "✅ Total contacts synced: X"
- [ ] See final summary with all counts
- [ ] Command completes successfully

**Expected counts**:
- Pipelines: 2
- Stages: 11
- Custom Field Groups: 13
- Custom Fields: 100+
- Contacts: Varies (your actual count)

### Test 7: Verify Database - Pipelines
```bash
sqlite3 tripbuilder.db "SELECT * FROM pipelines;"
```

**Verify**:
- [ ] See 2 rows
- [ ] One row has ID: `IlWdPtOpcczLpgsde2KF` (TripBooking)
- [ ] One row has ID: `fnsdpRtY9o83Vr4z15bE` (Passenger)

### Test 8: Verify Database - Stages
```bash
sqlite3 tripbuilder.db "SELECT COUNT(*) FROM pipeline_stages;"
sqlite3 tripbuilder.db "SELECT name, position FROM pipeline_stages WHERE pipeline_id='IlWdPtOpcczLpgsde2KF' ORDER BY position;"
```

**Verify**:
- [ ] Total count is 11
- [ ] TripBooking pipeline has multiple stages
- [ ] Stages have position numbers
- [ ] Stage names make sense

### Test 9: Verify Database - Custom Fields
```bash
sqlite3 tripbuilder.db "SELECT COUNT(*) FROM custom_field_groups;"
sqlite3 tripbuilder.db "SELECT COUNT(*) FROM custom_fields;"
sqlite3 tripbuilder.db "SELECT name FROM custom_field_groups LIMIT 5;"
```

**Verify**:
- [ ] 13 custom field groups
- [ ] 100+ custom fields
- [ ] Group names like "Personal Details", "Passport Information", etc.

### Test 10: Verify Database - Contacts
```bash
sqlite3 tripbuilder.db "SELECT COUNT(*) FROM contacts;"
sqlite3 tripbuilder.db "SELECT firstname, lastname, email FROM contacts LIMIT 5;"
```

**Verify**:
- [ ] Contact count matches your GHL location
- [ ] Contacts have names and emails
- [ ] Data looks correct

### Test 11: Verify Database - Sync Log
```bash
sqlite3 tripbuilder.db "SELECT sync_type, status, records_synced, started_at FROM sync_logs ORDER BY started_at DESC LIMIT 1;"
```

**Verify**:
- [ ] One row with sync_type = 'full'
- [ ] Status = 'success'
- [ ] records_synced > 0
- [ ] started_at has recent timestamp

### Test 12: View Contacts in Web App
```bash
# Visit http://localhost:5269/contacts
```

**Verify**:
- [ ] Page loads successfully
- [ ] All contacts display in table
- [ ] Names, emails, phones show correctly
- [ ] Tags display (if any)
- [ ] "View" buttons present

### Test 13: Re-run Sync (Idempotency Test)
```bash
flask sync-ghl
```

**Verify**:
- [ ] Command runs without errors
- [ ] Same counts as before (or higher if new contacts added to GHL)
- [ ] No duplicate records created
- [ ] New sync log entry created

### Test 14: Enroll Passenger (Smart Contact Handling)
```bash
# Visit http://localhost:5269/trips (pick a trip)
# Click "Enroll Passenger"
```

**Test Case A - Existing Contact**:
1. Enter email of a contact that exists in the database
2. Fill other fields
3. Submit

**Verify**:
- [ ] Passenger enrolls successfully
- [ ] No duplicate contact created
- [ ] Success message shows contact name

**Test Case B - New Contact**:
1. Enter email that doesn't exist in database or GHL
2. Fill all required fields
3. Submit

**Verify**:
- [ ] Contact created in GHL
- [ ] Contact synced to local database
- [ ] Passenger enrolled successfully
- [ ] Success message appears

---

## Dashboard Testing

### Test 15: Dashboard Stats
```bash
# Visit http://localhost:5269/
```

**Verify**:
- [ ] Trip count is correct
- [ ] Contact count matches synced contacts
- [ ] Passenger count is correct
- [ ] Cards display properly
- [ ] Links work to each list page

---

## Error Handling Testing

### Test 16: Invalid GHL Credentials
```bash
# Edit .env with invalid token
echo "GHL_API_TOKEN=invalid_token" >> .env
flask sync-ghl
```

**Verify**:
- [ ] Error message appears
- [ ] Sync fails gracefully
- [ ] No partial data saved
- [ ] Sync log shows 'failed' status

**Cleanup**:
```bash
# Restore correct token in .env
```

### Test 17: Network Issues (Optional)
```bash
# Disconnect internet
flask sync-ghl
```

**Verify**:
- [ ] Appropriate error message
- [ ] No database corruption
- [ ] Sync log records failure

---

## Performance Testing

### Test 18: Large Contact Sync
```bash
# If you have 100+ contacts in GHL
flask sync-ghl
```

**Verify**:
- [ ] Batch progress messages appear
- [ ] Each batch shows count (100 per batch)
- [ ] Total is correct
- [ ] Completes in reasonable time

---

## Final Verification

### Test 19: Complete Workflow
```bash
# Start fresh
rm tripbuilder.db
flask init-db
flask sync-ghl
python app.py
```

**Steps**:
1. Visit dashboard
2. Create new trip with name
3. Enroll passenger (use existing contact)
4. Enroll another passenger (new contact)
5. View trip detail
6. Edit trip name
7. View contact list

**Verify**:
- [ ] Every step works smoothly
- [ ] No errors in console
- [ ] Data persists correctly
- [ ] UI updates properly

---

## Checklist Summary

### Stage 1 - Trip Names (5 tests)
- [ ] Test 1: Create new trip
- [ ] Test 2: View trip list
- [ ] Test 3: View trip detail
- [ ] Test 4: Edit trip
- [ ] Test 5: Delete trip

### Stage 2A - GHL Sync (13 tests)
- [ ] Test 6: Run full sync
- [ ] Test 7: Verify pipelines
- [ ] Test 8: Verify stages
- [ ] Test 9: Verify custom fields
- [ ] Test 10: Verify contacts
- [ ] Test 11: Verify sync log
- [ ] Test 12: View contacts in web
- [ ] Test 13: Re-run sync
- [ ] Test 14: Enroll passenger (smart contact)
- [ ] Test 15: Dashboard stats
- [ ] Test 16: Invalid credentials
- [ ] Test 17: Network issues
- [ ] Test 18: Large contact sync

### Integration (1 test)
- [ ] Test 19: Complete workflow

---

## All Tests Passed? ✅

**If yes**: Congratulations! Stage 1 and Stage 2A are fully functional!

**If no**: Review error messages and check:
1. Environment variables in `.env`
2. Database file exists
3. All files are in correct locations
4. Virtual environment is activated
5. Dependencies are installed

---

## Next Steps

Once all tests pass:
1. Commit your changes to git
2. Document any custom configurations
3. Proceed to Stage 2B implementation

**Stage 2B Goal**: Trip → TripBooking Opportunity Creation

When you create a trip in the app, it should automatically create a TripBooking opportunity in GoHighLevel!

---

**Testing Complete!** 🎉
