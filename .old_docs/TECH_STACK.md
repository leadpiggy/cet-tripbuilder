# TripBuilder - Technical Stack

## Backend Architecture

### Core Framework
- **Python 3.x**: Primary language
- **Flask**: Web framework for routing, templating, and HTTP handling
- **SQLAlchemy**: ORM for backend database operations
- **Flask-SQLAlchemy**: Flask integration for SQLAlchemy
- **Flask-Login**: User authentication and session management
- **Flask-Migrate**: Database migration management

### Database Models
Defined in `base.py.txt`:
- **Trip**: Destination, start_date, end_date, notes
- **Contact**: Synced with GHL contacts (id, firstname, lastname, email, phone, tags)
- **Pipeline**: Two pipelines (TripBooking, Passenger)
- **PipelineStage**: 11 stages across both pipelines
- **CustomField**: 100+ field definitions with data types, options
- **CustomFieldGroup**: 13 field groupings
- **Passenger**: Junction model linking Contacts to Trips via Passenger opportunities

### GHL API Integration
- **ghl-api-wrapper-complete.py**: Pre-built Python class for GHL API v2.0
- **API Base URL**: `https://services.leadconnectorhq.com`
- **Version Header**: `Version: 2021-07-28`
- **Authentication**: Private Integration API token (Bearer)
- **Key API Endpoints**:
  - Contacts: Create, Read, Update, Delete, Search
  - Opportunities: Create, Update, Move through pipeline stages
  - Tasks: Create, Update, Mark complete, Delete
  - Custom Fields: Read field definitions and values, Update field values

## Frontend Stack

### Templating & UI
- **Jinja2**: Flask's default templating engine
- **Bootstrap 5**: Responsive UI framework (via CDN)
  - Forms, tables, navigation, modals, alerts
  - Grid system for layout
- **Bootstrap Icons**: Icon library for UI elements

### JavaScript
- **Bootstrap JS** (via CDN): Interactive components (modals, dropdowns, tooltips)
- **Minimal custom JS**: Form validation, confirmation dialogs, dynamic form elements

## Authentication & Security

### GHL Authentication
- **Private Integration Token**: Single sub-account scope, non-expiring
- **Storage**: Environment variable (`GHL_API_TOKEN`)
- **Authorization**: Bearer token in request headers

### Application Authentication
- **Flask-Login**: User session management
- **User Model**: Email/password with admin flag
- **Password Hashing**: Werkzeug security utilities
- **Login Required**: Decorator for protected routes

## Data Sources & Configuration

### CSV Data Files (for seeding/reference)
- `pipelines.csv`: 2 pipelines
- `pipeline_stages.csv`: 11 stages with IDs, names, positions, pipeline associations
- `custom_fields.csv`: Field definitions (name, data_type, field_key, options, placeholder)
- `custom_field_groups.csv`: Field group configurations with pipeline associations

### Environment Configuration
```
GHL_API_TOKEN=your_private_integration_token
GHL_LOCATION_ID=your_location_id
DATABASE_URL=sqlite:///tripbuilder.db (or PostgreSQL for production)
SECRET_KEY=your_flask_secret_key
```

## Dependencies (requirements.txt)

```
Flask>=2.3.0
Flask-SQLAlchemy>=3.0.0
Flask-Login>=0.6.0
Flask-Migrate>=4.0.0
SQLAlchemy>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
werkzeug>=2.3.0
```

## Application Structure

```
tripbuilder/
├── app.py                          # Main Flask application
├── ghl-api-wrapper-complete.py    # GHL API wrapper class
├── models/
│   └── base.py                     # SQLAlchemy models
├── templates/
│   ├── base.html                   # Base layout template
│   ├── trips/
│   │   ├── list.html              # All trips list
│   │   ├── detail.html            # Trip detail with passengers
│   │   └── form.html              # Create/edit trip
│   ├── contacts/
│   │   ├── list.html              # All contacts list
│   │   ├── detail.html            # Contact detail with trips
│   │   └── form.html              # Create/edit contact
│   └── passengers/
│       ├── add_to_trip.html       # Add passenger to trip
│       └── detail.html            # Passenger opportunity details
├── static/
│   ├── css/
│   │   └── custom.css             # Custom styles
│   └── js/
│       └── app.js                 # Custom JavaScript
├── data/
│   ├── pipelines.csv
│   ├── pipeline_stages.csv
│   ├── custom_fields.csv
│   └── custom_field_groups.csv
├── .env                            # Environment variables
├── requirements.txt
└── README.md
```

## API Wrapper Methods (Expected)

### Contacts
- `ghl.contacts.search(query, location_id)` → List[Contact]
- `ghl.contacts.get(contact_id)` → Contact
- `ghl.contacts.create(contact_data, location_id)` → Contact
- `ghl.contacts.update(contact_id, contact_data)` → Contact
- `ghl.contacts.delete(contact_id)` → Success

### Opportunities
- `ghl.opportunities.create(opportunity_data)` → Opportunity
- `ghl.opportunities.get(opportunity_id)` → Opportunity
- `ghl.opportunities.update(opportunity_id, data)` → Opportunity
- `ghl.opportunities.update_stage(opportunity_id, stage_id)` → Opportunity
- `ghl.opportunities.upsert_custom_field(opportunity_id, field_key, value)` → Success

### Tasks
- `ghl.tasks.get_all(contact_id)` → List[Task]
- `ghl.tasks.create(contact_id, task_data)` → Task
- `ghl.tasks.update(contact_id, task_id, data)` → Task
- `ghl.tasks.mark_complete(contact_id, task_id)` → Task
- `ghl.tasks.delete(contact_id, task_id)` → Success

### Custom Fields
- `ghl.custom_fields.get_by_location(location_id)` → List[CustomField]
- `ghl.custom_fields.update_value(model_id, field_key, value)` → Success

## Database Schema

### Trip Table
- `id` (Integer, PK)
- `destination` (String)
- `start_date` (Date)
- `end_date` (Date)
- `notes` (Text)
- `ghl_opportunity_id` (String) - Links to TripBooking opportunity
- `created_at`, `updated_at` (DateTime)

### Contact Table (Synced from GHL)
- `id` (String, PK) - GHL contact ID
- `firstname`, `lastname` (String)
- `email` (String, unique)
- `phone` (String)
- `tags` (Array[String])
- `business` (String)
- `created_at`, `updated_at` (DateTime)

### Passenger Table (Junction)
- `id` (String, PK) - GHL Passenger opportunity ID
- `contact_id` (FK → Contact)
- `trip_id` (FK → Trip)
- `stage_id` (FK → PipelineStage)
- `custom_field_values` (JSON) - Cached field data
- `created_at`, `updated_at` (DateTime)

## Deployment Considerations

### Development
- SQLite database for simplicity
- Flask development server
- Debug mode enabled

### Production
- PostgreSQL or MySQL database
- WSGI server (Gunicorn, uWSGI)
- Reverse proxy (Nginx)
- HTTPS/SSL certificates
- Environment-based configuration
- Rate limiting for GHL API calls
- Celery for background sync tasks (optional)