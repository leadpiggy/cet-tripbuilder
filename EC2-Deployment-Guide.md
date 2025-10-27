# TripBuilder - Amazon Linux EC2 Deployment Guide

**Last Updated:** October 27, 2025
**Target:** Amazon Linux 2/2023 EC2 Instance

---

## 🚀 Deployment Steps

### Step 1: Connect to EC2 Instance

```bash
# From your local machine
ssh -i your-key.pem ec2-user@your-ec2-ip
```

---

### Step 2: Install System Dependencies

```bash
# Update system
sudo yum update -y

# Install Python 3.13 (compile from source as it's not in default repos)
# First, install build dependencies
sudo yum groupinstall "Development Tools" -y
sudo yum install openssl-devel bzip2-devel libffi-devel zlib-devel -y

# Download and compile Python 3.13
cd /tmp
wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
tar xzf Python-3.13.0.tgz
cd Python-3.13.0
./configure --enable-optimizations
sudo make altinstall  # altinstall to not replace system python

# Verify installation
python3.13 --version

# Install PostgreSQL 17 client (if using external PostgreSQL)
sudo yum install postgresql17 -y

# Install PostgreSQL 17 server (if hosting DB on same instance)
sudo yum install postgresql17-server postgresql17-devel -y

# Install Nginx for reverse proxy
sudo yum install nginx -y

# Install Git
sudo yum install git -y
```

---

### Step 3: Initialize PostgreSQL (if hosting on EC2)

```bash
# Initialize PostgreSQL
sudo postgresql-setup --initdb

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE tripbuilder;
CREATE USER tripbuilder_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE tripbuilder TO tripbuilder_user;
\q
EOF

# Configure PostgreSQL to allow local connections
sudo vim /var/lib/pgsql/data/pg_hba.conf
# Change the following line:
# host    all             all             127.0.0.1/32            ident
# To:
# host    all             all             127.0.0.1/32            md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

### Step 4: Clone Repository

```bash
# Create application directory
sudo mkdir -p /var/www
cd /var/www

# Clone repository
sudo git clone https://github.com/leadpiggy/cet-tripbuilder.git
cd cet-tripbuilder

# Set ownership
sudo chown -R ec2-user:ec2-user /var/www/cet-tripbuilder
```

---

### Step 5: Set Up Python Virtual Environment

```bash
cd /var/www/cet-tripbuilder

# Create virtual environment with Python 3.13
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
cd tripbuilder
pip install -r requirements.txt

# Install Gunicorn for production
pip install gunicorn
```

---

### Step 6: Configure Environment Variables

```bash
cd /var/www/cet-tripbuilder/tripbuilder

# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required Environment Variables:**
```bash
# Database (use your new PostgreSQL credentials)
DATABASE_URL=postgresql://tripbuilder_user:your_secure_password@localhost:5432/tripbuilder

# Flask
SECRET_KEY=generate-a-strong-secret-key-here
FLASK_ENV=production

# GoHighLevel (use NEW rotated credentials)
GHL_API_TOKEN=your_new_ghl_token
GHL_LOCATION_ID=your_location_id

# AWS S3 (use NEW rotated credentials)
AWS_ACCESS_KEY_ID=your_new_access_key
AWS_SECRET_ACCESS_KEY=your_new_secret_key
AWS_S3_BUCKET=cet-uploads
AWS_REGION=us-east-1
```

**Generate secure SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 7: Initialize Database

```bash
cd /var/www/cet-tripbuilder/tripbuilder
source ../venv/bin/activate

# Initialize database tables
python app.py init-db

# Sync data from GoHighLevel
python app.py sync-ghl
```

---

### Step 8: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/tripbuilder.service
```

**Service Configuration:**
```ini
[Unit]
Description=TripBuilder Flask Application
After=network.target postgresql.service

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/var/www/cet-tripbuilder/tripbuilder
Environment="PATH=/var/www/cet-tripbuilder/venv/bin"
ExecStart=/var/www/cet-tripbuilder/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5270 \
    --timeout 120 \
    --access-logfile /var/log/tripbuilder/access.log \
    --error-logfile /var/log/tripbuilder/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/tripbuilder
sudo chown ec2-user:ec2-user /var/log/tripbuilder

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tripbuilder
sudo systemctl start tripbuilder

