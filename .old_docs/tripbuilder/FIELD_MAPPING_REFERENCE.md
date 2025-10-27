# Field Mapping Reference

## Quick Reference: GHL Custom Fields → Database Columns

This document shows exactly which GoHighLevel custom fields are mapped to which database columns during sync.

---

## Trip Fields (30+ mappings)

### Opportunity Details Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.birthcountry` | `birth_country` | String | Passenger's birth country |
| `opportunity.passengerid` | `passenger_id` | String | Reference ID |
| `opportunity.passengername` | `passenger_first_name` | String | May need splitting |
| `opportunity.passengernumber` | `passenger_number` | Integer | Passenger number |
| `opportunity.tripid` | `trip_id_custom` | Integer | Trip reference ID |
| `opportunity.tripname` | `trip_name` | String | **Trip name** |
| `opportunity.nights` | `nights_total` | Integer | Total nights |

### Trip Details Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.arrivaldate` | `arrival_date` | Date | **Start of trip** |
| `opportunity.returndate` | `return_date` | Date | **End of trip** |
| `opportunity.maxpassengers` | `max_passengers` | Integer | **Maximum capacity** |
| `opportunity.travelcategory` | `travel_category` | String | Type of travel |
| `opportunity.tripstandardlevelpricing` | `trip_standard_level_pricing` | Decimal | **Base price** |
| `opportunity.passengercount` | `passenger_count` | Integer | Current count |
| `opportunity.lodging` | `lodging` | String | Where staying |
| `opportunity.lodgingnotes` | `lodging_notes` | Text | Additional info |
| `opportunity.depositdate` | `deposit_date` | Date | When deposit due |
| `opportunity.finalpayment` | `final_payment` | Date | Final payment date |
| `opportunity.tripdescription` | `trip_description` | Text | Full description |

### Vendor Info Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.tripvendor` | `trip_vendor` | String | **Vendor name** |
| `opportunity.vendorterms` | `vendor_terms` | Text | Terms & conditions |
| `opportunity.travelbusinessused` | `travel_business_used` | String | Business entity |

### Internal Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.internaltripdetails` | `internal_trip_details` | Text | Internal notes |
| `opportunity.ischild` | `is_child` | Boolean | Child trip flag |

---

## Passenger Fields (25+ mappings)

### Contact Info (from Contact record, not custom fields)
| GHL Contact Field | Database Column | Type | Notes |
|-------------------|----------------|------|-------|
| `firstName` | `firstname` | String | From contact |
| `lastName` | `lastname` | String | From contact |
| `email` | `email` | String | From contact |
| `phone` | `phone` | String | From contact |

### Room Info Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.userroomate` | `user_roomate` | String | Roommate preference |
| `opportunity.roomoccupancy` | `room_occupancy` | String | Single/Double/etc |

### Passport Info Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.passportnumber` | `passport_number` | String | **Passport #** |
| `opportunity.passportexpire` | `passport_expire` | Date | **Expiration date** |
| `opportunity.passportfile` | `passport_file` | String | File URL |
| `opportunity.passportcountry` | `passport_country` | String | **Issuing country** |

### Health Details Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.healthstate` | `health_state` | String | **Health status** |
| `opportunity.healthmedicalinfo` | `health_medical_info` | Text | Medical conditions |
| `opportunity.primaryphy` | `primary_phy` | String | Doctor name |
| `opportunity.physicianphone` | `physician_phone` | String | Doctor phone |
| `opportunity.medicationlist` | `medication_list` | Text | **Current meds** |

### Emergency Contact Group (Contact 1)
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.contact1ulastname` | `contact1_ulast_name` | String | EC last name |
| `opportunity.contact1ufirstname` | `contact1_ufirst_name` | String | EC first name |
| `opportunity.contact1urelationship` | `contact1_urelationship` | String | Relationship |
| `opportunity.contact1umailingaddress` | `contact1_umailing_address` | String | Street address |
| `opportunity.contact1ucity` | `contact1_ucity` | String | City |
| `opportunity.contact1uzip` | `contact1_uzip` | String | Zip code |
| `opportunity.contact1uemail` | `contact1_uemail` | String | EC email |
| `opportunity.contact1uphone` | `contact1_uphone` | String | EC phone |
| `opportunity.contact1umobnumber` | `contact1_umob_number` | String | EC mobile |
| `opportunity.contact1ustate` | `contact1_ustate` | String | State |

### Legal Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.formsubmitteddate` | `form_submitted_date` | Date | When submitted |
| `opportunity.travelcategorylicense` | `travel_category_license` | String | License info |
| `opportunity.passengersignature` | `passenger_signature` | String | Signature file |

### Files Group
| GHL Field Key | Database Column | Type | Notes |
|---------------|----------------|------|-------|
| `opportunity.reservation` | `reservation` | String | Reservation file |
| `opportunity.mou` | `mou` | String | MOU file |
| `opportunity.affidavit` | `affidavit` | String | Affidavit file |

---

## Type Conversions

The field mapping utilities automatically handle type conversions:

