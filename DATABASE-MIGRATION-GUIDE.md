# TripBuilder - Database Migration Guide

**Migrating your local PostgreSQL database to EC2**

Last Updated: October 27, 2025

---

## 🎯 Overview

You have three options for getting your database live on EC2:

1. **Option A:** Migrate local database to PostgreSQL on EC2 (Recommended for small-medium datasets)
2. **Option B:** Use AWS RDS PostgreSQL (Recommended for production/scalability)
3. **Option C:** Fresh database + GHL sync (If you can re-sync all data from GoHighLevel)

---

## 📊 Option A: Migrate Local DB to EC2 PostgreSQL (Recommended)

### Step 1: Export Your Local Database

**On your local machine:**

```bash
# Navigate to your local project
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder

# Create backup directory
mkdir -p ../database_backup

# Export the database
pg_dump -U ridiculaptop tripbuilder > ../database_backup/tripbuilder_backup.sql

# Verify the backup file
ls -lh ../database_backup/tripbuilder_backup.sql
head -n 20 ../database_backup/tripbuilder_backup.sql
```

### Step 2: Transfer Backup to EC2

**Method 1: Using SCP (Secure Copy)**

```bash
# From your local machine
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder

# Transfer the backup file to EC2
scp -i your-key.pem database_backup/tripbuilder_backup.sql ec2-user@your-ec2-ip:/tmp/
```

**Method 2: Using S3 (Alternative)**

```bash
# Upload to S3
aws s3 cp database_backup/tripbuilder_backup.sql s3://your-bucket/backups/

# On EC2, download from S3
aws s3 cp s3://your-bucket/backups/tripbuilder_backup.sql /tmp/
```

### Step 3: Set Up PostgreSQL on EC2

**On your EC2 instance:**

```bash
# Install PostgreSQL 17
sudo yum install postgresql17-server postgresql17-devel -y

# Initialize PostgreSQL
sudo postgresql-setup --initdb

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### Step 4: Configure PostgreSQL

```bash
# Edit PostgreSQL configuration for better performance
sudo nano /var/lib/pgsql/data/postgresql.conf
```

**Add/modify these settings:**
```conf
# Connection Settings
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%a.log'
log_rotation_age = 1d
log_rotation_size = 0
log_line_prefix = '%m [%p] %q%u@%d '
```

**Configure authentication:**
```bash
sudo nano /var/lib/pgsql/data/pg_hba.conf
```

**Change this line:**
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            ident
```

**To:**
```
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
```

**Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

### Step 5: Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
```

```sql
-- Create database
CREATE DATABASE tripbuilder;

-- Create user with strong password
CREATE USER tripbuilder_user WITH PASSWORD 'your_strong_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE tripbuilder TO tripbuilder_user;

-- Connect to tripbuilder database
\c tripbuilder

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO tripbuilder_user;

-- Exit
\q
```

### Step 6: Import the Database

```bash
# Import the backup
sudo -u postgres psql tripbuilder < /tmp/tripbuilder_backup.sql

# Or, if you need to import as tripbuilder_user:
psql -U tripbuilder_user -d tripbuilder -h localhost < /tmp/tripbuilder_backup.sql
# Enter password when prompted
```

### Step 7: Verify the Import

```bash
# Connect to database
psql -U tripbuilder_user -d tripbuilder -h localhost

# In PostgreSQL shell:
```

```sql
-- Check tables exist
\dt

-- Check row counts
SELECT 'trips' as table_name, COUNT(*) as count FROM trips
UNION ALL
SELECT 'passengers', COUNT(*) FROM passengers
UNION ALL
SELECT 'contacts', COUNT(*) FROM contacts
UNION ALL
SELECT 'pipelines', COUNT(*) FROM pipelines
UNION ALL
SELECT 'custom_fields', COUNT(*) FROM custom_fields;

-- Check a sample trip
SELECT id, name, destination, start_date FROM trips LIMIT 5;

-- Check a sample passenger
SELECT id, firstname, lastname, email FROM passengers LIMIT 5;

