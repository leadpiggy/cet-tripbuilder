# Technical Context

**Project:** TripBuilder
**Build Location:** tripbuilder/
**Last Updated:** October 27, 2025

---

## 🎯 Technology Stack Overview

### Backend Framework
**Flask 2.3.0+:** Python web framework

**Why Flask:**
- Lightweight and flexible
- Excellent ecosystem (SQLAlchemy, Jinja2)
- Easy to extend with blueprints
- Built-in development server
- Strong community support

**Configuration:**
```python
# app.py
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
```

**Commands:**
```bash
# Run development server
python app.py

# CLI commands
flask init-db          # Initialize database
flask sync-ghl         # Sync from GoHighLevel
```

---

### Database - PostgreSQL
**PostgreSQL 14+:** Production relational database

**Why PostgreSQL:**
- Handles 12,000+ records efficiently
- ACID compliance for data integrity
- JSON field support for custom fields
- Advanced indexing capabilities
- Reliable for production workloads

**Connection String:**
```
postgresql://ridiculaptop@localhost:5432/tripbuilder
```

**Configuration:**
```python
# In .env
DATABASE_URL=postgresql://ridiculaptop@localhost:5432/tripbuilder
```

**Database Models (9 total):**
```python
# models.py
Trip              # Trip master records
Contact           # GHL contacts (synced)
Passenger         # Junction: Contact ↔ Trip
Pipeline          # 2 pipelines (TripBooking, Passenger)
PipelineStage     # 11 stages across pipelines
CustomFieldGroup  # 5 field groups
CustomField       # 53 field definitions
SyncLog           # Sync operation history
FieldMap          # Dynamic field mapping
```

**Common Queries:**
```bash
# Connect to database
psql -U ridiculaptop -d tripbuilder

# Check record counts
SELECT COUNT(*) FROM trips;           -- 693
SELECT COUNT(*) FROM passengers;      -- 6,477
SELECT COUNT(*) FROM contacts;        -- 5,453

# Exit
\q
```

---

### ORM - SQLAlchemy
**SQLAlchemy 2.0.0+:** Python SQL toolkit and ORM

**Why SQLAlchemy:**
- Mature and well-documented
- Type-safe queries
- Relationship management
- Migration support
- Session management

**Model Examples:**
```python
class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255))
    arrival_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    max_passengers = db.Column(db.Integer)
    ghl_opportunity_id = db.Column(db.String(100), unique=True)
    
    # Relationship to passengers
    passengers = db.relationship('Passenger', backref='trip', lazy=True)

class Passenger(db.Model):
    __tablename__ = 'passengers'
    
    id = db.Column(db.String(100), primary_key=True)  # GHL opportunity ID
    contact_id = db.Column(db.String(100), db.ForeignKey('contacts.id'))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    trip_name = db.Column(db.String(255))  # Used for linking
    stage_id = db.Column(db.String(100), db.ForeignKey('pipeline_stages.id'))
    
    # Custom fields
    passport_number = db.Column(db.String(100))
    passport_expire = db.Column(db.Date)
    health_state = db.Column(db.Text)
    # ... 20+ more custom fields
```

---

### API Integration - GoHighLevel
**GoHighLevel API v2:** CRM and workflow automation platform

**Why GoHighLevel:**
- Native CRM with contacts and opportunities
- Custom fields for data capture
- Pipeline workflow management
- Automation capabilities
- REST API with Bearer token auth

**API Configuration:**
```bash
# .env
GHL_API_TOKEN=your_private_integration_token_here
GHL_LOCATION_ID=your_location_id_here
```

**API Wrapper:**
```python
# ghl_api.py
class GoHighLevelAPI:
    def __init__(self, location_id, api_token):
        self.base_url = "https://services.leadconnectorhq.com"
        self.location_id = location_id
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Version': '2021-07-28',
            'Content-Type': 'application/json'
        }
    
    # Key methods
    def get_pipelines(self)
    def get_custom_fields(model='opportunity')
    def search_contacts(query)
    def create_contact(contact_data)
    def create_opportunity(opp_data)
    def update_opportunity(opp_id, data)
    def update_custom_field(opp_id, field_key, value)
    def delete_opportunity(opp_id)
```

