# Sync Troubleshooting Guide

Quick reference for debugging common issues with the GHL sync.

---

## Quick Checks

Before troubleshooting, verify basics:

```bash
cd ~/Downloads/claude_code_tripbuilder/tripbuilder
source ../.venv/bin/activate

# 1. Check environment variables
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('GHL_API_TOKEN:', 'SET' if os.getenv('GHL_API_TOKEN') else 'MISSING'); print('GHL_LOCATION_ID:', 'SET' if os.getenv('GHL_LOCATION_ID') else 'MISSING')"

# 2. Test database connection
psql -U ridiculaptop -d tripbuilder -c "SELECT 1;"

# 3. Check tables exist
psql -U ridiculaptop -d tripbuilder -c "\dt"
```

---

## Common Issues

### Issue 1: "Module not found: field_mapping"

**Symptoms:**
```
ImportError: No module named 'field_mapping'
```

**Cause:** Import path issue or file not in correct location

**Fix:**
```bash
# Verify file exists
ls -la field_mapping.py

# Should be in same directory as ghl_sync.py
pwd
# Should show: /Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder
```

**If file is missing:**
The file should have been created in Stage 2A. If it's missing, you need to recreate it.

---

### Issue 2: "Column does not exist"

**Symptoms:**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column "arrival_date" does not exist
```

**Cause:** Database schema not updated with new columns

**Fix:**
```bash
# Recreate database with new schema
python3 recreate_db.py

# Or run migrations
flask db upgrade
```

**Verify columns exist:**
```sql
-- Check Trip columns
\d trips

-- Should show arrival_date, return_date, max_passengers, etc.

-- Check Passenger columns  
\d passengers

-- Should show passport_number, health_state, etc.
```

---

### Issue 3: "API key invalid" or "401 Unauthorized"

**Symptoms:**
```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Cause:** Invalid or expired API token

**Fix:**
```bash
# 1. Check .env file
cat .env | grep GHL_API_TOKEN

# 2. Verify token in GHL dashboard
# Go to: Settings > Integrations > API Keys

# 3. Update token if needed
# Edit .env file and replace GHL_API_TOKEN value

# 4. Restart Flask app
flask sync-ghl
```

---

### Issue 4: Sync hangs or times out

**Symptoms:**
- Sync starts but never completes
- Process seems stuck on one page
- No output for several minutes

**Possible Causes:**
1. Network issues
2. GHL API rate limiting
3. Large dataset causing timeout

**Fix:**

**A) Check if process is still running:**
```bash
# In another terminal
ps aux | grep flask
```

**B) Try with smaller page size:**
```python
# In ghl_sync.py, modify sync methods:
def sync_trip_opportunities(self, limit=20):  # Reduced from 100
    ...

def sync_passenger_opportunities(self, limit=20):  # Reduced from 100
    ...
```

**C) Add timeout handling:**
```python
# In ghl_sync.py, add to API calls:
try:
    response = self.api.search_opportunities(
        pipeline_id=TRIPBOOKING_PIPELINE_ID,
        limit=limit,
        page=page,
        timeout=30  # Add timeout
    )
except requests.exceptions.Timeout:
    print(f"   ⚠️  Timeout on page {page}, retrying...")
    continue
```

---

### Issue 5: "Too many values to unpack"

**Symptoms:**
```
ValueError: too many values to unpack (expected 2)
```

**Cause:** GHL API response format changed or unexpected data structure

**Fix:**

**Add debug output to see what's being returned:**
```python
# In ghl_sync.py, add before parsing:
print(f"DEBUG: custom_fields_list = {custom_fields_list[:3]}")  # First 3 items
```

**Check if custom fields format is correct:**
```python
# Expected format:
[
    {"id": "field_id_1", "fieldValue": "value1"},
    {"id": "field_id_2", "fieldValue": "value2"}
]

# If format is different, update parse_ghl_custom_fields()
```

---

### Issue 6: Data not appearing in database

**Symptoms:**
- Sync completes successfully
- Shows "X trips synced"
- But `SELECT COUNT(*) FROM trips` returns 0

**Cause:** Transaction not committed or exception during commit

**Fix:**

**A) Check for errors during commit:**
```python
# Add explicit error handling:
try:
    db.session.commit()
    print(f"   ✅ Committed {trip_count} trips")
except Exception as e:
    print(f"   ❌ Commit failed: {e}")
    db.session.rollback()
    raise
```

**B) Check database directly:**
```sql
-- See if data exists
SELECT COUNT(*) FROM trips;
SELECT COUNT(*) FROM passengers;

-- Check last sync time
SELECT * FROM sync_log ORDER BY started_at DESC LIMIT 1;
```

