# Quick Start: Link Passengers to Trips

## Overview
This process links passenger opportunities to trip opportunities using the trip_name custom field (ID: tJoung7L6ymp1vHmU2Tq).

## 🚀 Quick Start (3 Steps)

### Step 1: Run Pre-Flight Check
```bash
python3 preflight_check.py
```
This checks:
- ✅ Environment variables are set
- ✅ Raw JSON file exists
- ✅ Database schema is ready
- ✅ Database has data

### Step 2: Run Migration (if needed)
```bash
python3 migrate_add_trip_columns.py
```
This adds:
- `trips.name` column
- `passengers.trip_name` column
- `field_maps` table

### Step 3: Run Linking Script
```bash
python3 link_passengers_from_raw_json.py
```
This will:
1. ✅ Extract trip_name from raw JSON
2. ✅ Update passenger records
3. ✅ Sync trip names to GHL dropdown
4. ✅ Link passengers to trips

## 📁 Required File Location

The script expects passenger data at:
```
~/Downloads/claude_code_tripbuilder/tripbuilder/raw_ghl_responses/passengers_raw.json
```

**To get this file:**
1. Export passengers from GoHighLevel as JSON
2. Save to the path above
3. OR update line 62-64 in `link_passengers_from_raw_json.py` with your path

## 🔧 What Each Script Does

### `preflight_check.py`
- Verifies environment setup
- Checks if raw JSON exists
- Validates database schema
- Reports database statistics

### `migrate_add_trip_columns.py`
- Adds `name` to trips table
- Adds `trip_name` to passengers table
- Makes `trip_id` nullable
- Creates `field_maps` table

### `link_passengers_from_raw_json.py`
- Reads raw JSON with ALL passenger data
- Extracts trip_name using correct field naming (fieldValueString, etc.)
- Updates passenger records with trip_name
- Ensures GHL dropdown has all trip names
- Links passengers to trips by matching names

## 💡 Key Features

### Smart Field Value Extraction
Handles GHL's field naming convention:
- STRING → `fieldValueString`
- NUMBER → `fieldValueNumber`
- DATE → `fieldValueDate`
- etc.

### Flexible Matching
Three-tier matching strategy:
1. Exact match
2. Case-insensitive match
3. Partial match (substring)

### GHL Dropdown Sync
Automatically updates the `opportunity.trip_name` dropdown in GoHighLevel with any trip names that are missing.

## 📊 Expected Output

```
════════════════════════════════════════════════════════════════════
          PASSENGER-TRIP LINKING FROM RAW JSON
════════════════════════════════════════════════════════════════════

STEP 1: Extract Trip Names from Raw JSON
════════════════════════════════════════════════════════════════════
📂 Reading file: ~/Downloads/.../passengers_raw.json
   Loaded 150 passenger records

✅ Extracted trip names:
   Passengers with trip_name: 145
   Passengers without trip_name: 5

STEP 2: Update Database with Trip Names
════════════════════════════════════════════════════════════════════
✅ Results:
   Updated: 145 passengers
   Already had trip_name: 0 passengers
   Not found in DB: 0 passengers

STEP 3: Ensure Field Mapping
════════════════════════════════════════════════════════════════════
✅ Field mapping exists: opportunity.trip_name -> passengers.trip_name

STEP 4: Sync Trip Names to GHL Dropdown
════════════════════════════════════════════════════════════════════
📊 Found 12 unique trip names in database
🔍 Fetching custom field definition from GHL...
✅ Found field: Trip Name
   Data Type: SINGLE_OPTIONS

📋 Current dropdown has 10 options
⚠️  Found 2 missing trip names
   - Alaska Adventure 2025
   - Iceland Explorer 2025

🔄 Updating GHL dropdown with 12 total options...
✅ Successfully updated GHL dropdown!
   Added 2 new options

STEP 5: Link Passengers to Trips
════════════════════════════════════════════════════════════════════
📊 Database Status:
   Total Passengers: 150
   Without trip_id: 150
   With trip_name: 145

📚 Building trip lookup tables...
   Loaded 12 trips

🔗 Linking passengers...
   ✅ Linked 100...
   ✅ Linked 145...

════════════════════════════════════════════════════════════════════
RESULTS
════════════════════════════════════════════════════════════════════
✅ Linked: 145
⚠️  No match: 0

📊 Final Status:
   With trip_id: 145
   Without trip_id: 5
   Success Rate: 96.7%

════════════════════════════════════════════════════════════════════
                    ALL STEPS COMPLETE!
════════════════════════════════════════════════════════════════════
```

## 🐛 Troubleshooting

### "File not found: passengers_raw.json"
- Export passenger data from GHL
- Save to the expected path
- OR update the path in the script

### "Column already exists" errors during migration
- The migration script is safe to re-run
- It checks if columns exist before adding them

### Some passengers don't link
- Check the "unmatched trip names" in the output
- Verify trip names in database match those in passenger records
- The script tries exact, case-insensitive, and partial matches

### GHL API errors
- Check your `GHL_API_TOKEN` and `GHL_LOCATION_ID`
- Verify API permissions include custom field management
- Check rate limits (script includes proper error handling)

## 📚 Related Files

- `models.py` - Updated with new columns
- `TRIP_LINKING_RESUME.md` - Detailed documentation
- `build_field_maps.py` - Populates field_maps table (optional)

## 🎯 Success Criteria

✅ All passengers have trip_name from raw JSON
✅ GHL dropdown includes all trip names
✅ Passengers linked to trips (high success rate)
✅ Field mapping exists in database

## 🔄 Re-Running

The scripts are safe to re-run:
- Migration script checks if columns exist
- Linking script won't duplicate work
- Updates are idempotent

## 📞 Support

Check these docs for more info:
- `TRIP_LINKING_RESUME.md` - Detailed technical documentation
- `IMPLEMENTATION_PLAN_V2.md` - Overall project architecture
- `SYNC_TROUBLESHOOTING.md` - Common sync issues
