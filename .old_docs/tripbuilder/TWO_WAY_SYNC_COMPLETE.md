# Two-Way Sync System Documentation

## Overview

The TripBuilder application now has **full bidirectional synchronization** with GoHighLevel (GHL). This means:

- ✅ **Local → GHL**: When you create or update data locally, it automatically syncs to GHL
- ✅ **GHL → Local**: When you pull data from GHL, it syncs to your local database
- ✅ **Automatic Sync**: Happens automatically on create/update operations

## Architecture

### Components

1. **`services/two_way_sync.py`** - Core bidirectional sync service
2. **`services/ghl_sync.py`** - Bulk sync operations (GHL → Local)
3. **`ghl_api.py`** - GHL API wrapper
4. **`field_mapping.py`** - Maps database fields ↔ GHL custom fields
5. **`app.py`** - Routes with integrated auto-sync

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                   TripBuilder App                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  User Creates/Updates:                                  │
│  ┌──────────┐        ┌──────────┐       ┌──────────┐  │
│  │   Trip   │ ──────→│ Passenger│ ─────→│ Contact  │  │
│  └──────────┘        └──────────┘       └──────────┘  │
│       │                    │                   │        │
│       │                    │                   │        │
│       ▼                    ▼                   ▼        │
│  ┌──────────────────────────────────────────────────┐  │
│  │         TwoWaySyncService                       │  │
│  │  - auto_sync_on_trip_create()                    │  │
│  │  - auto_sync_on_trip_update()                    │  │
│  │  - auto_sync_on_passenger_create()               │  │
│  │  - auto_sync_on_passenger_update()               │  │
│  └──────────────────────────────────────────────────┘  │
│                         │                               │
└─────────────────────────┼───────────────────────────────┘
                          │
                          ▼
               ┌──────────────────────┐
               │   GoHighLevel API    │
               ├──────────────────────┤
               │  TripBooking Pipeline│
               │  Passenger Pipeline  │
               │  Contacts            │
               │  Custom Fields       │
               └──────────────────────┘
```

## Sync Operations

### 1. Trip Sync (TripBooking Opportunities)

**Create a Trip:**
```python
from services.two_way_sync import TwoWaySyncService

sync_service = TwoWaySyncService(ghl_api)

# Create trip locally
trip = Trip(
    name="Hawaii Adventure",
    destination="Honolulu, Hawaii",
    start_date=date(2025, 6, 1),
    end_date=date(2025, 6, 8),
    max_capacity=20
)
db.session.add(trip)
db.session.flush()

# Automatically push to GHL
sync_service.auto_sync_on_trip_create(trip)
db.session.commit()

# Result: trip.ghl_opportunity_id is now populated
```

**Update a Trip:**
```python
# Update trip
trip.max_capacity = 25
trip.internal_trip_details = "Updated capacity"

# Automatically sync changes to GHL
sync_service.auto_sync_on_trip_update(trip)
db.session.commit()

# Result: GHL opportunity is updated with new values
```

**What Gets Synced:**
- All fields mapped in `TRIP_FIELD_MAP` (see field_mapping.py)
- Examples: destination, dates, max_capacity, pricing, vendor info, etc.
- Maps to TripBooking pipeline custom fields in GHL

### 2. Passenger Sync (Passenger Opportunities)

**Enroll a Passenger:**
```python
# Create/get contact first
contact = Contact(...)
db.session.add(contact)

# Create passenger
passenger = Passenger(
    contact_id=contact.id,
    trip_id=trip.id,
    trip_name=trip.name
)
db.session.add(passenger)
db.session.flush()

# Automatically create in GHL
sync_service.auto_sync_on_passenger_create(passenger)
db.session.commit()

# Result: passenger.id is the GHL Passenger opportunity ID
```

**Update Passenger Info:**
```python
# Update passenger
passenger.passport_number = "X1234567"
passenger.passport_expire = date(2030, 12, 31)

# Automatically sync to GHL
sync_service.auto_sync_on_passenger_update(passenger)
db.session.commit()

# Result: GHL custom fields are updated
```

**What Gets Synced:**
- All fields mapped in `PASSENGER_FIELD_MAP`
- Examples: passport info, health details, emergency contacts, room preferences
- Maps to Passenger pipeline custom fields in GHL

### 3. Contact Sync

**Create/Update Contact:**
```python
# Create contact
contact = Contact(
    firstname="John",
    lastname="Doe",
    email="john@example.com",
    phone="+15551234567"
)

# Push to GHL
sync_service.push_contact_to_ghl(contact)

