# Quick Command Reference

One-page reference for common TripBuilder commands.

---

## Setup & Activation

```bash
# Navigate to project
cd ~/Downloads/claude_code_tripbuilder/tripbuilder

# Activate virtual environment
source ../.venv/bin/activate

# Check environment variables
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Token:', 'SET' if os.getenv('GHL_API_TOKEN') else 'MISSING'); print('Location ID:', 'SET' if os.getenv('GHL_LOCATION_ID') else 'MISSING')"
```

---

## Database Commands

```bash
# Initialize database (first time only)
flask init-db

# Drop and recreate tables
python3 recreate_db.py

# Open database shell
psql -U ridiculaptop -d tripbuilder

# Backup database
pg_dump -U ridiculaptop tripbuilder > backup_$(date +%Y%m%d).sql

# Restore database
psql -U ridiculaptop tripbuilder < backup_20250127.sql
```

---

## Sync Commands

```bash
# Full sync from GHL
flask sync-ghl

# Expected output:
# ✅ Pipelines: 2
# ✅ Stages: 11
# ✅ Custom Fields: 53
# ✅ Contacts: ~5,453
# ✅ Trips: ~693
# ✅ Passengers: ~6,477
```

---

## Query Commands (PostgreSQL)

### Quick Counts
```sql
-- All counts at once
SELECT 
    (SELECT COUNT(*) FROM pipelines) as pipelines,
    (SELECT COUNT(*) FROM pipeline_stages) as stages,
    (SELECT COUNT(*) FROM custom_fields) as fields,
    (SELECT COUNT(*) FROM contacts) as contacts,
    (SELECT COUNT(*) FROM trips) as trips,
    (SELECT COUNT(*) FROM passengers) as passengers;
```

### Trip Queries
```sql
-- List recent trips
SELECT id, name, destination, arrival_date, return_date, max_passengers
FROM trips
ORDER BY arrival_date DESC
LIMIT 10;

-- Trips by vendor
SELECT trip_vendor, COUNT(*) as count
FROM trips
WHERE trip_vendor IS NOT NULL
GROUP BY trip_vendor
ORDER BY count DESC;

-- Trips with pricing
SELECT name, destination, trip_standard_level_pricing, max_passengers
FROM trips
WHERE trip_standard_level_pricing IS NOT NULL
ORDER BY trip_standard_level_pricing DESC;
```

### Passenger Queries
```sql
-- Recent passengers
SELECT id, firstname, lastname, email, passport_country, health_state
FROM passengers
ORDER BY created_at DESC
LIMIT 10;

-- Passengers by trip
SELECT 
    t.name as trip,
    COUNT(p.id) as passengers,
    t.max_passengers as capacity
FROM trips t
LEFT JOIN passengers p ON p.trip_id = t.id
GROUP BY t.id, t.name, t.max_passengers
ORDER BY passengers DESC;

-- Passengers with passport info
SELECT COUNT(*) as with_passport
FROM passengers
WHERE passport_number IS NOT NULL;

-- Passengers with health info
SELECT health_state, COUNT(*) as count
FROM passengers
WHERE health_state IS NOT NULL
GROUP BY health_state;
```

### Sync Log
```sql
-- Recent syncs
SELECT 
    sync_type,
    status,
    records_synced,
    started_at,
    completed_at,
    (completed_at - started_at) as duration
FROM sync_log
ORDER BY started_at DESC
LIMIT 5;

-- Failed syncs
SELECT *
FROM sync_log
WHERE status = 'failed'
ORDER BY started_at DESC;
```

---

## Flask Commands

```bash
# Run web server
flask run
# or
python3 app.py

# Access at: http://localhost:5269

# Flask shell (interactive Python)
flask shell

# In shell:
>>> from models import Trip, Passenger, Contact
>>> Trip.query.count()
>>> Passenger.query.first().firstname
>>> exit()
```

---

## Verification Scripts

### Check Trip Fields
```bash
python3 check_trip_fields.py
```

### Debug Passenger
```bash
python3 debug_passenger.py
```

### Debug Sync
```bash
python3 debug_sync.py
```

---

## Common SQL Patterns

### Find Unlinked Passengers
```sql
SELECT id, firstname, lastname, email
FROM passengers
WHERE trip_id IS NULL
LIMIT 20;
```

### Find Trips Without Passengers
```sql
SELECT t.id, t.name, t.destination, t.arrival_date
FROM trips t
LEFT JOIN passengers p ON p.trip_id = t.id
WHERE p.id IS NULL
ORDER BY t.arrival_date DESC;
```

### Find Duplicate Opportunities
```sql
-- Duplicate trips
SELECT ghl_opportunity_id, COUNT(*) as count
FROM trips
GROUP BY ghl_opportunity_id
HAVING COUNT(*) > 1;

-- Duplicate passengers
SELECT id, COUNT(*) as count
FROM passengers
GROUP BY id
HAVING COUNT(*) > 1;
```

### Data Quality Checks
```sql
-- Trips missing required fields
SELECT id, name, destination
FROM trips
WHERE arrival_date IS NULL 
   OR return_date IS NULL 
   OR max_passengers IS NULL;

-- Passengers missing contact info
SELECT id, firstname, lastname
FROM passengers
WHERE email IS NULL 
   OR phone IS NULL;
```