**Pipelines:**
- **TripBooking:** `IlWdPtOpcczLpgsde2KF` (5 stages)
- **Passenger:** `fnsdpRtY9o83Vr4z15bE` (6 stages)

**Custom Fields:**
- 53 opportunity custom fields
- Field format: `opportunity.fieldname`
- Types: STRING, NUMBER, DATE, LARGE_TEXT, SINGLE_OPTIONS, FILE_UPLOAD, SIGNATURE

---

### Sync Services
**Bidirectional synchronization between local database and GHL**

**GHL → Local Bulk Sync:**
```python
# services/ghl_sync.py
class GHLSyncService:
    def sync_pipelines()              # 2 pipelines, 11 stages
    def sync_custom_fields()          # 5 groups, 53 fields
    def sync_contacts()               # 5,453 contacts with pagination
    def sync_trip_opportunities()     # 693 trips
    def sync_passenger_opportunities() # 6,477 passengers
    def perform_full_sync()           # Orchestrates all syncs
```

**Local → GHL Auto-Sync:**
```python
# services/two_way_sync.py
class TwoWaySyncService:
    def auto_sync_on_trip_create(trip)
    def auto_sync_on_trip_update(trip)
    def auto_sync_on_passenger_create(passenger)
    def auto_sync_on_passenger_update(passenger)
    def push_contact_to_ghl(contact)
```

**Field Mapping:**
```python
# field_mapping.py
TRIP_FIELD_MAP = {
    'opportunity.tripname': ('trip_name', 'string'),
    'opportunity.destination': ('destination', 'string'),
    'opportunity.arrivaldate': ('arrival_date', 'date'),
    'opportunity.returndate': ('return_date', 'date'),
    'opportunity.maxpassengers': ('max_passengers', 'integer'),
    # ... 25+ more mappings
}

PASSENGER_FIELD_MAP = {
    'opportunity.tripname': ('trip_name', 'string'),
    'opportunity.passportnumber': ('passport_number', 'string'),
    'opportunity.passportexpire': ('passport_expire', 'date'),
    'opportunity.healthstate': ('health_state', 'text'),
    # ... 20+ more mappings
}
```

---

### Frontend - Templates & UI
**Jinja2:** Server-side templating engine (Flask built-in)

**Bootstrap 5:** Responsive CSS framework

**Why Bootstrap:**
- Rapid development
- Professional appearance
- Mobile-responsive out of the box
- Extensive component library
- Well-documented

**Template Structure:**
```
templates/
├── base.html                 # Base layout with navbar
├── index.html                # Dashboard
├── trips/
│   ├── list.html            # Trip cards view
│   ├── detail.html          # Trip detail
│   └── form.html            # Create/edit trip
├── passengers/
│   ├── enroll.html          # Enrollment form
│   └── detail.html          # Passenger profile (to be built)
└── contacts/
    ├── list.html            # Contact list
    └── detail.html          # Contact detail
```

**Static Assets:**
```
static/
├── css/
│   └── custom.css           # Custom styles
└── js/
    └── app.js               # Client-side JavaScript
```

---

## 📦 Package Management

**pip + virtual environment:** Python dependency management

**Installation:**
```bash
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder
python3 -m venv .venv
source .venv/bin/activate
cd tripbuilder
pip install -r requirements.txt
```

**Dependencies (requirements.txt):**
```
Flask>=2.3.0
Flask-SQLAlchemy>=3.0.0
SQLAlchemy>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
requests>=2.31.0
werkzeug>=2.3.0
```

**Commands:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Freeze dependencies
pip freeze > requirements.txt