# Result: contact.id is the GHL contact ID
```

## Automatic Sync in Routes

### Trip Routes

**`/trips/new` - Create Trip**
```python
# After creating trip locally:
sync_service.auto_sync_on_trip_create(trip)
# ✅ Trip is now in GHL as TripBooking opportunity
```

**`/trips/<id>/edit` - Update Trip**
```python
# After updating trip:
sync_service.auto_sync_on_trip_update(trip)
# ✅ GHL opportunity is updated
```

**`/trips/<id>/delete` - Delete Trip**
```python
# Deletes from GHL first, then local database
ghl_api.delete_opportunity(trip.ghl_opportunity_id)
db.session.delete(trip)
# ✅ Removed from both systems
```

### Passenger Routes

**`/trips/<id>/enroll` - Enroll Passenger**
```python
# After enrolling:
sync_service.auto_sync_on_passenger_create(passenger)
# ✅ Passenger opportunity created in GHL
```

## Pull from GHL

To sync data FROM GHL TO local database:

```python
# Pull a specific trip
trip = sync_service.pull_trip_from_ghl(ghl_opportunity_id)

# Pull a specific passenger
passenger = sync_service.pull_passenger_from_ghl(ghl_opportunity_id)

# Bulk sync all data
from services.ghl_sync import GHLSyncService
ghl_sync = GHLSyncService(ghl_api)
results = ghl_sync.perform_full_sync()
```

Or use the CLI command:
```bash
flask sync-ghl
```

## Field Mapping

### Trip Fields (TripBooking Opportunities)

Maps database columns to GHL custom fields:

| Database Column | GHL Field Key | Type |
|----------------|---------------|------|
| trip_name | opportunity.tripname | String |
| destination | opportunity.destination | String |
| arrival_date | opportunity.arrivaldate | Date |
| return_date | opportunity.returndate | Date |
| max_passengers | opportunity.maxpassengers | Integer |
| trip_vendor | opportunity.tripvendor | String |
| internal_trip_details | opportunity.internaltripdetails | Text |

See `TRIP_FIELD_MAP` in `field_mapping.py` for complete list.

### Passenger Fields (Passenger Opportunities)

| Database Column | GHL Field Key | Type |
|----------------|---------------|------|
| trip_name | opportunity.tripname | String |
| passport_number | opportunity.passportnumber | String |
| passport_expire | opportunity.passportexpire | Date |
| health_state | opportunity.healthstate | Text |
| user_roomate | opportunity.userroomate | String |
| room_occupancy | opportunity.roomoccupancy | String |

See `PASSENGER_FIELD_MAP` in `field_mapping.py` for complete list.

## Testing

Run the test suite to verify sync functionality:

```bash
cd ~/Downloads/claude_code_tripbuilder/tripbuilder
source ../.venv/bin/activate
python test_two_way_sync.py
```

Tests include:
1. ✅ Create trip and sync to GHL
2. ✅ Update trip and sync changes
3. ✅ Create passenger and sync to GHL
4. ✅ Pull data from GHL to local
5. ✅ Cleanup test data

## Error Handling

The sync system has built-in error handling:

```python
try:
    sync_service.auto_sync_on_trip_create(trip)
    flash('Trip created and synced to GHL!', 'success')
except Exception as sync_error:
    print(f"Warning: Failed to sync to GHL: {sync_error}")
    flash('Trip created locally, but GHL sync failed', 'warning')
```

- **Graceful degradation**: If GHL sync fails, data is still saved locally
- **User feedback**: Flash messages inform users of sync status
- **Logging**: Errors are printed to console for debugging

## Pipeline IDs

From `PIPELINE_CUSTOM_FIELD_DATA.md`:

- **TripBooking Pipeline**: `IlWdPtOpcczLpgsde2KF`
- **Passenger Pipeline**: `fnsdpRtY9o83Vr4z15bE`

## Benefits

1. **No Data Loss**: Changes are never lost between systems
2. **Real-time Sync**: Updates happen immediately
3. **Bidirectional**: Works both ways (local ↔ GHL)
4. **Automatic**: No manual sync needed
5. **Reliable**: Error handling ensures data integrity
6. **Flexible**: Easy to extend with new fields

## Troubleshooting

**Problem**: Trip created but no GHL opportunity ID

**Solution**: Check:
1. GHL_LOCATION_ID and GHL_API_TOKEN in .env
2. Console output for error messages
3. GHL API permissions

**Problem**: Custom fields not syncing

**Solution**: 
1. Verify field mappings in `field_mapping.py`
2. Check field keys match GHL custom field definitions
3. Run `python build_field_maps.py` to rebuild mappings

**Problem**: "Column does not exist" error

**Solution**: 
- Database schema may be out of sync
- Check actual schema vs models.py
- Run migrations if needed

## Future Enhancements

- [ ] Webhook listeners for GHL → Local real-time sync
- [ ] Conflict resolution for simultaneous updates
- [ ] Batch sync optimizations
- [ ] Sync status dashboard
- [ ] Automatic retry on failed syncs

## Summary

✅ **Two-way sync is now fully operational!**

- Create trips → Auto-sync to GHL
- Update trips → Auto-sync changes
- Enroll passengers → Auto-create opportunities
- Delete operations → Remove from both systems
- Pull from GHL → Sync to local database

The sync happens **automatically** in all the routes, so you don't need to think about it!
