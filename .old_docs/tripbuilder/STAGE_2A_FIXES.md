# Stage 2A Fixes Applied

## Issues Fixed

### 1. Missing `locationId` Parameter in `get_pipelines()`
**Problem**: API endpoint required locationId parameter but it wasn't being passed.

**Error**: `locationId can't be undefined`

**Fix**: Updated `ghl_api.py` line ~265:
```python
def get_pipelines(self) -> Dict:
    params = {"locationId": self.location_id}
    return self._make_request("GET", "opportunities/pipelines", params=params)
```

### 2. Custom Fields Primary Key Type Mismatch
**Problem**: Sync code was trying to use GHL string IDs as primary keys, but the model uses auto-increment integers.

**Error**: `invalid input syntax for type integer: "JCuGgaYNZJqH1SR2d9L7"`

**Fix**: Updated `services/ghl_sync.py` to query by `ghl_field_id` instead:
```python
field = CustomField.query.filter_by(ghl_field_id=field_id).first() or CustomField()
field.ghl_field_id = field_id
field.field_key = field_data.get('fieldKey', '')
# ... etc
```

### 3. Contact Pagination with Wrong Parameters
**Problem**: Used `offset` parameter which GHL API doesn't accept. Also used wrong pagination metadata.

**Error**: `['property offset should not exist']`

**Fix**: Updated `services/ghl_sync.py` to use proper GHL pagination:
```python
# Use startAfterId for pagination
params = {'limit': limit}
if start_after_id:
    params['startAfterId'] = start_after_id

# Check pagination from meta
meta = response.get('meta', {})
next_start_after_id = meta.get('nextStartAfterId')
```

## Test Results

✅ **Working**: `flask sync-ghl`

```
🔄 Starting full GHL sync...
============================================================

1️⃣  Syncing Pipelines & Stages...
📊 Syncing pipelines...
   ✅ Synced 2 pipelines, 11 stages

2️⃣  Syncing Custom Fields...
🔧 Syncing custom fields...
   ✅ Synced 0 field groups, 53 custom fields

3️⃣  Syncing Contacts...
👥 Syncing contacts...
   📦 Synced batch: 100 contacts (total: 100)
   ✅ Total contacts synced: 100

============================================================
✅ Sync complete!
   Pipelines: 2
   Stages: 11
   Custom Field Groups: 0
   Custom Fields: 53
   Contacts: 100
   Total Records: 166
```

## Files Modified

1. `/Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder/ghl_api.py`
   - Added locationId parameter to get_pipelines()

2. `/Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder/services/ghl_sync.py`
   - Fixed custom field sync to use ghl_field_id
   - Fixed contact pagination to use GHL's startAfterId pattern
   - Updated metadata checking for pagination

## Database State After Sync

- **Pipelines**: 2 rows
- **Pipeline Stages**: 11 rows  
- **Custom Fields**: 53 rows
- **Custom Field Groups**: 0 rows (GHL didn't return group data, which is expected)
- **Contacts**: 100 rows (or more if you have more contacts)

## Stage 2A Status

✅ **COMPLETE** - GHL data synchronization is fully functional!

## Next: Verify Data

Check your PostgreSQL database:

```bash
psql -U ridiculaptop -d tripbuilder

-- View pipelines
SELECT * FROM pipelines;

-- View stages
SELECT name, position FROM pipeline_stages ORDER BY pipeline_id, position;

-- Count custom fields
SELECT COUNT(*) FROM custom_fields;

-- View sample contacts
SELECT firstname, lastname, email FROM contacts LIMIT 5;

-- Check sync log
SELECT * FROM sync_logs ORDER BY started_at DESC LIMIT 1;
```

## Ready for Stage 2B!

Now that data sync is working, we can proceed to Stage 2B: Trip → TripBooking Opportunity Creation.
