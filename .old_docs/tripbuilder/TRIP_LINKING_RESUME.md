# Trip-Passenger Linking - Resume Summary

## What Was Completed

### 1. Model Updates (models.py)
- ✅ Added `name` column to `Trip` model for linking passengers
- ✅ Added `trip_name` column to `Passenger` model (custom field ID: tJoung7L6ymp1vHmU2Tq)
- ✅ Made `trip_id` nullable in `Passenger` model (since we're linking after creation)
- ✅ Added `FieldMap` model for dynamic field mapping

### 2. Migration Script Created
- ✅ Created `migrate_add_trip_columns.py` to update database schema
- Adds columns safely (checks if they already exist)
- Creates field_maps table if needed

### 3. Existing Scripts Ready
- ✅ `link_passengers_from_raw_json.py` already exists with complete logic:
  - Extracts trip_name from raw JSON using correct field naming convention
  - Updates passenger records with trip_name
  - Ensures all trip names are in GHL dropdown  
  - Links passengers to trips by matching names

## Next Steps to Complete the Task

### Step 1: Run the Database Migration
```bash
cd /path/to/project
python3 migrate_add_trip_columns.py
```

### Step 2: Ensure Raw JSON File Exists
The script expects the file at:
```
~/Downloads/claude_code_tripbuilder/tripbuilder/raw_ghl_responses/passengers_raw.json
```

**If this file doesn't exist:**
- Create the directory structure
- Export passenger data from GoHighLevel and save it there
- OR update the path in line 62-64 of `link_passengers_from_raw_json.py`

### Step 3: Run the Linking Script
```bash
python3 link_passengers_from_raw_json.py
```

This will:
1. Extract trip_name from raw JSON (using fieldValueString/fieldValueNumber pattern)
2. Update passenger records with trip_name values
3. Check if all trip names exist in GHL dropdown for 'opportunity.trip_name'
4. Add missing trip names to the dropdown
5. Link passengers to trips by matching trip_name to trips.name

## Important Notes

### Custom Field Value Extraction
The script correctly handles GHL's field value naming convention:
- Type is capitalized and concatenated with "fieldValue"
- STRING → `fieldValueString`
- NUMBER → `fieldValueNumber`  
- DATE → `fieldValueDate`
- etc.

See `get_field_value_by_type()` function in the script (lines 28-49).

### Trip Name Matching
The linking logic uses multiple strategies:
1. Exact match
2. Case-insensitive match
3. Partial match (substring)

This provides flexibility in case there are minor differences in trip names.

### GHL Dropdown Update
The script will automatically update the GHL custom field dropdown to include any trip names that are in the database but not yet in the dropdown options.

## Files Modified/Created

1. `/mnt/project/models.py` - Updated with new columns and FieldMap model
2. `/mnt/project/migrate_add_trip_columns.py` - New migration script
3. `/mnt/project/link_passengers_from_raw_json.py` - Already existed, ready to use

## Troubleshooting

### If passengers_raw.json is missing:
You can export it from GoHighLevel or update the path in the script.

### If some passengers don't link:
Check the console output - the script shows:
- Passengers with trip_name
- Passengers without trip_name
- Unmatched trip names (couldn't find matching trip)

### If field mapping fails:
Run `build_field_maps.py` to populate the field_maps table with all custom field mappings.

## Database Schema Changes

### trips table
```sql
ALTER TABLE trips ADD COLUMN name VARCHAR(200);
```

### passengers table  
```sql
ALTER TABLE passengers ADD COLUMN trip_name VARCHAR(200);
ALTER TABLE passengers ALTER COLUMN trip_id DROP NOT NULL;
```

### field_maps table (new)
```sql
CREATE TABLE field_maps (
    id SERIAL PRIMARY KEY,
    ghl_key VARCHAR(100) UNIQUE NOT NULL,
    field_key VARCHAR(200) NOT NULL,
    table_column VARCHAR(100) NOT NULL,
    tablename VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL
);
```