**C) Manual commit test:**
```python
# In Flask shell
flask shell

>>> from models import db, Trip
>>> trips = Trip.query.all()
>>> print(len(trips))
>>> # If 0, check database connection
```

---

### Issue 7: Type conversion errors

**Symptoms:**
```
ValueError: time data '2025-03-15' does not match format '%Y-%m-%dT%H:%M:%S.%fZ'
```

**Cause:** Date format from GHL doesn't match expected format

**Fix:**

**Update date parsing in field_mapping.py:**
```python
def map_trip_custom_fields(custom_fields: Dict[str, Any]) -> Dict[str, Any]:
    # ...
    if column_name in ['arrival_date', 'return_date', 'deposit_date', 'final_payment']:
        try:
            if isinstance(value, str):
                # Try multiple formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d', '%Y/%m/%d']:
                    try:
                        mapped[column_name] = datetime.strptime(value, fmt).date()
                        break
                    except:
                        continue
        except:
            print(f"   ⚠️  Failed to parse date: {value}")
```

---

### Issue 8: Duplicate records

**Symptoms:**
- Running sync multiple times creates duplicate trips/passengers
- Same trip appears multiple times

**Cause:** Upsert logic not working (matching key not found)

**Check:**
```sql
-- Find duplicates
SELECT ghl_opportunity_id, COUNT(*) 
FROM trips 
GROUP BY ghl_opportunity_id 
HAVING COUNT(*) > 1;
```

**Fix:**

**Ensure ghl_opportunity_id is being set:**
```python
# In sync_trip_opportunities:
trip = Trip.query.filter_by(ghl_opportunity_id=opp_id).first()
if not trip:
    trip = Trip()
trip.ghl_opportunity_id = opp_id  # Make sure this is set!
```

**Remove duplicates manually:**
```sql
-- Keep only the most recent of each duplicate
DELETE FROM trips a USING trips b
WHERE a.id > b.id 
AND a.ghl_opportunity_id = b.ghl_opportunity_id;
```

---

### Issue 9: Passenger-Trip linking fails

**Symptoms:**
- Passengers sync successfully
- But `passenger.trip_id` is NULL for most records

**Cause:** Trip name in custom field doesn't match trip name in database

**Diagnose:**
```sql
-- See what trip names passengers reference
SELECT DISTINCT trip_name, COUNT(*) 
FROM (
    SELECT 
        p.id,
        cf.field_value as trip_name
    FROM passengers p
    JOIN opportunities o ON o.id = p.id
    JOIN custom_fields cf ON cf.opportunity_id = o.id
    WHERE cf.field_key = 'opportunity.tripname'
) subq
GROUP BY trip_name;

-- Compare with actual trip names
SELECT name FROM trips ORDER BY name;
```

**Fix:**

**Option A: Manual linking script**
```python
# link_passengers.py
from app import app
from models import db, Trip, Passenger

with app.app_context():
    unlinked = Passenger.query.filter_by(trip_id=None).all()
    
    for passenger in unlinked:
        # Get trip name from custom fields
        trip_name = get_custom_field(passenger.id, 'opportunity.tripname')
        
        if trip_name:
            # Try exact match
            trip = Trip.query.filter_by(name=trip_name).first()
            
            # Try fuzzy match
            if not trip:
                trip = Trip.query.filter(Trip.name.ilike(f'%{trip_name}%')).first()
            
            if trip:
                passenger.trip_id = trip.id
                print(f"Linked {passenger.firstname} to {trip.name}")
    
    db.session.commit()
```

**Option B: Update sync to be more flexible**
```python
# In sync_passenger_opportunities:
trip_name = custom_fields_dict.get('opportunity.tripname')
if trip_name and not passenger.trip_id:
    # Try multiple matching strategies
    trip = (Trip.query.filter_by(name=trip_name).first() or
            Trip.query.filter(Trip.name.ilike(f'%{trip_name}%')).first() or
            Trip.query.filter(Trip.destination.ilike(f'%{trip_name}%')).first())
    
    if trip:
        passenger.trip_id = trip.id
```

---

### Issue 10: Custom field not syncing

**Symptoms:**
- Specific custom field always NULL in database
- Other fields sync fine

**Diagnose:**

**A) Check field exists in GHL:**
```sql
SELECT * FROM custom_fields 
WHERE field_key LIKE '%fieldname%';
```

**B) Check raw data from GHL:**
```python
# In Flask shell
flask shell

>>> from ghl_api import GoHighLevelAPI
>>> import os
>>> api = GoHighLevelAPI(os.getenv('GHL_LOCATION_ID'), os.getenv('GHL_API_TOKEN'))
>>> opps = api.search_opportunities(pipeline_id='IlWdPtOpcczLpgsde2KF', limit=1)
>>> print(opps['opportunities'][0]['customFields'])
```