# Check status
sudo systemctl status tripbuilder
```

---

### Step 9: Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/conf.d/tripbuilder.conf
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or EC2 public IP

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Client max body size (for file uploads)
    client_max_body_size 20M;

    # Logs
    access_log /var/log/nginx/tripbuilder_access.log;
    error_log /var/log/nginx/tripbuilder_error.log;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5270;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Static files (if serving static files directly)
    location /static {
        alias /var/www/cet-tripbuilder/tripbuilder/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Test Nginx configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Restart Nginx
sudo systemctl restart nginx
```

---

### Step 10: Configure EC2 Security Group

**In AWS Console:**
1. Go to EC2 → Security Groups
2. Find your instance's security group
3. Add Inbound Rules:
   - **HTTP**: Port 80, Source: 0.0.0.0/0 (or your IP range)
   - **HTTPS**: Port 443, Source: 0.0.0.0/0 (for future SSL)
   - **SSH**: Port 22, Source: Your IP only (security)

---

### Step 11: Set Up SSL Certificate (Optional but Recommended)

```bash
# Install Certbot for Let's Encrypt
sudo yum install certbot -y
sudo python3.13 -m pip install certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

**Update Nginx config after SSL:**
```bash
sudo nano /etc/nginx/conf.d/tripbuilder.conf
```

Certbot will automatically modify the file, or manually add:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🔄 Updating the Application

```bash
# Pull latest changes
cd /var/www/cet-tripbuilder
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies (if requirements.txt changed)
cd tripbuilder
pip install -r requirements.txt

# Restart application
sudo systemctl restart tripbuilder

# Check logs
sudo journalctl -u tripbuilder -f
```

---

## 📊 Monitoring & Maintenance

### View Application Logs
```bash
# Real-time logs
sudo journalctl -u tripbuilder -f

# Application logs
tail -f /var/log/tripbuilder/access.log
tail -f /var/log/tripbuilder/error.log

# Nginx logs
tail -f /var/log/nginx/tripbuilder_access.log
tail -f /var/log/nginx/tripbuilder_error.log
```

### Check Service Status
```bash
# Application
sudo systemctl status tripbuilder

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

### Database Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-tripbuilder.sh
```

**Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/tripbuilder"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump tripbuilder > $BACKUP_DIR/tripbuilder_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "tripbuilder_*.sql" -mtime +7 -delete

echo "Backup completed: tripbuilder_$DATE.sql"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-tripbuilder.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-tripbuilder.sh
```

---

## 🔒 Security Best Practices

### 1. Firewall Configuration
```bash
# Install firewalld
sudo yum install firewalld -y
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Configure rules
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 2. Fail2Ban (Optional)
```bash
# Install fail2ban
sudo yum install fail2ban -y

# Configure
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Updates
```bash
# Create update script
sudo nano /usr/local/bin/system-update.sh
```

```bash
#!/bin/bash
sudo yum update -y
sudo systemctl restart tripbuilder
```

---

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check logs
sudo journalctl -u tripbuilder -n 50

# Test manually
cd /var/www/cet-tripbuilder/tripbuilder
source ../venv/bin/activate
python app.py
```

### Database Connection Issues
```bash
# Test connection
psql -U tripbuilder_user -d tripbuilder -h localhost

# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/lib/pgsql/data/log/postgresql-*.log
```

### Nginx Issues
```bash
# Test configuration
sudo nginx -t

# Check error log
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

---

## 📝 Post-Deployment Checklist

- [ ] Application accessible via HTTP
- [ ] Database connection working
- [ ] GHL sync successful
- [ ] S3 file uploads working
- [ ] SSL certificate installed (if using HTTPS)
- [ ] Firewall configured
- [ ] Backup script running
- [ ] Monitoring set up
- [ ] Old AWS credentials rotated
- [ ] Application logs rotating properly

---

## 🔗 Access Points

**Application URL:** `http://your-ec2-ip` or `https://your-domain.com`

**Dashboard:** `/`
**Trips:** `/trips`
**Contacts:** `/contacts`
**Vendors:** `/vendors`

---

**Deployment complete! Your TripBuilder application is now running on Amazon Linux EC2.**