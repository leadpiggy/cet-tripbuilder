"""
TripBuilder Flask Application

Main application file with routes, configuration, and CLI commands.
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and GHL API
from models import db, Trip, Contact, Passenger, Pipeline, PipelineStage, CustomField, CustomFieldGroup, SyncLog, File
from ghl_api import GoHighLevelAPI
from services.two_way_sync import TwoWaySyncService
from services.file_manager import file_manager

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tripbuilder.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize GHL API
ghl_api = GoHighLevelAPI(
    location_id=os.getenv('GHL_LOCATION_ID'),
    api_key=os.getenv('GHL_API_TOKEN')
)

# Initialize Two-Way Sync Service
sync_service = TwoWaySyncService(ghl_api)

# =====================================================================
# CONTEXT PROCESSORS
# =====================================================================

@app.context_processor
def inject_dropdown_options():
    """
    Make dropdown options from GHL custom fields available to all templates.
    
    These are populated during GHL sync and cached in CustomField.options.
    Use in templates like: {{ travel_categories }}, {{ passport_countries }}
    """
    def get_field_options(field_key):
        """Helper to get options for a custom field"""
        field = CustomField.query.filter_by(field_key=field_key).first()
        return field.options if field and field.options else []
    
    return {
        'travel_categories': get_field_options('opportunity.travelcategory'),
        'passport_countries': get_field_options('opportunity.passportcountry'),
        'birth_countries': get_field_options('opportunity.birthcountry'),
        'get_field_options': get_field_options  # Function available in templates
    }


@app.context_processor
def inject_vendors():
    """Make all vendors available to templates for dropdown population"""
    from models import TripVendor
    return {
        'all_vendors': TripVendor.query.order_by(TripVendor.name).all()
    }



# =====================================================================
# CLI COMMANDS
# =====================================================================

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")


@app.cli.command('sync-ghl')
def sync_ghl_command():
    """Sync all data from GoHighLevel (Stage 2A)"""
    from services.ghl_sync import GHLSyncService
    
    print("🔄 Starting GHL sync...")
    sync_service = GHLSyncService(ghl_api)
    
    try:
        results = sync_service.perform_full_sync()
        
        print("\n✅ Sync complete!")
        print(f"  Pipelines: {results.get('pipelines', 0)}")
        print(f"  Stages: {results.get('stages', 0)}")
        print(f"  Custom Field Groups: {results.get('groups', 0)}")
        print(f"  Custom Fields: {results.get('fields', 0)}")
        print(f"  Contacts: {results.get('contacts', 0)}")
        print(f"  Trips: {results.get('trips', 0)}")
        print(f"  Passengers: {results.get('passengers', 0)}")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {str(e)}")


# =====================================================================
# ROUTES
# =====================================================================

@app.route('/')
def index():
    """Dashboard - Overview of trips, passengers, and stats"""
    # Get counts
    trip_count = Trip.query.count()
    contact_count = Contact.query.count()
    passenger_count = Passenger.query.count()
    
    # Get recent trips
    recent_trips = Trip.query.order_by(Trip.created_at.desc()).limit(5).all()
    
    # Get pipeline stats (if synced)
    pipelines = Pipeline.query.all()
    
    return render_template('index.html',
                         trip_count=trip_count,
                         contact_count=contact_count,
                         passenger_count=passenger_count,
                         recent_trips=recent_trips,
                         pipelines=pipelines)


# =====================================================================
# TRIP ROUTES
# =====================================================================

@app.route('/trips')
def trip_list():
    """List all trips with search and filter support"""
    # Start with base query
    query = Trip.query
    
    # Get search parameters
    search_term = request.args.get('search', '').strip()
    destination = request.args.get('destination', '').strip()
    start_date_from = request.args.get('start_date_from', '').strip()
    start_date_to = request.args.get('start_date_to', '').strip()
    status = request.args.get('status', '').strip()
    travel_category = request.args.get('travel_category', '').strip()
    min_capacity = request.args.get('min_capacity', '').strip()
    max_capacity = request.args.get('max_capacity', '').strip()
    passenger_search = request.args.get('passenger_search', '').strip()
    
    # Apply general search (searches multiple fields)
    if search_term:
        search_filter = db.or_(
            Trip.destination.ilike(f'%{search_term}%'),
            Trip.name.ilike(f'%{search_term}%'),
            Trip.trip_description.ilike(f'%{search_term}%'),
            Trip.internal_trip_details.ilike(f'%{search_term}%'),
            Trip.travel_category.ilike(f'%{search_term}%'),
            Trip.trip_vendor.ilike(f'%{search_term}%')
        )
        query = query.filter(search_filter)
    
    # Apply specific filters
    if destination:
        query = query.filter(Trip.destination.ilike(f'%{destination}%'))
    
    if start_date_from:
        try:
            date_from = datetime.strptime(start_date_from, '%Y-%m-%d').date()
            query = query.filter(Trip.start_date >= date_from)
        except ValueError:
            pass
    
    if start_date_to:
        try:
            date_to = datetime.strptime(start_date_to, '%Y-%m-%d').date()
            query = query.filter(Trip.start_date <= date_to)
        except ValueError:
            pass
    
    if status:
        query = query.filter(Trip.status == status)
    
    if travel_category:
        query = query.filter(Trip.travel_category.ilike(f'%{travel_category}%'))
    
    if min_capacity:
        try:
            query = query.filter(Trip.max_passengers >= int(min_capacity))
        except ValueError:
            pass
    
    if max_capacity:
        try:
            query = query.filter(Trip.max_passengers <= int(max_capacity))
        except ValueError:
            pass
    
    # Filter by passenger name (joins with passengers and contacts)
    if passenger_search:
        query = query.join(Passenger).join(Contact).filter(
            db.or_(
                Contact.firstname.ilike(f'%{passenger_search}%'),
                Contact.lastname.ilike(f'%{passenger_search}%'),
                Passenger.firstname.ilike(f'%{passenger_search}%'),
                Passenger.lastname.ilike(f'%{passenger_search}%')
            )
        ).distinct()
    
    # Get all trips matching the filters
    trips = query.order_by(Trip.start_date.desc()).all()
    
    # Get unique values for filter dropdowns
    all_destinations = db.session.query(Trip.destination).distinct().filter(Trip.destination.isnot(None)).all()
    all_categories = db.session.query(Trip.travel_category).distinct().filter(Trip.travel_category.isnot(None)).all()
    all_statuses = db.session.query(Trip.status).distinct().filter(Trip.status.isnot(None)).all()
    
    return render_template('trips/list.html', 
                         trips=trips,
                         search_term=search_term,
                         destination=destination,
                         start_date_from=start_date_from,
                         start_date_to=start_date_to,
                         status=status,
                         travel_category=travel_category,
                         min_capacity=min_capacity,
                         max_capacity=max_capacity,
                         passenger_search=passenger_search,
                         all_destinations=[d[0] for d in all_destinations],
                         all_categories=[c[0] for c in all_categories],
                         all_statuses=[s[0] for s in all_statuses])


@app.route('/trips/new', methods=['GET', 'POST'])
def trip_new():
    """Create a new trip (public form)"""
    if request.method == 'GET':
        return render_template('trips/form.html', trip=None)
    
    # Create trip
    try:
        # Get vendor ID (empty string becomes None)
        trip_vendor_id = request.form.get('trip_vendor_id')
        trip_vendor_id = int(trip_vendor_id) if trip_vendor_id and trip_vendor_id.isdigit() else None
        
        trip = Trip(
            destination=request.form['destination'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
            max_passengers=int(request.form.get('max_passengers', 10)),
            internal_trip_details=request.form.get('internal_trip_details', ''),
            trip_vendor_id=trip_vendor_id
        )
        
        # Set name if provided
        if request.form.get('name'):
            trip.name = request.form['name']
        else:
            trip.name = f"{trip.destination} - {trip.start_date}"
        
        db.session.add(trip)
        db.session.flush()  # Get trip.id
        
        # ✅ AUTO-SYNC: Push to GHL
        try:
            sync_service.auto_sync_on_trip_create(trip)
            flash(f'Trip to {trip.destination} created and synced to GHL!', 'success')
        except Exception as sync_error:
            print(f"Warning: Failed to sync to GHL: {sync_error}")
            flash(f'Trip created locally, but GHL sync failed: {str(sync_error)}', 'warning')
        
        db.session.commit()
        return redirect(url_for('trip_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating trip: {str(e)}', 'error')
        return render_template('trips/form.html', trip=None)


@app.route('/trips/<int:trip_id>')
def trip_detail(trip_id):
    """Trip detail page with passengers"""
    trip = Trip.query.get_or_404(trip_id)
    ghl_location_id = os.getenv('GHL_LOCATION_ID')
    return render_template('trips/detail.html', trip=trip, ghl_location_id=ghl_location_id)


@app.route('/trips/<int:trip_id>/edit', methods=['GET', 'POST'])
def trip_edit(trip_id):
    """Edit a trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'GET':
        return render_template('trips/form.html', trip=trip)
    
    try:
        # Get vendor ID (empty string becomes None)
        trip_vendor_id = request.form.get('trip_vendor_id')
        trip.trip_vendor_id = int(trip_vendor_id) if trip_vendor_id and trip_vendor_id.isdigit() else None
        
        trip.destination = request.form['destination']
        trip.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        trip.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        trip.max_passengers = int(request.form.get('max_passengers', 10))
        trip.internal_trip_details = request.form.get('internal_trip_details', '')
        trip.updated_at = datetime.utcnow()
        
        # Update name if provided
        if request.form.get('name'):
            trip.name = request.form['name']
        
        # ✅ AUTO-SYNC: Push updates to GHL
        try:
            sync_service.auto_sync_on_trip_update(trip)
            flash('Trip updated and synced to GHL!', 'success')
        except Exception as sync_error:
            print(f"Warning: Failed to sync to GHL: {sync_error}")
            flash(f'Trip updated locally, but GHL sync failed: {str(sync_error)}', 'warning')
        
        db.session.commit()
        return redirect(url_for('trip_detail', trip_id=trip.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating trip: {str(e)}', 'error')
        return render_template('trips/form.html', trip=trip)


@app.route('/trips/<int:trip_id>/delete', methods=['POST'])
def trip_delete(trip_id):
    """Delete a trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    try:
        # ✅ AUTO-SYNC: Delete from GHL first
        if trip.ghl_opportunity_id:
            try:
                ghl_api.delete_opportunity(trip.ghl_opportunity_id)
                print(f"Deleted TripBooking opportunity {trip.ghl_opportunity_id} from GHL")
            except Exception as ghl_error:
                print(f"Warning: Failed to delete from GHL: {ghl_error}")
        
        # Delete passengers from GHL
        for passenger in trip.passengers:
            if passenger.id:
                try:
                    ghl_api.delete_opportunity(passenger.id)
                    print(f"Deleted Passenger opportunity {passenger.id} from GHL")
                except Exception as ghl_error:
                    print(f"Warning: Failed to delete passenger from GHL: {ghl_error}")
        
        destination = trip.destination
        
        # Delete from local database (cascades to passengers)
        db.session.delete(trip)
        db.session.commit()
        
        flash(f'Trip to {destination} deleted from database and GHL.', 'info')
        return redirect(url_for('trip_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting trip: {str(e)}', 'error')
        return redirect(url_for('trip_detail', trip_id=trip.id))


# =====================================================================
# PASSENGER ROUTES
# =====================================================================

@app.route('/trips/<int:trip_id>/enroll', methods=['GET', 'POST'])
def enroll_passenger(trip_id):
    """Enroll a passenger in a trip (public form)"""
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'GET':
        return render_template('passengers/enroll.html', trip=trip)
    
    # Get or create contact
    from services.ghl_sync import GHLSyncService
    ghl_sync = GHLSyncService(ghl_api)
    
    contact_data = {
        'firstname': request.form['firstname'],
        'lastname': request.form['lastname'],
        'email': request.form['email'],
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'postal_code': request.form.get('postal_code'),
        'country': request.form.get('country', 'United States')
    }
    
    try:
        # Get or create contact (syncs with GHL)
        contact = ghl_sync.get_or_create_contact(contact_data)
        
        # Create passenger record
        passenger = Passenger(
            contact_id=contact.id,
            trip_id=trip.id,
            trip_name=trip.name
        )
        
        db.session.add(passenger)
        db.session.flush()  # Get passenger.id if auto-assigned
        
        # ✅ AUTO-SYNC: Create Passenger opportunity in GHL
        try:
            sync_service.auto_sync_on_passenger_create(passenger)
            flash(f'{contact.firstname} {contact.lastname} enrolled and synced to GHL!', 'success')
        except Exception as sync_error:
            print(f"Warning: Failed to sync passenger to GHL: {sync_error}")
            flash(f'Passenger enrolled locally, but GHL sync failed: {str(sync_error)}', 'warning')
        
        db.session.commit()
        return redirect(url_for('trip_detail', trip_id=trip.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error enrolling passenger: {str(e)}', 'error')
        return render_template('passengers/enroll.html', trip=trip)


@app.route('/passengers/<passenger_id>')
def passenger_detail(passenger_id):
    """Passenger detail page"""
    passenger = Passenger.query.get_or_404(passenger_id)
    ghl_location_id = os.getenv('GHL_LOCATION_ID')
    return render_template('passengers/detail.html', passenger=passenger, ghl_location_id=ghl_location_id)


# =====================================================================
# CONTACT ROUTES
# =====================================================================

@app.route('/contacts')
def contact_list():
    """List all contacts (TODO)"""
    contacts = Contact.query.order_by(Contact.lastname, Contact.firstname).all()
    return render_template('contacts/list.html', contacts=contacts)


@app.route('/contacts/<contact_id>')
def contact_detail(contact_id):
    """Contact detail page"""
    contact = Contact.query.get_or_404(contact_id)
    ghl_location_id = os.getenv('GHL_LOCATION_ID')
    return render_template('contacts/detail.html', contact=contact, ghl_location_id=ghl_location_id)


# =====================================================================
# FILE UPLOAD ROUTES
# =====================================================================

@app.route('/upload/passport/<passenger_id>', methods=['POST'])
def upload_passport(passenger_id):
    """Upload passport photo for a passenger"""
    passenger = Passenger.query.get_or_404(passenger_id)
    
    if 'passport' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('passenger_detail', passenger_id=passenger_id))
    
    file = request.files['passport']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('passenger_detail', passenger_id=passenger_id))
    
    try:
        # Build S3 path
        passenger_name = f"{passenger.firstname}_{passenger.lastname}"
        trip_name = passenger.trip.name if passenger.trip else "unassigned"
        s3_path = file_manager.build_s3_path(
            trip_name,
            passenger_name,
            'passports',
            file.filename
        )
        
        # Upload to S3
        success = file_manager.upload_file(
            file,
            s3_path,
            content_type=file.content_type,
            make_public=False  # Private by default
        )
        
        if success:
            # Save file record
            file_record = File(
                filename=file.filename,
                s3_key=s3_path,
                file_type='passport',
                content_type=file.content_type,
                file_size=file.content_length if hasattr(file, 'content_length') else None,
                is_public=False,
                opportunity_type='passenger',
                passenger_id=passenger_id,
                trip_id=passenger.trip_id,
                uploaded_by=passenger.contact_id
            )
            db.session.add(file_record)
            
            # Update passenger record
            passenger.passport_file = s3_path
            passenger.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Passport photo uploaded successfully!', 'success')
        else:
            flash('Failed to upload file to S3', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Upload error: {str(e)}', 'error')
    
    return redirect(url_for('passenger_detail', passenger_id=passenger_id))


@app.route('/upload/signature/<passenger_id>', methods=['POST'])
def upload_signature(passenger_id):
    """Save digital signature for a passenger"""
    passenger = Passenger.query.get_or_404(passenger_id)
    
    try:
        # Get signature data from JSON request
        import json
        import base64
        import io
        
        data = request.get_json()
        signature_data = data.get('signature')
        
        if not signature_data:
            return {'success': False, 'error': 'No signature data'}, 400
        
        # Decode base64 signature
        signature_bytes = base64.b64decode(signature_data.split(',')[1])
        
        # Build S3 path
        passenger_name = f"{passenger.firstname}_{passenger.lastname}"
        trip_name = passenger.trip.name if passenger.trip else "unassigned"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_path = f"trips/{trip_name}/passengers/{passenger_name}/signatures/signature_{timestamp}.png"
        
        # Upload to S3
        success = file_manager.upload_file(
            io.BytesIO(signature_bytes),
            s3_path,
            content_type='image/png',
            make_public=False
        )
        
        if success:
            # Save file record
            file_record = File(
                filename=f'signature_{timestamp}.png',
                s3_key=s3_path,
                file_type='signature',
                content_type='image/png',
                file_size=len(signature_bytes),
                is_public=False,
                opportunity_type='passenger',
                passenger_id=passenger_id,
                trip_id=passenger.trip_id,
                uploaded_by=passenger.contact_id
            )
            db.session.add(file_record)
            
            # Update passenger record
            passenger.passenger_signature = s3_path
            passenger.updated_at = datetime.utcnow()
            
            db.session.commit()
            return {'success': True, 's3_path': s3_path}
        else:
            return {'success': False, 'error': 'S3 upload failed'}, 500
            
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500


@app.route('/upload/document/<passenger_id>', methods=['POST'])
def upload_document(passenger_id):
    """Upload document (PDF, etc.) for a passenger"""
    passenger = Passenger.query.get_or_404(passenger_id)
    
    if 'document' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('passenger_detail', passenger_id=passenger_id))
    
    file = request.files['document']
    document_type = request.form.get('document_type', 'document')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('passenger_detail', passenger_id=passenger_id))
    
    try:
        # Build S3 path
        passenger_name = f"{passenger.firstname}_{passenger.lastname}"
        trip_name = passenger.trip.name if passenger.trip else "unassigned"
        s3_path = file_manager.build_s3_path(
            trip_name,
            passenger_name,
            'documents',
            file.filename
        )
        
        # Upload to S3
        success = file_manager.upload_file(
            file,
            s3_path,
            content_type=file.content_type,
            make_public=False
        )
        
        if success:
            # Save file record
            file_record = File(
                filename=file.filename,
                s3_key=s3_path,
                file_type=document_type,
                content_type=file.content_type,
                file_size=file.content_length if hasattr(file, 'content_length') else None,
                is_public=False,
                opportunity_type='passenger',
                passenger_id=passenger_id,
                trip_id=passenger.trip_id,
                uploaded_by=passenger.contact_id
            )
            db.session.add(file_record)
            
            # Update passenger record based on document type
            if document_type == 'reservation':
                passenger.reservation = s3_path
            elif document_type == 'mou':
                passenger.mou = s3_path
            elif document_type == 'affidavit':
                passenger.affidavit = s3_path
            
            passenger.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash(f'{document_type.title()} uploaded successfully!', 'success')
        else:
            flash('Failed to upload file to S3', 'error')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Upload error: {str(e)}', 'error')
    
    return redirect(url_for('passenger_detail', passenger_id=passenger_id))


@app.route('/files/<int:file_id>/download')
def download_file(file_id):
    """Generate download URL for a file"""
    file_record = File.query.get_or_404(file_id)
    
    # Generate pre-signed download URL (valid for 1 hour)
    download_url = file_manager.generate_download_url(file_record.s3_key, expiration=3600)
    
    if download_url:
        return redirect(download_url)
    else:
        flash('Could not generate download URL', 'error')
        return redirect(request.referrer or url_for('index'))


@app.route('/files/list/<entity_type>/<entity_id>')
def list_files(entity_type, entity_id):
    """List all files for a trip or passenger"""
    if entity_type == 'trip':
        files = File.query.filter_by(trip_id=entity_id).order_by(File.uploaded_at.desc()).all()
    elif entity_type == 'passenger':
        files = File.query.filter_by(passenger_id=entity_id).order_by(File.uploaded_at.desc()).all()
    else:
        files = []
    
    from flask import jsonify
    return jsonify([{
        'id': f.id,
        'filename': f.filename,
        'file_type': f.file_type,
        'content_type': f.content_type,
        'file_size': f.file_size,
        'uploaded_at': f.uploaded_at.isoformat() if f.uploaded_at else None,
        'download_url': url_for('download_file', file_id=f.id, _external=True)
    } for f in files])


@app.route('/ghl-webhook', methods=['POST'])
def ghl_webhook():
    """
    GHL webhook endpoint for file uploads
    Generates pre-signed upload URLs for GoHighLevel to upload files directly to S3
    """
    data = request.json
    
    # TODO: Implement GHL signature validation
    # See: https://highlevel.stoplight.io/docs/integrations/ZG9jOjE1ODU0MTQz-webhook-signature
    
    # Extract file details from webhook
    file_name = data.get('file_name')
    contact_id = data.get('contact_id')
    file_type = data.get('file_type', 'application/pdf')
    
    if not file_name or not contact_id:
        return {'error': 'Missing required fields'}, 400
    
    try:
        # Build S3 path for GHL uploads
        s3_path = f"ghl-uploads/{contact_id}/{file_name}"
        
        # Generate pre-signed upload URL
        upload_url = file_manager.generate_upload_url(s3_path, content_type=file_type)
        
        if upload_url:
            return {
                'upload_url': upload_url,
                'contact_id': contact_id,
                'file_name': file_name,
                'file_type': file_type
            }
        else:
            return {'error': 'Could not generate upload URL'}, 500
    except Exception as e:
        return {'error': str(e)}, 500

# =====================================================================
# ENROLLMENT WIZARD ROUTES
# =====================================================================

@app.route('/trips/<int:trip_id>/enroll/start')
def enrollment_start(trip_id):
    """Initialize enrollment wizard session"""
    from flask import session
    trip = Trip.query.get_or_404(trip_id)
    
    # Initialize wizard session
    session['enrollment_wizard'] = {
        'trip_id': trip_id,
        'current_step': 1,
        'step_1_complete': False,
        'step_2_complete': False,
        'step_3_complete': False,
        'step_4_complete': False,
        'step_5_complete': False,
        'contact_id': None,
        'data': {}
    }
    
    return redirect(url_for('enrollment_step', trip_id=trip_id, step=1))


@app.route('/trips/<int:trip_id>/enroll/step/<int:step>', methods=['GET', 'POST'])
def enrollment_step(trip_id, step):
    """Handle enrollment wizard steps"""
    from flask import session
    from forms import (Step2PassengerInfoForm, Step3PassportInfoForm, 
                      Step4HealthInfoForm, Step5SignatureForm, populate_form_choices)
    from constants import RESPONSIBILITY_STATEMENT
    
    trip = Trip.query.get_or_404(trip_id)
    wizard = session.get('enrollment_wizard')
    
    # Redirect to start if no session
    if not wizard or wizard['trip_id'] != trip_id:
        return redirect(url_for('enrollment_start', trip_id=trip_id))
    
    # Handle POST - save step data
    if request.method == 'POST':
        # Validate step
        form = None
        if step == 2:
            form = Step2PassengerInfoForm()
            populate_form_choices(form)
        elif step == 3:
            form = Step3PassportInfoForm()
            populate_form_choices(form)
        elif step == 4:
            form = Step4HealthInfoForm()
        elif step == 5:
            form = Step5SignatureForm()
            populate_form_choices(form)
        
        if form and form.validate_on_submit():
            # Save step data to session
            wizard['data'][f'step_{step}'] = request.form.to_dict()
            wizard[f'step_{step}_complete'] = True
            
            # For step 2, create or find contact
            if step == 2:
                from services.ghl_sync import GHLSyncService
                ghl_sync = GHLSyncService(ghl_api)
                
                contact_data = {
                    'firstname': request.form['first_name'],
                    'lastname': request.form['last_name'],
                    'email': request.form['user_email'],
                    'phone': request.form.get('user_phone'),
                    'address': request.form.get('mailing_address'),
                    'city': request.form.get('user_city'),
                    'state': request.form.get('user_state'),
                    'postal_code': request.form.get('user_zip')
                }
                
                try:
                    contact = ghl_sync.get_or_create_contact(contact_data)
                    wizard['contact_id'] = contact.id
                except Exception as e:
                    flash(f'Error with contact: {e}', 'error')
                    return redirect(url_for('enrollment_step', trip_id=trip_id, step=step))
            
            session['enrollment_wizard'] = wizard
            
            # Redirect to next step or completion
            if step < 5:
                return redirect(url_for('enrollment_step', trip_id=trip_id, step=step+1))
            else:
                return redirect(url_for('enrollment_complete', trip_id=trip_id))
        else:
            # Form validation failed
            flash('Please correct the errors below', 'error')
    
    # GET request or validation failed - show form
    wizard['current_step'] = step
    session['enrollment_wizard'] = wizard
    
    # Create form instance with saved data
    form = None
    saved_data = wizard['data'].get(f'step_{step}', {})
    
    if step == 2:
        form = Step2PassengerInfoForm(data=saved_data)
        populate_form_choices(form)
    elif step == 3:
        form = Step3PassportInfoForm(data=saved_data)
        populate_form_choices(form)
    elif step == 4:
        form = Step4HealthInfoForm(data=saved_data)
    elif step == 5:
        form = Step5SignatureForm(data=saved_data)
        populate_form_choices(form)
    
    # Template names
    template_map = {
        1: 'enrollment/step_1_trip_info.html',
        2: 'enrollment/step_2_passenger.html',
        3: 'enrollment/step_3_passport.html',
        4: 'enrollment/step_4_health.html',
        5: 'enrollment/step_5_signature.html'
    }
    
    return render_template(
        template_map.get(step, 'enrollment/step_1_trip_info.html'),
        trip=trip,
        wizard=wizard,
        current_step=step,
        form=form,
        responsibility_statement=RESPONSIBILITY_STATEMENT,
        current_date=datetime.utcnow()
    )


@app.route('/trips/<int:trip_id>/enroll/complete', methods=['POST'])
def enrollment_complete(trip_id):
    """Complete enrollment - create passenger record with all data"""
    from flask import session
    from services.pdf_generator import pdf_generator
    import base64
    import io
    
    trip = Trip.query.get_or_404(trip_id)
    wizard = session.get('enrollment_wizard')
    
    if not wizard or wizard['trip_id'] != trip_id:
        flash('Enrollment session expired. Please start again.', 'error')
        return redirect(url_for('enrollment_start', trip_id=trip_id))
    
    try:
        # Combine all step data
        all_data = {}
        for step_key, step_data in wizard['data'].items():
            all_data.update(step_data)
        
        # Add final form data
        all_data.update(request.form.to_dict())
        
        # Create passenger
        passenger = Passenger(
            contact_id=wizard['contact_id'],
            trip_id=trip_id,
            trip_name=trip.name,
            
            # From Step 2
            firstname=all_data.get('first_name'),
            lastname=all_data.get('last_name'),
            email=all_data.get('user_email'),
            phone=all_data.get('user_phone') or all_data.get('mob_number'),
            
            # From Step 3
            passport_number=all_data.get('passport_number'),
            date_of_birth=datetime.strptime(all_data['user_dob'], '%Y-%m-%d').date() if all_data.get('user_dob') else None,
            gender=all_data.get('gender'),
            passport_expire=datetime.strptime(all_data['passport_expire'], '%Y-%m-%d').date() if all_data.get('passport_expire') else None,
            passport_country=all_data.get('passport_country'),
            
            # From Step 4
            health_state=all_data.get('health_state'),
            health_medical_info=all_data.get('health_medical_info'),
            primary_phy=all_data.get('primary_phy'),
            physician_phone=all_data.get('physician_phone'),
            medication_list=all_data.get('medication_list'),
            
            # Room preferences
            room_occupancy=all_data.get('choose_occupancy'),
            user_roomate=all_data.get('user_roomate'),
            
            # From Step 5
            contact1_ufirst_name=all_data.get('contact1_ufirst_name'),
            contact1_ulast_name=all_data.get('contact1_ulast_name'),
            contact1_urelationship=all_data.get('contact1_urelationship'),
            contact1_umailing_address=all_data.get('contact1_umailing_address'),
            contact1_ucity=all_data.get('contact1_ucity'),
            contact1_ustate=all_data.get('contact1_ustate'),
            contact1_uzip=all_data.get('contact1_uzip'),
            contact1_uemail=all_data.get('contact1_uemail'),
            contact1_uphone=all_data.get('contact1_uphone'),
            contact1_umob_number=all_data.get('contact1_umob_number'),
            
            # Travel category
            travel_category_license=all_data.get('travel_category_license'),
            
            # Form submission
            form_submitted_date=datetime.utcnow().date(),
            registration_completed=True
        )
        
        # Copy travel category from trip
        if trip.travel_category:
            passenger.travel_category_license = trip.travel_category
        
        db.session.add(passenger)
        db.session.flush()  # Get passenger.id
        
        # Handle signature
        signature_data = all_data.get('signature_data')
        if signature_data:
            # Decode base64 signature
            signature_bytes = base64.b64decode(signature_data.split(',')[1])
            
            # Upload to S3
            passenger_name = f"{passenger.firstname}_{passenger.lastname}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_path = file_manager.build_s3_path(
                trip.name,
                passenger_name,
                'signatures',
                f'signature_{timestamp}.png'
            )
            
            file_manager.upload_file(
                io.BytesIO(signature_bytes),
                s3_path,
                content_type='image/png',
                make_public=False
            )
            
            passenger.passenger_signature = s3_path
        
        # Generate PDFs
        try:
            pdfs = pdf_generator.generate_all_pdfs(passenger, trip, passenger.passenger_signature)
            passenger.mou = pdfs.get('mou')
            passenger.affidavit = pdfs.get('affidavit')
            passenger.reservation = pdfs.get('reservation')
        except Exception as pdf_error:
            print(f"Warning: PDF generation failed: {pdf_error}")
            flash('Enrollment successful, but PDF generation failed. PDFs will be generated later.', 'warning')
        
        # Sync to GHL
        try:
            sync_service.auto_sync_on_passenger_create(passenger)
            flash(f'Enrollment complete for {passenger.firstname} {passenger.lastname}! Synced to GHL.', 'success')
        except Exception as sync_error:
            print(f"Warning: GHL sync failed: {sync_error}")
            flash(f'Enrollment complete locally, but GHL sync failed: {sync_error}', 'warning')
        
        db.session.commit()
        
        # Clear wizard session
        session.pop('enrollment_wizard', None)
        
        return redirect(url_for('passenger_detail', passenger_id=passenger.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Enrollment failed: {e}', 'error')
        print(f"Enrollment error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('enrollment_step', trip_id=trip_id, step=5))


@app.route('/enrollment/cancel')
def enrollment_cancel():
    """Cancel enrollment and clear session"""
    from flask import session
    trip_id = session.get('enrollment_wizard', {}).get('trip_id')
    session.pop('enrollment_wizard', None)
    
    flash('Enrollment cancelled', 'info')
    
    if trip_id:
        return redirect(url_for('trip_detail', trip_id=trip_id))
    return redirect(url_for('trip_list'))

# =====================================================================
# VENDOR ROUTES
# =====================================================================

@app.route('/vendors')
def vendor_list():
    """List all vendors"""
    from models import TripVendor
    vendors = TripVendor.query.order_by(TripVendor.name).all()
    return render_template('vendors/list.html', vendors=vendors)


@app.route('/vendors/new', methods=['GET', 'POST'])
def vendor_create():
    """Create a new vendor"""
    from models import TripVendor
    
    if request.method == 'GET':
        return render_template('vendors/form.html', vendor=None)
    
    try:
        vendor = TripVendor(
            name=request.form['name'],
            description=request.form.get('description', '')
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        # Note: SQLAlchemy event listener will auto-sync to GHL
        flash(f'Vendor "{vendor.name}" created successfully!', 'success')
        return redirect(url_for('vendor_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating vendor: {str(e)}', 'error')
        return render_template('vendors/form.html', vendor=None)


@app.route('/vendors/<int:vendor_id>/edit', methods=['GET', 'POST'])
def vendor_edit(vendor_id):
    """Edit a vendor"""
    from models import TripVendor
    vendor = TripVendor.query.get_or_404(vendor_id)
    
    if request.method == 'GET':
        return render_template('vendors/form.html', vendor=vendor)
    
    try:
        vendor.name = request.form['name']
        vendor.description = request.form.get('description', '')
        
        db.session.commit()
        flash(f'Vendor "{vendor.name}" updated successfully!', 'success')
        return redirect(url_for('vendor_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating vendor: {str(e)}', 'error')
        return render_template('vendors/form.html', vendor=vendor)


@app.route('/vendors/<int:vendor_id>/delete', methods=['POST'])
def vendor_delete(vendor_id):
    """Delete a vendor"""
    from models import TripVendor
    vendor = TripVendor.query.get_or_404(vendor_id)
    
    # Check if vendor is used by any trips
    if vendor.trips:
        flash(f'Cannot delete vendor "{vendor.name}" - it is assigned to {len(vendor.trips)} trip(s). Please reassign trips first.', 'error')
        return redirect(url_for('vendor_list'))
    
    try:
        vendor_name = vendor.name
        db.session.delete(vendor)
        db.session.commit()
        
        # Note: SQLAlchemy event listener will auto-sync to GHL
        flash(f'Vendor "{vendor_name}" deleted successfully.', 'info')
        return redirect(url_for('vendor_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting vendor: {str(e)}', 'error')
        return redirect(url_for('vendor_list'))


@app.route('/api/vendors/create', methods=['POST'])
def api_vendor_create():
    """Create vendor via AJAX (for modal in trip form)"""
    from models import TripVendor
    from flask import jsonify
    
    try:
        vendor = TripVendor(
            name=request.form['name'],
            description=request.form.get('description', '')
        )
        
        db.session.add(vendor)
        db.session.commit()
        
        # Note: SQLAlchemy event listener will auto-sync to GHL
        return jsonify({
            'success': True,
            'id': vendor.id,
            'name': vendor.name,
            'description': vendor.description
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# =====================================================================
# ADMIN ROUTES
# =====================================================================

@app.route('/admin/sync', methods=['POST'])
def admin_sync():
    """Trigger manual sync (TODO: Add to admin panel)"""
    from services.ghl_sync import GHLSyncService
    
    try:
        sync_service = GHLSyncService(ghl_api)
        results = sync_service.perform_full_sync()
        
        flash(f"Sync complete! Contacts: {results.get('contacts', 0)}, Pipelines: {results.get('pipelines', 0)}", 'success')
    except Exception as e:
        flash(f'Sync failed: {str(e)}', 'error')
    
    return redirect(url_for('index'))


# =====================================================================
# ERROR HANDLERS
# =====================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# =====================================================================
# RUN APPLICATION
# =====================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5270)