**C) Check field mapping:**
```python
# In field_mapping.py
TRIP_FIELD_MAP = {
    'opportunity.fieldname': 'column_name',  # Make sure this exists
}
```

**Fix:**
- If field key is different in GHL, update TRIP_FIELD_MAP
- If field doesn't exist in GHL, add it in GHL dashboard
- If field type is wrong, update type conversion logic

---

## Debug Mode

To see detailed sync information:

```python
# In ghl_sync.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or add print statements:
```python
def sync_trip_opportunities(self, limit=100):
    # ...
    for opp_data in opportunities_data:
        print(f"\n=== Processing Opportunity {opp_data.get('id')} ===")
        print(f"Name: {opp_data.get('name')}")
        print(f"Custom Fields Count: {len(opp_data.get('customFields', []))}")
        
        custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
        print(f"Parsed Fields: {list(custom_fields_dict.keys())}")
        
        mapped_fields = map_trip_custom_fields(custom_fields_dict)
        print(f"Mapped Fields: {mapped_fields}")
```

---

## Performance Issues

If sync is too slow:

**1. Add indexes:**
```sql
CREATE INDEX idx_trips_ghl_id ON trips(ghl_opportunity_id);
CREATE INDEX idx_passengers_trip ON passengers(trip_id);
CREATE INDEX idx_passengers_contact ON passengers(contact_id);
```

**2. Reduce page size:**
```python
# Smaller pages commit more frequently
results['trips'] = self.sync_trip_opportunities(limit=50)  # Instead of 100
```

**3. Skip unchanged records:**
```python
# Check if opportunity was updated since last sync
if opp_data.get('dateUpdated') and trip.updated_at:
    opp_updated = datetime.fromisoformat(opp_data['dateUpdated'].replace('Z', '+00:00'))
    if opp_updated <= trip.updated_at:
        continue  # Skip unchanged
```

---

## Getting Help

If none of these solutions work:

1. **Check the sync log:**
```sql
SELECT * FROM sync_log ORDER BY started_at DESC LIMIT 5;
```

2. **Enable full error output:**
```python
try:
    results = sync_service.perform_full_sync()
except Exception as e:
    import traceback
    traceback.print_exc()
    raise
```

3. **Test individual components:**
```bash
# Test just pipelines
flask shell
>>> from ghl_sync import GHLSyncService
>>> from ghl_api import GoHighLevelAPI
>>> import os
>>> api = GoHighLevelAPI(os.getenv('GHL_LOCATION_ID'), os.getenv('GHL_API_TOKEN'))
>>> sync = GHLSyncService(api)
>>> sync.sync_pipelines()

# Test just one trip
>>> sync.sync_trip_opportunities(limit=1)
```

4. **Provide details when asking for help:**
- Exact error message
- Stack trace
- GHL API response (if relevant)
- Database state (record counts)
- Sync log entries

---

## Recovery Procedures

### Start Fresh
If everything is broken, start over:

```bash
# 1. Backup current database (just in case)
pg_dump -U ridiculaptop tripbuilder > backup_$(date +%Y%m%d).sql

# 2. Drop and recreate
python3 recreate_db.py

# 3. Run sync again
flask sync-ghl
```

### Partial Reset
Reset just trips or passengers:

```sql
-- Reset trips only
TRUNCATE TABLE trips CASCADE;

-- Reset passengers only  
TRUNCATE TABLE passengers CASCADE;

-- Reset everything except contacts
TRUNCATE TABLE trips CASCADE;
TRUNCATE TABLE passengers CASCADE;
TRUNCATE TABLE pipelines CASCADE;
TRUNCATE TABLE pipeline_stages CASCADE;
TRUNCATE TABLE custom_fields CASCADE;
TRUNCATE TABLE custom_field_groups CASCADE;
```

Then re-run sync:
```bash
flask sync-ghl
```

---

## Success Indicators

You know sync is working when:

✅ No errors in output
✅ Record counts match expectations:
   - 2 pipelines
   - 11 stages  
   - 53 custom fields
   - ~5,453 contacts
   - ~693 trips
   - ~6,477 passengers

✅ Data appears in database:
```sql
SELECT COUNT(*) FROM trips;        -- Should be ~693
SELECT COUNT(*) FROM passengers;    -- Should be ~6,477
```

✅ Fields are populated:
```sql
SELECT COUNT(*) FROM trips WHERE arrival_date IS NOT NULL;     -- Most trips
SELECT COUNT(*) FROM passengers WHERE passport_number IS NOT NULL;  -- Many passengers
```

✅ Some passengers are linked:
```sql
SELECT COUNT(*) FROM passengers WHERE trip_id IS NOT NULL;  -- Some percentage
```

---

**Last Updated:** Stage 2A Implementation
**File:** SYNC_TROUBLESHOOTING.md