### Date Fields
**GHL Format:** ISO 8601 string or Unix timestamp
**Conversion:**
```python
# ISO format: "2025-03-15T00:00:00.000Z"
datetime.fromisoformat(value.replace('Z', '+00:00')).date()

# Unix timestamp: 1710460800000 (milliseconds)
datetime.fromtimestamp(value / 1000).date()
```

**Applied to:**
- `arrival_date`, `return_date`, `deposit_date`, `final_payment` (trips)
- `passport_expire`, `form_submitted_date` (passengers)

### Integer Fields
**GHL Format:** String or numeric
**Conversion:**
```python
int(float(value)) if value else None
```

**Applied to:**
- `max_passengers`, `passenger_number`, `passenger_count`, `nights_total`, `trip_id_custom`

### Decimal Fields
**GHL Format:** String or numeric
**Conversion:**
```python
float(value) if value else None
```

**Applied to:**
- `trip_standard_level_pricing`

### Boolean Fields
**GHL Format:** Boolean, "true"/"false", "yes"/"no", "1"/"0"
**Conversion:**
```python
if isinstance(value, bool):
    return value
elif isinstance(value, str):
    return value.lower() in ['true', 'yes', '1']
```

**Applied to:**
- `is_child`

### String Fields
**GHL Format:** Any
**Conversion:**
```python
str(value) if value else None
```

**Applied to:** All other fields

---

## Usage in Sync

### Trip Sync Flow
```python
# 1. Get opportunity from GHL
opp_data = ghl_api.get_opportunity(opp_id)

# 2. Parse custom fields
custom_fields_list = opp_data.get('customFields', [])
custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
# Result: {"opportunity.arrivaldate": "2025-03-15T00:00:00Z", ...}

# 3. Map to database columns
mapped_fields = map_trip_custom_fields(custom_fields_dict)
# Result: {"arrival_date": date(2025, 3, 15), ...}

# 4. Apply to Trip model
for column, value in mapped_fields.items():
    if hasattr(trip, column) and value is not None:
        setattr(trip, column, value)
```

### Passenger Sync Flow
```python
# 1. Get opportunity from GHL
opp_data = ghl_api.get_opportunity(opp_id)

# 2. Get contact info
contact = Contact.query.get(opp_data['contactId'])
passenger.firstname = contact.firstname
passenger.lastname = contact.lastname
passenger.email = contact.email
passenger.phone = contact.phone

# 3. Parse and map custom fields
custom_fields_list = opp_data.get('customFields', [])
custom_fields_dict = parse_ghl_custom_fields(custom_fields_list)
mapped_fields = map_passenger_custom_fields(custom_fields_dict)

# 4. Apply to Passenger model
for column, value in mapped_fields.items():
    if hasattr(passenger, column) and value is not None:
        setattr(passenger, column, value)
```

---

## Verifying Mappings

After running sync, check that fields are populated:

```sql
-- Trip fields verification
SELECT 
    COUNT(*) as total_trips,
    COUNT(arrival_date) as has_arrival,
    COUNT(return_date) as has_return,
    COUNT(max_passengers) as has_capacity,
    COUNT(trip_vendor) as has_vendor,
    COUNT(trip_standard_level_pricing) as has_pricing
FROM trips;

-- Passenger fields verification
SELECT 
    COUNT(*) as total_passengers,
    COUNT(passport_number) as has_passport,
    COUNT(passport_country) as has_country,
    COUNT(health_state) as has_health,
    COUNT(contact1_ufirst_name) as has_emergency_contact
FROM passengers;
```

Expected results:
- Most trips should have dates, capacity, and vendor
- Many passengers should have passport info
- Health and emergency contact info varies by completion

---

## Adding New Field Mappings

To add a new field mapping:

1. **Add to field_mapping.py:**
```python
TRIP_FIELD_MAP = {
    # ... existing mappings ...
    'opportunity.newfield': 'new_column_name',
}
```

2. **Add column to models.py:**
```python
class Trip(db.Model):
    # ... existing columns ...
    new_column_name = db.Column(db.String(255))
```

3. **Create migration:**
```bash
flask db migrate -m "Add new_column_name to trips"
flask db upgrade
```

4. **Run sync:**
```bash
flask sync-ghl
```

The field will automatically be mapped during sync!

---

## Troubleshooting

### Field Not Syncing
1. Check field key matches exactly (case-sensitive)
2. Verify field exists in GHL custom fields
3. Check type conversion logic
4. Look for errors in sync output

### Type Conversion Errors
The mapping functions have try/except blocks that silently skip invalid values.
Enable debug logging to see conversion errors:

```python
# In field_mapping.py, add:
import logging
logger = logging.getLogger(__name__)

# In try/except blocks:
except Exception as e:
    logger.debug(f"Failed to convert {field_key}: {e}")
```

### Wrong Data Type
- Dates appearing as strings → Check GHL format (ISO vs timestamp)
- Numbers appearing as strings → Add to integer/decimal field list
- Booleans not converting → Check true/false string format

---

## Pipeline IDs Reference

| Pipeline | ID | Purpose |
|----------|-----|---------|
| TripBooking | `IlWdPtOpcczLpgsde2KF` | Trip opportunities |
| TripBooking (Passenger) | `fnsdpRtY9o83Vr4z15bE` | Passenger enrollments |

---

This reference is current as of Stage 2A implementation.