-- Exit
\q
```

### Step 8: Update Application Configuration

```bash
cd /var/www/cet-tripbuilder/tripbuilder

# Edit .env file
nano .env
```

**Update DATABASE_URL:**
```bash
DATABASE_URL=postgresql://tripbuilder_user:your_strong_password_here@localhost:5432/tripbuilder
```

### Step 9: Test the Connection

```bash
# Activate virtual environment
source /var/www/cet-tripbuilder/venv/bin/activate

# Test database connection
cd /var/www/cet-tripbuilder/tripbuilder
python3 -c "from app import app, db; app.app_context().push(); print('Tables:', db.engine.table_names())"

# Or start the app and check
python app.py
# Visit http://your-ec2-ip:5270 and verify data is visible
```

---

## 🌐 Option B: AWS RDS PostgreSQL (Production Grade)

### Advantages:
- ✅ Automated backups
- ✅ High availability
- ✅ Automatic scaling
- ✅ Managed updates
- ✅ Better security

### Step 1: Create RDS Instance

**In AWS Console:**

1. Go to RDS → Create database
2. Choose:
   - **Engine:** PostgreSQL 17.x
   - **Template:** Production (or Dev/Test for lower cost)
   - **DB instance identifier:** tripbuilder-db
   - **Master username:** tripbuilder_admin
   - **Master password:** [Strong password]
   - **DB instance class:** db.t3.micro (for testing) or db.t3.small (production)
   - **Storage:** 20 GB (expandable)
   - **VPC:** Same as your EC2 instance
   - **Security group:** Create new (allow PostgreSQL from EC2)
3. Create database

### Step 2: Configure Security Group

1. Go to RDS → Your database → Connectivity & security
2. Note the security group
3. Edit inbound rules:
   - **Type:** PostgreSQL
   - **Port:** 5432
   - **Source:** Security group of your EC2 instance

### Step 3: Import Database to RDS

**On your EC2 instance:**

```bash
# Get RDS endpoint from AWS Console
RDS_ENDPOINT="your-db-name.xxxxx.us-east-1.rds.amazonaws.com"

# Import backup
psql -h $RDS_ENDPOINT -U tripbuilder_admin -d postgres < /tmp/tripbuilder_backup.sql

# Or create database first, then import
psql -h $RDS_ENDPOINT -U tripbuilder_admin -d postgres << EOF
CREATE DATABASE tripbuilder;
\c tripbuilder
EOF

psql -h $RDS_ENDPOINT -U tripbuilder_admin -d tripbuilder < /tmp/tripbuilder_backup.sql
```

### Step 4: Update Application Configuration

```bash
# Edit .env
nano /var/www/cet-tripbuilder/tripbuilder/.env
```

**Update DATABASE_URL:**
```bash
DATABASE_URL=postgresql://tripbuilder_admin:your_password@your-db-name.xxxxx.us-east-1.rds.amazonaws.com:5432/tripbuilder
```

---

## 🔄 Option C: Fresh Database + GHL Sync

**If all your data is in GoHighLevel and can be re-synced:**

### Step 1: Set Up Fresh Database (Follow Option A Steps 3-5)

### Step 2: Initialize Empty Schema

```bash
cd /var/www/cet-tripbuilder/tripbuilder
source ../venv/bin/activate

# Create tables
python app.py init-db
```

### Step 3: Sync from GoHighLevel

```bash
# Full sync from GHL
python app.py sync-ghl

# This will pull:
# - All pipelines and stages
# - All custom fields
# - All contacts
# - All TripBooking opportunities (trips)
# - All Passenger opportunities (passengers)
```

### Step 4: Verify Sync

```bash
# Check sync logs in the application
# Or query database directly
psql -U tripbuilder_user -d tripbuilder -h localhost

