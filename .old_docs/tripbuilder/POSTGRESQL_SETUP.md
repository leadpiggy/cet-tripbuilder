# Quick Start: PostgreSQL Setup

## PostgreSQL Configuration

### 1. Update .env File
```bash
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder
nano .env
```

**Required configuration**:
```env
# GoHighLevel API
GHL_API_TOKEN=your_actual_token_here
GHL_LOCATION_ID=your_actual_location_id_here

# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/tripbuilder

# Flask
SECRET_KEY=any-random-string
FLASK_ENV=development
DEBUG=True
```

**Example DATABASE_URL formats**:
```env
# With password
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/tripbuilder

# Without password (trust auth)
DATABASE_URL=postgresql://postgres@localhost:5432/tripbuilder

# Different port
DATABASE_URL=postgresql://postgres:mypassword@localhost:5433/tripbuilder

# Different user
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/tripbuilder
```

### 2. Create PostgreSQL Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE tripbuilder;

# Verify
\l

# Exit
\q
```

**Or use createdb command**:
```bash
createdb -U postgres tripbuilder
```

### 3. Initialize Database Tables
```bash
flask init-db
```

**Expected output**:
```
✅ Database tables created successfully!
```

### 4. Apply Trip Name Migration (if needed)
```bash
# Only if you have existing trips in the database
psql -U postgres -d tripbuilder -f migration_add_trip_name.sql

# OR connect and run manually
psql -U postgres -d tripbuilder
tripbuilder=# ALTER TABLE trips ADD COLUMN name VARCHAR(200);
tripbuilder=# UPDATE trips SET name = destination || ' Trip' WHERE name IS NULL;
tripbuilder=# ALTER TABLE trips ALTER COLUMN name SET NOT NULL;
tripbuilder=# \q
```

### 5. Verify Database Connection
```bash
# Test connection
psql -U postgres -d tripbuilder -c "SELECT 1;"

# List tables
psql -U postgres -d tripbuilder -c "\dt"
```

**Expected tables**:
- trips
- contacts
- passengers
- pipelines
- pipeline_stages
- custom_field_groups
- custom_fields
- sync_logs

---

## Troubleshooting PostgreSQL Issues

### Issue: "database 'tripbuilder' does not exist"
```bash
# Create the database
createdb -U postgres tripbuilder
```

### Issue: "FATAL: password authentication failed"
```bash
# Check PostgreSQL authentication settings
cat /usr/local/var/postgresql@14/pg_hba.conf  # Mac Homebrew
# or
cat /etc/postgresql/14/main/pg_hba.conf  # Linux

# Ensure you have a line like:
# local   all   postgres   trust
# or
# local   all   postgres   md5

# Update your DATABASE_URL with correct credentials
```

### Issue: "connection to server at localhost:5432 failed"
```bash
# Check if PostgreSQL is running
brew services list  # Mac
# or
systemctl status postgresql  # Linux

# Start PostgreSQL if needed
brew services start postgresql@14  # Mac
# or
sudo systemctl start postgresql  # Linux
```

### Issue: "psycopg2" module not found
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary
```

---

## Running flask sync-ghl

### Before Running Sync
**Checklist**:
1. PostgreSQL is running
2. Database `tripbuilder` exists
3. Tables are created (`flask init-db`)
4. `.env` has correct `DATABASE_URL`
5. `.env` has valid `GHL_API_TOKEN` and `GHL_LOCATION_ID`

### Run the Sync
```bash
source venv/bin/activate
flask sync-ghl
```

### Verify Results in PostgreSQL
```bash
# Connect to database
psql -U postgres -d tripbuilder

# Check pipelines
SELECT * FROM pipelines;

# Check stages
SELECT COUNT(*) FROM pipeline_stages;

# Check custom field groups
SELECT COUNT(*) FROM custom_field_groups;

# Check custom fields
SELECT COUNT(*) FROM custom_fields;

# Check contacts
SELECT COUNT(*) FROM contacts;

# Check sync log
SELECT * FROM sync_logs ORDER BY started_at DESC LIMIT 1;

# Exit
\q
```

---

## Common PostgreSQL Commands

### View Table Structure
```sql
\d trips
\d contacts
\d pipelines
```

### View Data
```sql
SELECT * FROM pipelines;
SELECT name, position FROM pipeline_stages ORDER BY pipeline_id, position;
SELECT firstname, lastname, email FROM contacts LIMIT 10;
```

### Count Records
```sql
SELECT 
    (SELECT COUNT(*) FROM pipelines) as pipelines,
    (SELECT COUNT(*) FROM pipeline_stages) as stages,
    (SELECT COUNT(*) FROM custom_field_groups) as groups,
    (SELECT COUNT(*) FROM custom_fields) as fields,
    (SELECT COUNT(*) FROM contacts) as contacts;
```

### Clear Data (for testing)
```sql
TRUNCATE TABLE sync_logs CASCADE;
TRUNCATE TABLE passengers CASCADE;
TRUNCATE TABLE contacts CASCADE;
TRUNCATE TABLE custom_fields CASCADE;
TRUNCATE TABLE custom_field_groups CASCADE;
TRUNCATE TABLE pipeline_stages CASCADE;
TRUNCATE TABLE pipelines CASCADE;
TRUNCATE TABLE trips CASCADE;
```

### Drop and Recreate Database
```bash
# Drop database
dropdb -U postgres tripbuilder

# Recreate
createdb -U postgres tripbuilder

# Reinitialize
flask init-db
```

---

## What Error Did You Get?

Please share the error message from `flask sync-ghl` so I can help you fix it!

**Common error types**:
1. Database connection errors
2. API authentication errors
3. Import errors
4. Data type errors
5. Foreign key errors

**To get detailed error info**:
```bash
# Run with verbose Python errors
python -c "from app import app; app.app_context().push(); from ghl_sync import GHLSyncService; from ghl_api import GoHighLevelAPI; import os; api = GoHighLevelAPI(os.getenv('GHL_LOCATION_ID'), os.getenv('GHL_API_TOKEN')); sync = GHLSyncService(api); sync.perform_full_sync()"
```

This will show the full Python traceback which helps identify the exact issue.
