# Stage 2A Extended - Schema Update Complete ✅

## What Was Accomplished

### 1. ✅ Updated Database Schema
**Files Created/Modified:**
- `models.py` - Complete schema with all GHL custom fields mapped to columns
- `field_mapping.py` - Utility functions to convert between GHL format and DB columns
- `recreate_db.py` - Script to drop/recreate tables
- `models_old_backup.py` - Backup of old schema

**New Trip Model Fields:**
- All basic trip info (name, destination, description)
- All dates (start, end, arrival, return, deposit, final_payment)
- Capacity and passenger counts
- Pricing fields (base_price, trip_standard_level_pricing)
- Vendor info (trip_vendor, vendor_terms, travel_business_used)
- Trip details (travel_category, lodging, nights_total, etc.)
- Custom passenger fields from TripBooking pipeline

**New Passenger Model Fields:**
- Basic passenger info (firstname, lastname, email, phone, DOB, gender)
- Status fields (status, registration_completed, documents_completed)
- Files (reservation, mou, affidavit)
- Health details (health_state, health_medical_info, primary_phy, etc.)
- Room info (user_roomate, room_occupancy)
- Emergency contact (10+ fields for contact1_u*)
- Passport info (number, expire, file, country)
- Legal (form_submitted_date, travel_category_license, passenger_signature)

### 2. ✅ Created Field Mapping Utility
**`field_mapping.py` provides:**
- `TRIP_FIELD_MAP` - Maps 30+ GHL fields to Trip columns
- `PASSENGER_FIELD_MAP` - Maps 25+ GHL fields to Passenger columns
- `parse_ghl_custom_fields()` - Converts GHL array format to dict
- `map_trip_custom_fields()` - Maps and type-converts trip fields
- `map_passenger_custom_fields()` - Maps and type-converts passenger fields
- `create_ghl_custom_fields_list()` - Reverse mapping for updates

### 3. ✅ Database Recreated
- All tables dropped and recreated with new schema
- Ready for fresh sync from GHL

## What Still Needs to Be Done

### 1. Update Sync Methods to Use Field Mapping
**File**: `services/ghl_sync.py`

Both `sync_trip_opportunities()` and `sync_passenger_opportunities()` need to be updated to:

1. Import the field mapping functions:
```python
from field_mapping import parse_ghl_custom_fields, map_trip_custom_fields, map_passenger_custom_fields
```

2. Replace the manual field mapping with the utility functions:

**For Trips:**
```python
# OLD CODE (lines ~265-290):
custom_fields_raw = opp_data.get('custom_fields', [])
custom_fields = {}
# ... manual conversion ...

# NEW CODE:
custom_fields_list = opp_data.get('custom_fields', [])
custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
mapped_fields = map_trip_custom_fields(custom_fields_dict)

# Apply all mapped fields to trip
for column, value in mapped_fields.items():
    if hasattr(trip, column) and value is not None:
        setattr(trip, column, value)
```

**For Passengers:**
```python
# OLD CODE (lines ~410-420):
custom_fields_raw = opp_data.get('custom_fields', [])
# ... manual conversion ...

# NEW CODE:
custom_fields_list = opp_data.get('custom_fields', [])
custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
mapped_fields = map_passenger_custom_fields(custom_fields_dict)

# Set passenger fields from contact
passenger.firstname = contact.firstname
passenger.lastname = contact.lastname
passenger.email = contact.email
passenger.phone = contact.phone

# Apply all mapped custom fields
for column, value in mapped_fields.items():
    if hasattr(passenger, column) and value is not None:
        setattr(passenger, column, value)
```

3. Handle trip linking for passengers:
```python
# For now, skip trip linking - we'll do this in a separate step
# Just look for trip name in custom fields
trip_name = custom_fields_dict.get('opportunity.tripname')
if trip_name:
    trip = Trip.query.filter(Trip.name.contains(trip_name)).first()
    if trip:
        passenger.trip_id = trip.id
```

### 2. Run Full Sync
```bash
cd ~/Downloads/claude_code_tripbuilder
source .venv/bin/activate
cd tripbuilder
flask sync-ghl
```

Expected results:
- ✅ 2 pipelines
- ✅ 11 stages
- ✅ 53 custom fields
- ✅ 5,453 contacts
- ✅ 693-697 trips (with all custom fields mapped)
- ✅ 6,477 passengers (with all custom fields mapped)

### 3. Verify Data in Database
```bash
psql -U ridiculaptop -d tripbuilder
```

```sql
-- Check trips
SELECT id, name, destination, arrival_date, return_date, max_passengers, trip_vendor
FROM trips
LIMIT 5;

-- Check passengers  
SELECT id, firstname, lastname, passport_number, passport_country, health_state
FROM passengers
LIMIT 5;

-- Check trip-passenger linkage
SELECT 
    t.name as trip_name,
    COUNT(p.id) as passenger_count
FROM trips t
LEFT JOIN passengers p ON p.trip_id = t.id
GROUP BY t.id, t.name
ORDER BY passenger_count DESC
LIMIT 10;
```

### 4. Link Passengers to Trips (Separate Task)
Many passengers won't link automatically because the trip reference field wasn't populated when they were created. We'll need a separate script to:
1. Look at each passenger's `opportunity.tripname` custom field
2. Find matching trip by name
3. Update passenger.trip_id

## Files Modified/Created

```
tripbuilder/
├── models.py                    # ✅ Updated with full schema
├── models_old_backup.py         # ✅ Backup of old schema
├── field_mapping.py             # ✅ NEW - Field mapping utilities
├── recreate_db.py               # ✅ NEW - Database recreation script
└── services/
    └── ghl_sync.py              # ⏳ NEEDS UPDATE - Add field mapping
```

## Next Command to Run

```bash
cd ~/Downloads/claude_code_tripbuilder
source .venv/bin/activate
cd tripbuilder

# Edit services/ghl_sync.py to add field mapping imports and usage
# Then run:
flask sync-ghl
```

## Status Summary

✅ **COMPLETE**:
- Database schema expanded with all custom fields
- Field mapping utility created
- Database recreated with new schema

⏳ **IN PROGRESS**:
- Update sync methods to use field mapping
- Run full sync with new schema
- Verify all 693 trips + 6,477 passengers sync correctly

🎯 **NEXT**:
- Stage 2B: Trip → Opportunity Creation (bidirectional sync)
- Trip-Passenger linking script