# Check counts
SELECT 'trips' as table_name, COUNT(*) as count FROM trips
UNION ALL
SELECT 'passengers', COUNT(*) FROM passengers
UNION ALL
SELECT 'contacts', COUNT(*) FROM contacts;
```

---

## 🔍 Troubleshooting

### Issue: "pg_dump: command not found"

```bash
# On Mac, install PostgreSQL client tools
brew install postgresql@15

# Add to PATH
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

### Issue: "Connection refused" when importing

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL is listening
sudo netstat -plnt | grep 5432

# Check pg_hba.conf allows connections
sudo cat /var/lib/pgsql/data/pg_hba.conf
```

### Issue: "FATAL: Peer authentication failed"

**Fix:** Edit pg_hba.conf and change `peer` to `md5`:

```bash
sudo nano /var/lib/pgsql/data/pg_hba.conf

# Change:
local   all             all                                     peer

# To:
local   all             all                                     md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Issue: Database import hangs or is slow

```bash
# Import without triggers/constraints for speed
psql -U tripbuilder_user -d tripbuilder -h localhost << EOF
SET session_replication_role = replica;
\i /tmp/tripbuilder_backup.sql
SET session_replication_role = DEFAULT;
EOF
```

### Issue: Foreign key constraint errors

```bash
# Import schema first, then data
pg_restore --schema-only tripbuilder_backup.dump | psql -U tripbuilder_user -d tripbuilder
pg_restore --data-only tripbuilder_backup.dump | psql -U tripbuilder_user -d tripbuilder
```

---

## 📊 Database Size & Performance

### Check Database Size

```sql
-- Connect to database
psql -U tripbuilder_user -d tripbuilder -h localhost

-- Check database size
SELECT pg_size_pretty(pg_database_size('tripbuilder'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Optimize After Import

```sql
-- Analyze tables for query planner
ANALYZE;

-- Vacuum to reclaim space
VACUUM ANALYZE;
```

---

## 🔐 Security Best Practices

### 1. Secure PostgreSQL Password

```bash
# Generate strong password
openssl rand -base64 32

# Use in DATABASE_URL
DATABASE_URL=postgresql://tripbuilder_user:generated_password@localhost:5432/tripbuilder
```

### 2. Limit Network Access

```bash
# Edit pg_hba.conf to allow only localhost
sudo nano /var/lib/pgsql/data/pg_hba.conf

# Only allow local connections
host    tripbuilder     tripbuilder_user    127.0.0.1/32    md5
```

### 3. Regular Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-tripbuilder-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/tripbuilder"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump tripbuilder > $BACKUP_DIR/tripbuilder_$DATE.sql

# Compress
gzip $BACKUP_DIR/tripbuilder_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "tripbuilder_*.sql.gz" -mtime +7 -delete

echo "Backup completed: tripbuilder_$DATE.sql.gz"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-tripbuilder-db.sh

# Test
sudo /usr/local/bin/backup-tripbuilder-db.sh

# Schedule (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-tripbuilder-db.sh
```

---

## ✅ Post-Migration Checklist

- [ ] Database imported successfully
- [ ] All tables present
- [ ] Row counts match local database
- [ ] Application can connect to database
- [ ] Sample queries return expected data
- [ ] Application starts without errors
- [ ] Can view trips in browser
- [ ] Can view passengers in browser
- [ ] Can view contacts in browser
- [ ] GHL sync still works (if needed)
- [ ] Backup script configured
- [ ] PostgreSQL service enabled on boot

---

## 📞 Quick Reference Commands

```bash
# Export local database
pg_dump -U ridiculaptop tripbuilder > backup.sql

# Transfer to EC2
scp -i key.pem backup.sql ec2-user@ip:/tmp/

# Import on EC2
psql -U tripbuilder_user -d tripbuilder -h localhost < /tmp/backup.sql

# Check database
psql -U tripbuilder_user -d tripbuilder -h localhost
\dt
SELECT COUNT(*) FROM trips;
\q

# Test application connection
cd /var/www/cet-tripbuilder/tripbuilder
source ../venv/bin/activate
python app.py
```

---

**Your database is now live on EC2! 🎉**