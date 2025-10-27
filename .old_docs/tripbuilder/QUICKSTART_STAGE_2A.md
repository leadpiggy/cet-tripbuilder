# Quick Start: Testing Stage 2A

## Prerequisites

1. **GHL Credentials**: You need your GoHighLevel API token and location ID
2. **Database**: Fresh database recommended for clean testing

---

## Setup Steps

### 1. Configure Environment
```bash
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder

# Copy environment template if not done already
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required variables**:
```env
GHL_API_TOKEN=your_actual_token_here
GHL_LOCATION_ID=your_actual_location_id_here
DATABASE_URL=sqlite:///tripbuilder.db
SECRET_KEY=any-random-string
```

### 2. Initialize Fresh Database
```bash
# Remove old database (if exists)
rm tripbuilder.db

# Create new database with all tables
flask init-db
```

**Expected output**:
```
✅ Database tables created successfully!
```

### 3. Apply Trip Name Migration
Since we added the `name` field to the Trip model:
```bash
# If you have existing trips, run migration
sqlite3 tripbuilder.db < migration_add_trip_name.sql

# Otherwise, the fresh database already has the name column
```

### 4. Run GHL Sync
```bash
flask sync-ghl
```

**Expected output** (example):
```
🔄 Starting full GHL sync...
============================================================

1️⃣  Syncing Pipelines & Stages...
📊 Syncing pipelines...
   ✅ Synced 2 pipelines, 11 stages

2️⃣  Syncing Custom Fields...
🔧 Syncing custom fields...
   ✅ Synced 13 field groups, 105 custom fields

3️⃣  Syncing Contacts...
👥 Syncing contacts...
   📦 Synced batch: 100 contacts (total: 100)
   ✅ Total contacts synced: 100

============================================================
✅ Sync complete!
   Pipelines: 2
   Stages: 11
   Custom Field Groups: 13
   Custom Fields: 105
   Contacts: 100
   Total Records: 231
```

---

## Verification

### Check Database
```bash
# See sync log
sqlite3 tripbuilder.db "SELECT * FROM sync_logs;"

# Count records
sqlite3 tripbuilder.db "
SELECT 
    'Pipelines: ' || (SELECT COUNT(*) FROM pipelines) ||
    ', Stages: ' || (SELECT COUNT(*) FROM pipeline_stages) ||
    ', Groups: ' || (SELECT COUNT(*) FROM custom_field_groups) ||
    ', Fields: ' || (SELECT COUNT(*) FROM custom_fields) ||
    ', Contacts: ' || (SELECT COUNT(*) FROM contacts) as Summary;
"

# View pipeline names
sqlite3 tripbuilder.db "SELECT id, name FROM pipelines;"

# View first 5 contacts
sqlite3 tripbuilder.db "SELECT firstname, lastname, email FROM contacts LIMIT 5;"
```

### Check Web Interface
```bash
# Start the application
python app.py
```

Then visit:
1. **Dashboard**: http://localhost:5269
2. **Contacts**: http://localhost:5269/contacts (should show all synced contacts)
3. **Trips**: http://localhost:5269/trips

---

## Common Issues

### Issue: "API authentication failed"
**Solution**: Check your `GHL_API_TOKEN` in `.env`

### Issue: "Location not found"
**Solution**: Verify `GHL_LOCATION_ID` in `.env`

### Issue: ImportError for GHLSyncService
**Solution**: Make sure you're in the project directory and `ghl_sync.py` exists

### Issue: No contacts synced
**Solution**: 
- Verify you have contacts in your GHL location
- Check that contacts are not filtered out by any settings
- Try running sync again

---

## Next: Create Your First Trip

Once sync is complete, test the full workflow:

1. **Create a trip**:
   ```
   Visit: http://localhost:5269/trips/new
   
   Fill in:
   - Trip Name: "Johnson Family Summer 2025"
   - Destination: "Hawaii"
   - Dates: June 1-8, 2025
   - Max Capacity: 10
   ```

2. **Enroll a passenger**:
   ```
   Click "Enroll Passenger" on the trip
   
   Fill in contact details:
   - Use an email from your synced contacts
   - OR enter new contact details
   ```

3. **View trip details**:
   ```
   See enrolled passengers
   Check capacity status
   View trip statistics
   ```

---

## Success! 🎉

You've completed Stage 1 and Stage 2A! Your app can now:
- ✅ Sync all GHL data (pipelines, custom fields, contacts)
- ✅ Create and manage trips with names
- ✅ Enroll passengers (creates contacts in GHL if needed)
- ✅ View comprehensive trip and contact information

**Ready for Stage 2B**: Trip → TripBooking Opportunity Creation
