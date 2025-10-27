# Sync and Debug Scripts

This directory contains scripts for syncing data from GoHighLevel and debugging issues without repeatedly hitting the API.

## Quick Start

Run the complete sync and debug process with a single command:

```bash
cd ~/Downloads/claude_code_tripbuilder/tripbuilder
source ../.venv/bin/activate
python run_complete_sync_and_debug.py
```

This will:
1. ✅ Sync all data from GHL and capture raw API responses
2. ✅ Export all database data to JSON files
3. ✅ Attempt to match passengers to trips automatically
4. ✅ Export database again to show the final state

## Individual Scripts

### 1. sync_with_capture.py
**Purpose**: Run the full GHL sync but capture all raw API responses to JSON files.

**Usage**:
```bash
python sync_with_capture.py
```

**Output**: Creates timestamped directory in `sync_captures/` with:
- `000_sync_results.json` - Summary of sync operation
- `001_pipelines.json` - Pipeline definitions from GHL
- `002_custom_fields_opportunity.json` - Custom field definitions
- `003_contacts.json`, `004_contacts.json`, etc. - Contact pages
- `005_opportunities_IlWdPtOpcczLpgsde2KF_page1.json` - Trip opportunities
- `006_opportunities_fnsdpRtY9o83Vr4z15bE_page1.json` - Passenger opportunities

**Benefits**: 
- Debug sync logic without hitting the API repeatedly
- See exactly what data GHL is returning
- Compare responses across different sync runs

### 2. export_database.py
**Purpose**: Export all database tables to JSON files for easy inspection.

**Usage**:
```bash
python export_database.py
```

**Output**: Creates timestamped directory in `database_exports/` with:
- `trips.json` - All trip records
- `contacts.json` - All contact records  
- `passengers.json` - All passenger records (with contact and trip names added)
- `pipelines.json` - Pipeline and stage definitions
- `summary.json` - Quick stats and overview

**Benefits**:
- See exactly what's in your database
- Easily search and filter records
- Compare database state before/after operations

### 3. backpopulate_trip_ids.py
**Purpose**: Fix passenger-trip relationships by matching passengers to trips.

**Usage**:
```bash
python backpopulate_trip_ids.py
```

**What it does**:
- Finds passengers without trip_id set
- Attempts multiple matching strategies:
  1. Exact match by GHL opportunity ID
  2. Exact match by trip name
  3. Fuzzy match by trip name
  4. If only one trip exists, use it
- Updates passenger.trip_id field

**Benefits**:
- Fixes broken relationships automatically
- Shows which strategy matched each passenger
- Can be run multiple times safely

### 4. run_complete_sync_and_debug.py
**Purpose**: Master script that runs all the above in sequence.

**Usage**:
```bash
python run_complete_sync_and_debug.py
```

**Process**:
1. Runs sync with API capture
2. Exports database state
3. Back-populates trip relationships
4. Exports database again (to show changes)

**Benefits**:
- Complete debugging package in one command
- Creates comprehensive snapshot of system state
- All data saved for offline analysis

## Directory Structure

After running the scripts, you'll have:

```
tripbuilder/
├── sync_captures/          # Raw API responses
│   └── 20241027_143022/    # Timestamped run
│       ├── 000_sync_results.json
│       ├── 001_pipelines.json
│       ├── 002_custom_fields_opportunity.json
│       └── ... (more API responses)
│
├── database_exports/        # Database snapshots
│   └── 20241027_143045/    # Timestamped run
│       ├── trips.json
│       ├── contacts.json
│       ├── passengers.json
│       ├── pipelines.json
│       └── summary.json
│
└── [these scripts]

```

## Debugging Workflow

1. **Initial Sync**:
   ```bash
   python run_complete_sync_and_debug.py
   ```

2. **Inspect Results**:
   - Check `sync_captures/[latest]/` to see raw API data
   - Check `database_exports/[latest]/` to see what was saved
   - Look at `passengers.json` to see trip assignments

3. **If Issues Found**:
   - Modify sync logic in `services/ghl_sync.py`
   - Test changes by editing `sync_with_capture.py` to use saved data
   - No need to hit the API again!

4. **Re-run Back-population** (if needed):
   ```bash
   python backpopulate_trip_ids.py
   python export_database.py
   ```

## Common Issues and Solutions

### Issue: Passengers have no trip_id
**Solution**: Run `backpopulate_trip_ids.py`

### Issue: Need to see what GHL is returning
**Solution**: Check `sync_captures/[latest]/` JSON files

### Issue: Unsure what's in the database
**Solution**: Run `export_database.py` and check the JSON files

### Issue: Sync failing with API errors
**Solution**: Check captured responses in `sync_captures/` to see exact error

### Issue: Want to test sync changes without API calls
**Solution**: Modify `sync_with_capture.py` to load from previous captures instead of calling API

## Environment Variables Required

Make sure `.env` file has:
```
GHL_API_TOKEN=your_token_here
GHL_LOCATION_ID=your_location_id_here
DATABASE_URL=sqlite:///tripbuilder.db
```

## Notes

- All timestamps are in format: `YYYYMMDD_HHMMSS`
- JSON files use indentation for readability
- Dates are exported in ISO format (YYYY-MM-DD)
- The scripts are safe to run multiple times
- Previous captures/exports are not deleted (you can compare across runs)

## Making Scripts Executable (Optional)

```bash
chmod +x *.py
```

Then you can run them as:
```bash
./run_complete_sync_and_debug.py
```