# Deactivate
deactivate
```

---

## 🗄️ File Structure

```
/Users/ridiculaptop/Downloads/claude_code_tripbuilder/
├── .venv/                           # Virtual environment
├── tripbuilder/                     # Main application directory
│   ├── app.py                       # Flask application & routes
│   ├── models.py                    # SQLAlchemy models
│   ├── ghl_api.py                   # GHL API wrapper
│   ├── field_mapping.py             # Field mapping definitions
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # Environment variables (gitignored)
│   ├── .env.example                 # Environment template
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ghl_sync.py             # GHL → Local sync
│   │   └── two_way_sync.py         # Local → GHL sync
│   ├── templates/                   # Jinja2 templates
│   ├── static/                      # CSS, JavaScript
│   ├── database_exports/            # Database snapshots
│   ├── raw_ghl_responses/          # GHL API response cache
│   └── sync_captures/              # Sync operation logs
└── memory-bank/                     # Roo Code context tracking
    ├── projectBrief.md
    ├── progress.md
    ├── activeContext.md
    ├── techContext.md               # This file
    └── systemPatterns.md
```

---

## 🔐 Environment Variables

**Location:** `tripbuilder/.env`

```bash
# GoHighLevel API
GHL_API_TOKEN=your_private_integration_token
GHL_LOCATION_ID=your_location_id

# Database
DATABASE_URL=postgresql://ridiculaptop@localhost:5432/tripbuilder

# Flask
SECRET_KEY=your_random_secret_key_for_sessions
FLASK_APP=app.py
FLASK_ENV=development

# Server
PORT=5269
```

**Getting GHL Credentials:**
1. Log into GoHighLevel
2. Navigate to Settings → Private Integrations
3. Create new private integration
4. Copy API token and location ID

---

## ✅ Technology Checklist

- [x] Python 3.x installed
- [x] Virtual environment created (`.venv`)
- [x] Flask 2.3.0+ installed
- [x] PostgreSQL 14+ running
- [x] Database `tripbuilder` created
- [x] SQLAlchemy configured
- [x] GHL API credentials set
- [x] Bootstrap 5 integrated (CDN)
- [x] Templates organized
- [x] Static files created
- [x] Sync services implemented
- [x] Field mapping system operational

---

## 🚀 Development Workflow

### Starting Development:
```bash
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder
source .venv/bin/activate
cd tripbuilder
```

### Running the Application:
```bash
# Development server
python app.py
# Access at http://localhost:5269

# Or use Flask CLI
flask run --port 5269
```

### Database Operations:
```bash
# Initialize database (first time)
flask init-db

# Access database
psql -U ridiculaptop -d tripbuilder

# Run migrations (if needed)
python migrate_add_trip_columns.py
```

### Sync Operations:
```bash
# Full sync from GHL
flask sync-ghl

# Export passengers
python export_all_passengers_raw.py

# Link passengers to trips
python link_passengers_from_raw_json.py
```

### Testing:
```bash
# Test two-way sync
python test_two_way_sync.py

# Test field mapping
python test_dynamic_mapping.py

# Verify data
python verify_data.py
```

---

## 🔧 Key Configuration Details

### Flask Application:
```python
# app.py configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JSON_SORT_KEYS'] = False

# Port configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5269))
    app.run(host='0.0.0.0', port=port, debug=True)
```

### Database Connection:
```python
# PostgreSQL connection via SQLAlchemy
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
session = Session()
```

### GHL API Headers:
```python
headers = {
    'Authorization': f'Bearer {api_token}',
    'Version': '2021-07-28',
    'Content-Type': 'application/json'
}
```

---

## 📚 API Reference

### Flask Routes:
```python
# Trip routes
GET  /                          # Dashboard
GET  /trips                     # Trip list
GET  /trips/new                 # Trip creation form
POST /trips/new                 # Create trip
GET  /trips/<id>                # Trip detail
POST /trips/<id>/edit           # Update trip
POST /trips/<id>/delete         # Delete trip

# Passenger routes
GET  /trips/<id>/enroll         # Enrollment form
POST /trips/<id>/enroll         # Enroll passenger

# Contact routes

---

## 🗂️ File Management System (S3) - BUCKET CONFIGURED

