# Ec2 Guide

## CET Application Backend

### 1. Install Python 3.12+

```bash
# Install required dependencies
sudo yum update -y
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel sqlite-devel zlib-devel tar make

# Download and compile Python 3.12
cd /opt
sudo curl -O https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
sudo tar xzf Python-3.12.0.tgz
cd Python-3.12.0
sudo ./configure --enable-optimizations
sudo make altinstall

# Verify installation
python3.12 --version
```

### 2. Install Poetry

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3.12 -

# Add Poetry to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
poetry --version
```

### 3. Install Nginx

```bash
sudo amazon-linux-extras install nginx1 -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4. Application Setup

```bash
# Create app directory
sudo mkdir /var/www/flaskapp
sudo chown ec2-user:ec2-user /var/www/flaskapp
cd /var/www/flaskapp

# Clone your repository (replace with your actual repo)
git clone https://github.com/yourusername/your-repo.git .
```

### 5. Create Poetry Environment

```bash
# Initialize Poetry environment with Python 3.12
poetry env use python3.12

# Install dependencies
poetry install

# Install Gunicorn
poetry add gunicorn
```

### 6. Create Gunicorn Config

Create `/var/www/flaskapp/gunicorn_config.py`:

```python
bind = "unix:/var/www/flaskapp/app.sock"
workers = 3
worker_class = "gthread"
threads = 2
timeout = 30
user = "ec2-user"
group = "ec2-user"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
pythonpath = "/var/www/flaskapp"
```

### 7. Create Systemd Service

Create `/etc/systemd/system/flaskapp.service`:

```ini
[Unit]
Description=Flask App with Gunicorn (Poetry)
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/var/www/flaskapp
Environment="PATH=/var/www/flaskapp/.venv/bin"
ExecStart=/var/www/flaskapp/.venv/bin/gunicorn -c gunicorn_config.py app:app

[Install]
WantedBy=multi-user.target
```

Enable the service:

```bash
sudo mkdir -p /var/log/gunicorn
sudo systemctl daemon-reload
sudo systemctl start flaskapp
sudo systemctl enable flaskapp
```

### 8. Configure Nginx

Create `/etc/nginx/conf.d/flaskapp.conf`:

```nginx
server {
    listen 80;
    server_name app.yourdomain.com;
    
    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_pass http://unix:/var/www/flaskapp/app.sock;
    }

    location /static {
        alias /var/www/flaskapp/static;
    }
}
```

Apply configuration:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Automated Deployment with Poetry

Create deployment script `/var/www/flaskapp/deploy.sh`:

```bash
#!/bin/bash

# Navigate to app directory
cd /var/www/flaskapp

# Pull latest changes
git pull origin main

# Install dependencies
poetry install

# Restart application
sudo systemctl restart flaskapp

# Optional: Run database migrations
# poetry run flask db upgrade

echo "Deployment completed at $(date)"
```

Make executable:

```bash
chmod +x deploy.sh
```

### 10. AWS CodeDeploy Integration (Alternative)

Create `appspec.yml` in repo root:

```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/flaskapp
hooks:
  ApplicationStop:
    - location: scripts/app_stop.sh
      timeout: 300
  BeforeInstall:
    - location: scripts/setup.sh
      timeout: 300
  ApplicationStart:
    - location: scripts/app_start.sh
      timeout: 300
```

Create scripts in `scripts/` directory:

`app_stop.sh`:

```bash
#!/bin/bash
sudo systemctl stop flaskapp
```

`setup.sh`:

```bash
#!/bin/bash
# Install Python 3.12 if not present
if ! command -v python3.12 &> /dev/null
then
    # Add Python 3.12 installation commands from step 1
fi

# Install Poetry
curl -sSL https://install.python-poetry.org | python3.12 -
export PATH="/home/ec2-user/.local/bin:$PATH"
```

`app_start.sh`:

```bash
#!/bin/bash
cd /var/www/flaskapp
export PATH="/home/ec2-user/.local/bin:$PATH"
poetry install
sudo systemctl start flaskapp
```

### 11. Post-Installation Checks

```bash
# Check services
sudo systemctl status flaskapp
sudo systemctl status nginx

# Check socket file
ls -la /var/www/flaskapp/app.sock

# Test application
curl --unix-socket /var/www/flaskapp/app.sock http://localhost
```

### 12. Security Configuration

```bash
# Configure firewall
sudo firewall-cmd --zone=public --add-port=80/tcp --permanent
sudo firewall-cmd --reload

# SELinux adjustments
sudo setsebool -P httpd_can_network_connect 1
sudo semanage permissive -a httpd_t
```

### Key Changes for Python 3.12+ and Poetry

1. **Python 3.12 Installation**: Compiled from source since Amazon Linux doesn't include 3.12 in default repos
2. **Poetry Integration**:
   - Poetry-managed virtual environments
   - `poetry install` instead of pip for dependency management
   - Path configuration for Poetry binaries
3. **Environment Configuration**:
   - Explicit Python version specification in Poetry
   - Path to Poetry's virtual environment in systemd service
4. **Deployment Scripts**:
   - Updated to use Poetry commands
   - Environment variable handling for Poetry

### Recommended Workflow

1. Develop locally with Poetry
2. Commit changes to Git repository
3. On server:

   ```bash
   cd /var/www/flaskapp
   ./deploy.sh
   ```

4. For zero-downtime deployments, consider adding:

   ```bash
   # In deploy.sh
   sudo systemctl reload flaskapp  # Instead of restart
   ```

### SSL Configuration (Optional)

```bash
# Install Certbot
sudo amazon-linux-extras install epel -y
sudo yum install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d app.yourdomain.com

# Auto-renewal
(crontab -l 2>/dev/null; echo "0 0,12 * * * python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q") | crontab -
```

This setup provides:

- Python 3.12 runtime
- Poetry-based dependency management
- Production-ready Gunicorn/Nginx configuration
- Automated deployment workflow
- Systemd service management
- Subdomain routing with Nginx
- Path for SSL/TLS encryption