---

## File Locations

```
~/Downloads/claude_code_tripbuilder/
├── .venv/                          # Virtual environment
│   └── bin/activate                # Activation script
│
└── tripbuilder/
    ├── .env                        # Environment variables (GHL keys)
    ├── app.py                      # Flask app & routes
    ├── models.py                   # Database models
    ├── ghl_api.py                  # GHL API wrapper
    ├── ghl_sync.py                 # Sync service ⭐ UPDATED
    ├── field_mapping.py            # Field mapping utilities ⭐ NEW
    ├── recreate_db.py              # DB recreation script
    │
    ├── templates/                  # HTML templates
    │   ├── index.html
    │   ├── trips/list.html
    │   ├── trips/detail.html
    │   └── passengers/enroll.html
    │
    └── static/                     # CSS/JS
        └── style.css
```

---

## Environment Variables (.env)

```bash
# Required
GHL_API_TOKEN=your_ghl_api_token_here
GHL_LOCATION_ID=your_location_id_here

# Database
DATABASE_URL=postgresql://ridiculaptop:@localhost/tripbuilder

# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

---

## Port Numbers

- **Flask Web App:** http://localhost:5269
- **PostgreSQL:** localhost:5432

---

## Log Locations

```bash
# Flask logs (if configured)
tail -f /var/log/tripbuilder/flask.log

# PostgreSQL logs
tail -f /usr/local/var/log/postgres.log

# System logs
tail -f /var/log/system.log
```

---

## Emergency Procedures

### If Database is Corrupted
```bash
# 1. Backup first
pg_dump -U ridiculaptop tripbuilder > emergency_backup.sql

# 2. Drop database
dropdb -U ridiculaptop tripbuilder

# 3. Recreate
createdb -U ridiculaptop tripbuilder

# 4. Run init
cd ~/Downloads/claude_code_tripbuilder/tripbuilder
source ../.venv/bin/activate
flask init-db

# 5. Re-sync
flask sync-ghl
```

### If Sync is Stuck
```bash
# 1. Find process
ps aux | grep flask

# 2. Kill it
kill -9 <pid>

# 3. Clear sync log
psql -U ridiculaptop tripbuilder -c "DELETE FROM sync_log WHERE status = 'in_progress';"

# 4. Try again
flask sync-ghl
```

### If GHL Credentials Invalid
```bash
# 1. Open .env
nano .env

# 2. Update credentials
GHL_API_TOKEN=new_token_here

# 3. Test connection
python3 -c "from ghl_api import GoHighLevelAPI; import os; api = GoHighLevelAPI(os.getenv('GHL_LOCATION_ID'), os.getenv('GHL_API_TOKEN')); print('Connected!' if api.get_pipelines() else 'Failed')"
```

---

## Helpful Aliases

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# TripBuilder shortcuts
alias tb='cd ~/Downloads/claude_code_tripbuilder/tripbuilder && source ../.venv/bin/activate'
alias tbdb='psql -U ridiculaptop tripbuilder'
alias tbsync='cd ~/Downloads/claude_code_tripbuilder/tripbuilder && source ../.venv/bin/activate && flask sync-ghl'
alias tbrun='cd ~/Downloads/claude_code_tripbuilder/tripbuilder && source ../.venv/bin/activate && flask run'
```

Usage:
```bash
tb        # Navigate & activate
tbdb      # Open database
tbsync    # Run sync
tbrun     # Start web server
```

---

## Quick Health Check

Run this to verify everything is working:

```bash
cd ~/Downloads/claude_code_tripbuilder/tripbuilder
source ../.venv/bin/activate

echo "1. Environment Variables"
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅' if os.getenv('GHL_API_TOKEN') else '❌', 'API Token'); print('✅' if os.getenv('GHL_LOCATION_ID') else '❌', 'Location ID')"

echo -e "\n2. Database Connection"
psql -U ridiculaptop tripbuilder -c "SELECT 'âœ…' as status, 'Connected' as result;" 2>/dev/null || echo "❌ Connection failed"

echo -e "\n3. Table Counts"
psql -U ridiculaptop tripbuilder -c "SELECT (SELECT COUNT(*) FROM trips) as trips, (SELECT COUNT(*) FROM passengers) as passengers, (SELECT COUNT(*) FROM contacts) as contacts;"

echo -e "\n4. Flask App"
python3 -c "from app import app; print('âœ… Flask app loads')" 2>/dev/null || echo "❌ Flask app failed"

echo -e "\n5. GHL API"
python3 -c "from ghl_api import GoHighLevelAPI; import os; from dotenv import load_dotenv; load_dotenv(); api = GoHighLevelAPI(os.getenv('GHL_LOCATION_ID'), os.getenv('GHL_API_TOKEN')); api.get_pipelines(); print('âœ… GHL API works')" 2>/dev/null || echo "❌ GHL API failed"
```

Expected output:
```
1. Environment Variables
✅ API Token
✅ Location ID

2. Database Connection
✅ Connected

3. Table Counts
 trips | passengers | contacts 
-------+------------+----------
   693 |       6477 |     5453

4. Flask App
✅ Flask app loads

5. GHL API
✅ GHL API works
```

---

**Quick Reference Last Updated:** Stage 2A Implementation