### AWS S3 Configuration (READY FOR IMPLEMENTATION)

**Status:** ✅ Bucket created and configured via `bucket_setup.py`

**Bucket Details:**
- **Name:** `cet-uploads`
- **Region:** `us-east-1`
- **Versioning:** Enabled
- **Public Access:** Tag-based (files with `Public=yes` tag are publicly readable)
- **CORS:** Configured for browser uploads
- **IAM User:** `cet-uploads-ftp-user` (for Cyberduck FTP access)

**Bucket Structure (Planned):**
```
s3://cet-uploads/
├── ghl-uploads/              # GHL webhook uploads (from S3-Setup.md)
├── trips/
│   └── {trip-name}/
│       └── passengers/
│           └── {passenger-name}/
│               ├── passports/
│               │   └── passport_{timestamp}.jpg
│               ├── signatures/
│               │   └── signature_{timestamp}.png
│               └── documents/
│                   ├── confirmation_{timestamp}.pdf
│                   ├── itinerary_{timestamp}.pdf
│                   └── legal-form_{timestamp}.pdf
└── temp/                     # Temporary uploads
```

**Environment Variables (Already Configured):**
```bash
# In tripbuilder/.env
AWS_ACCESS_KEY_ID=<from bucket_setup.py output>
AWS_SECRET_ACCESS_KEY=<from bucket_setup.py output>
AWS_S3_BUCKET=cet-uploads
AWS_REGION=us-east-1
BOTO_USER_NAME=python-s3-setup
BOTO_USER_PW=CETcrm2025!
```

**Dependencies to Add:**
```bash
# Add to tripbuilder/requirements.txt
boto3>=1.28.0
```

### S3 File Manager Service (To Be Created)

**File:** `tripbuilder/services/file_manager.py`

```python
import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from datetime import datetime
import io

load_dotenv()

class S3FileManager:
    def __init__(self):
        """Initialize S3 client with credentials from .env"""
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket = os.getenv('AWS_S3_BUCKET', 'cet-uploads')
    
    def upload_file(self, file_obj, s3_path, content_type=None, make_public=False):
        """
        Upload file to S3
        
        Args:
            file_obj: File object or bytes
            s3_path: Destination path in S3 bucket
            content_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            make_public: If True, add Public=yes tag for public access
        """
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type
        if make_public:
            extra_args['Tagging'] = 'Public=yes'
        
        try:
            self.s3.upload_fileobj(file_obj, self.bucket, s3_path, ExtraArgs=extra_args)
            return True
        except ClientError as e:
            print(f"Upload error: {e}")
            return False
    
    def generate_upload_url(self, s3_path, content_type='application/pdf', expiration=3600):
        """
        Generate pre-signed URL for direct uploads (for GHL webhooks)
        
        Args:
            s3_path: Destination path in S3
            content_type: MIME type
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            Pre-signed upload URL
        """
        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': s3_path,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"URL generation error: {e}")
            return None
    
    def generate_download_url(self, s3_path, expiration=3600):
        """
        Generate temporary download URL (for private files)
        
        Args:
            s3_path: File path in S3
            expiration: URL validity in seconds (default 1 hour)
        
        Returns:
            Pre-signed download URL
        """
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_path},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Download URL error: {e}")
            return None
    
    def get_public_url(self, s3_path):
        """
        Get public URL for files tagged with Public=yes
        
        Args:
            s3_path: File path in S3
        
        Returns:
            Public S3 URL
        """
        return f"https://{self.bucket}.s3.amazonaws.com/{s3_path}"
    
    def delete_file(self, s3_path):
        """Delete file from S3"""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_path)
            return True
        except ClientError as e:
            print(f"Delete error: {e}")
            return False
    
    def list_files(self, prefix):
        """
        List all files under prefix
        
        Args:
            prefix: Directory path in S3 (e.g., 'trips/Greece 2025/')
        
        Returns:
            List of file objects
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            print(f"List error: {e}")
            return []
    
    def file_exists(self, s3_path):
        """Check if file exists in S3"""
        try:
            self.s3.head_object(Bucket=self.bucket, Key=s3_path)
            return True
        except ClientError:
            return False
```

