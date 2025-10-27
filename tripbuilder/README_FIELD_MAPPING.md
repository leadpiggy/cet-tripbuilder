# CORRECT FIELD MAPPING APPROACH

## The Problem

The GHL field keys in the API have UNDERSCORES (e.g., `opportunity.passport_file`), but the documentation sometimes shows them without underscores. This caused mapping errors.

## The Solution

Use a database-driven approach with the `field_maps` table to dynamically map between:
- GHL custom field IDs (the actual ID like `cScyx9WMk8apxXU0rMZX`)
- Database column names (like `passport_file`)
- Data types (for proper conversion)

## Workflow

### Step 1: Fetch RAW GHL Data

```bash
cd ~/Downloads/claude_code_tripbuilder/tripbuilder
source ../.venv/bin/activate
python raw_ghl_sync.py
```

This saves RAW (unconverted) responses to `raw_ghl_responses/`:
- `contacts_raw.json` - All contacts as GHL returns them
- `trips_raw.json` - All trip opportunities as GHL returns them
- `passengers_raw.json` - All passenger opportunities as GHL returns them
- `custom_fields_raw.json` - All custom field definitions
- `sync_summary.json` - Summary counts

**Why RAW?** So you can see the ACTUAL structure GHL uses, not a converted version.

### Step 2: Build Field Maps Table

```bash
python build_field_maps.py
```

This:
1. Fetches custom field definitions from GHL
2. Shows you the ACTUAL field keys (with underscores!)
3. Maps them to database columns
4. Populates the `field_maps` table
5. Saves `custom_fields_response.json` for inspection

**The field_maps table contains:**
- `ghl_key` - The custom field ID (e.g., `cScyx9WMk8apxXU0rMZX`)
- `field_key` - The field key (e.g., `opportunity.passport_file`)
- `table_column` - Database column (e.g., `passport_file`)
- `tablename` - Which table (`trips` or `passengers`)
- `data_type` - For conversion (`string`, `date`, `integer`, etc.)

### Step 3: Verify Field Keys

Check the actual field keys from GHL:

```bash
cat custom_fields_response.json | python -m json.tool | grep fieldKey | head -20
```

You should see field keys like:
- `opportunity.passport_file` (WITH underscore)
- `opportunity.passport_number` (WITH underscore)
- NOT `opportunity.passportfile` (without underscore)

### Step 4: Check Raw Responses

Inspect the raw GHL responses:

```bash
# See actual contact structure
cat raw_ghl_responses/contacts_raw.json | python -m json.tool | head -50

# See actual trip opportunity structure
cat raw_ghl_responses/trips_raw.json | python -m json.tool | head -100

# See custom fields in a trip
cat raw_ghl_responses/trips_raw.json | python -m json.tool | grep -A 20 '"customFields"'
```

## Field Mapping Example

### GHL Custom Field Definition:
```json
{
  "id": "cScyx9WMk8apxXU0rMZX",
  "name": "Passport Image",
  "fieldKey": "opportunity.passport_file",
  "dataType": "FILEUPLOAD"
}
```

### In field_maps table:
```
ghl_key: cScyx9WMk8apxXU0rMZX
field_key: opportunity.passport_file
table_column: passport_file
tablename: passengers
data_type: string
```

### In GHL Opportunity customFields array:
```json
{
  "id": "cScyx9WMk8apxXU0rMZX",
  "fieldValue": "https://bucket.s3.amazonaws.com/passport.jpg"
}
```

### Mapping Process:
1. Get field ID from opportunity: `cScyx9WMk8apxXU0rMZX`
2. Look up in field_maps: Find row where `ghl_key = 'cScyx9WMk8apxXU0rMZX'`
3. Get column name: `passport_file`
4. Get data type: `string`
5. Set `passenger.passport_file = "https://bucket.s3.amazonaws.com/passport.jpg"`

## Updating Field Mappings

If you need to add or update mappings:

1. Edit `FIELD_KEY_TO_TABLE` dict in `build_field_maps.py`
2. Add the field key WITH underscores as GHL actually uses them
3. Map to the correct table and column
4. Run `python build_field_maps.py` again

Example:
```python
FIELD_KEY_TO_TABLE = {
    # Correct (WITH underscores):
    'opportunity.passport_file': ('passengers', 'passport_file'),
    'opportunity.passport_number': ('passengers', 'passport_number'),
    
    # NOT this (without underscores):
    # 'opportunity.passportfile': ('passengers', 'passport_file'),  # WRONG
}
```

## Files Created

1. **`raw_ghl_sync.py`** - Fetches RAW responses (no conversion)
2. **`build_field_maps.py`** - Builds field_maps table from GHL
3. **`models.py`** - Added FieldMap model
4. **`README_FIELD_MAPPING.md`** - This file

## Next Steps

After you have:
- ✅ RAW JSON files from GHL
- ✅ field_maps table populated
- ✅ Verified the actual field keys

Then I can create:
1. Dynamic field mapper that uses the field_maps table
2. Sync script that properly converts data using the mappings
3. Database population from the RAW responses

## Key Points

- **GHL field keys HAVE underscores**: `opportunity.passport_file`
- **Documentation is sometimes wrong**: Shows without underscores
- **Use RAW responses**: See actual structure
- **Use field_maps table**: Database-driven mapping
- **Verify first**: Always check what GHL actually returns

## Debugging

If mappings aren't working:

1. Check the RAW response:
   ```bash
   cat raw_ghl_responses/trips_raw.json | python -m json.tool | grep -A 5 '"customFields"'
   ```

2. Check the field_maps table:
   ```python
   from app import app, db
   from models import FieldMap
   
   with app.app_context():
       for fm in FieldMap.query.limit(10):
           print(f"{fm.tablename}.{fm.table_column} <- {fm.field_key} (ID: {fm.ghl_key})")
   ```

3. Check what field keys are in the response vs what's in field_maps

## Status

- ✅ Created raw_ghl_sync.py for fetching RAW responses
- ✅ Created build_field_maps.py for building field_maps table
- ✅ Added FieldMap model to models.py
- ⏳ Next: Run these on your machine to get actual data
- ⏳ Then: Create proper mapper using field_maps table

---

**Run on your machine (where you have GHL API access):**

```bash
# Step 1: Get RAW data
python raw_ghl_sync.py

# Step 2: Build field maps
python build_field_maps.py

# Step 3: Verify
cat custom_fields_response.json | grep -i passport
```