**File Model:**
```python
class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_path = db.Column(db.String(500), nullable=False, unique=True)
    file_type = db.Column(db.String(50))  # passport, signature, pdf
    content_type = db.Column(db.String(100))  # image/jpeg, application/pdf
    file_size = db.Column(db.Integer)
    
    # Link to opportunity
    opportunity_id = db.Column(db.String(100))
    opportunity_type = db.Column(db.String(20))  # trip, passenger
    
    # Link to entities
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    passenger_id = db.Column(db.String(100), db.ForeignKey('passengers.id'))
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.String(100))
```

### PDF Generation

**ReportLab Templates:**
```python
# services/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class PDFGenerator:
    def generate_trip_confirmation(self, trip, passenger):
        """Generate trip confirmation letter"""
        filename = f"confirmation_{trip.id}_{passenger.id}.pdf"
        s3_path = f"trips/{trip.name}/passengers/{passenger.name}/documents/{filename}"
        
        # Generate PDF
        pdf = canvas.Canvas(filename, pagesize=letter)
        pdf.drawString(100, 750, f"Trip Confirmation: {trip.name}")
        pdf.drawString(100, 720, f"Passenger: {passenger.firstname} {passenger.lastname}")
        pdf.drawString(100, 690, f"Destination: {trip.destination}")
        # ... more content
        pdf.save()
        
        # Upload to S3
        file_manager.upload_file(open(filename, 'rb'), s3_path)
        
        return s3_path
```

### Signature Capture

**JavaScript Integration:**
```html
<!-- templates/passengers/signature-capture.html -->
<script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>

<canvas id="signature-pad" class="signature-canvas"></canvas>
<button id="save-signature">Save Signature</button>

<script>
var canvas = document.getElementById('signature-pad');
var signaturePad = new SignaturePad(canvas);

document.getElementById('save-signature').addEventListener('click', function() {
    if (!signaturePad.isEmpty()) {
        var dataURL = signaturePad.toDataURL('image/png');
        // Send to backend
        fetch('/passengers/{{ passenger.id }}/signature', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({signature: dataURL})
        });
    }
});
</script>
```

**Backend Route:**
```python
@app.route('/passengers/<passenger_id>/signature', methods=['POST'])
def save_signature(passenger_id):
    signature_data = request.json['signature']
    
    # Decode base64 and save to S3
    import base64
    signature_bytes = base64.b64decode(signature_data.split(',')[1])
    
    passenger = Passenger.query.get_or_404(passenger_id)
    s3_path = f"trips/{passenger.trip_name}/passengers/{passenger.firstname}_{passenger.lastname}/signatures/signature.png"
    
    file_manager.upload_file(io.BytesIO(signature_bytes), s3_path)
    
    # Save metadata
    file_record = File(
        filename='signature.png',
        s3_path=s3_path,
        file_type='signature',
        content_type='image/png',
        passenger_id=passenger_id
    )
    db.session.add(file_record)
    db.session.commit()
    
    return jsonify({'success': True, 's3_path': s3_path})
```

**This file management system is planned for Stage 4 implementation.**

GET  /contacts                  # Contact list
GET  /contacts/<id>             # Contact detail
```

### GHL API Endpoints:
```python
# Pipelines
GET /pipelines?locationId={location_id}

# Custom Fields
GET /custom-fields?model=opportunity

# Contacts
GET /contacts/search?locationId={location_id}&query={query}
POST /contacts
GET /contacts/{contact_id}
PUT /contacts/{contact_id}
DELETE /contacts/{contact_id}

# Opportunities
POST /opportunities
GET /opportunities/{opp_id}
PUT /opportunities/{opp_id}
DELETE /opportunities/{opp_id}
PUT /opportunities/{opp_id}/status
PUT /opportunities/{opp_id}/upsert/customField
```

---

**This is the complete, up-to-date technology context.**

Last Updated: October 27, 2025