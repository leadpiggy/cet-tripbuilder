# Field Mapping Visual Guide

## How It Works - Real Examples

This shows exactly what happens when the sync runs with field mapping enabled.

---

## Example 1: Trip Opportunity

### What GHL Returns (Raw API Response):

```json
{
  "id": "trip_abc123",
  "name": "Costa Rica Adventure March 2025",
  "pipelineId": "IlWdPtOpcczLpgsde2KF",
  "customFields": [
    {
      "id": "field_001",
      "fieldValue": "2025-03-15T00:00:00.000Z"
    },
    {
      "id": "field_002", 
      "fieldValue": "2025-03-22T00:00:00.000Z"
    },
    {
      "id": "field_003",
      "fieldValue": "25"
    },
    {
      "id": "field_004",
      "fieldValue": "Adventure Travel"
    },
    {
      "id": "field_005",
      "fieldValue": "2500.00"
    },
    {
      "id": "field_006",
      "fieldValue": "Costa Rica Expeditions"
    }
  ]
}
```

### Step 1: Field Mapping Looks Up Field Keys

The sync queries the `custom_fields` table to convert IDs to keys:

```
field_001 → opportunity.arrivaldate
field_002 → opportunity.returndate
field_003 → opportunity.maxpassengers
field_004 → opportunity.travelcategory
field_005 → opportunity.tripstandardlevelpricing
field_006 → opportunity.tripvendor
```

### Step 2: parse_ghl_custom_fields() Converts to Dict

```python
custom_fields_dict = {
    'opportunity.arrivaldate': '2025-03-15T00:00:00.000Z',
    'opportunity.returndate': '2025-03-22T00:00:00.000Z',
    'opportunity.maxpassengers': '25',
    'opportunity.travelcategory': 'Adventure Travel',
    'opportunity.tripstandardlevelpricing': '2500.00',
    'opportunity.tripvendor': 'Costa Rica Expeditions'
}
```

### Step 3: map_trip_custom_fields() Maps to Database Columns

```python
mapped_fields = {
    'arrival_date': date(2025, 3, 15),      # Converted from ISO string to date
    'return_date': date(2025, 3, 22),       # Converted from ISO string to date
    'max_passengers': 25,                   # Converted from string to int
    'travel_category': 'Adventure Travel',  # String (no conversion)
    'trip_standard_level_pricing': 2500.0,  # Converted from string to decimal
    'trip_vendor': 'Costa Rica Expeditions' # String (no conversion)
}
```

### Step 4: Fields Applied to Trip Model

```python
trip.arrival_date = date(2025, 3, 15)
trip.return_date = date(2025, 3, 22)
trip.max_passengers = 25
trip.travel_category = 'Adventure Travel'
trip.trip_standard_level_pricing = 2500.0
trip.trip_vendor = 'Costa Rica Expeditions'
```

### What Gets Saved to Database:

```sql
INSERT INTO trips (
    ghl_opportunity_id,
    name,
    destination,
    arrival_date,
    return_date,
    max_passengers,
    travel_category,
    trip_standard_level_pricing,
    trip_vendor
) VALUES (
    'trip_abc123',
    'Costa Rica Adventure March 2025',
    'Costa Rica Adventure March 2025',
    '2025-03-15',
    '2025-03-22',
    25,
    'Adventure Travel',
    2500.00,
    'Costa Rica Expeditions'
);
```

---

## Example 2: Passenger Opportunity

### What GHL Returns:

```json
{
  "id": "pass_xyz789",
  "contactId": "contact_123",
  "pipelineId": "fnsdpRtY9o83Vr4z15bE",
  "customFields": [
    {
      "id": "field_101",
      "fieldValue": "AB123456"
    },
    {
      "id": "field_102",
      "fieldValue": "2028-06-15T00:00:00.000Z"
    },
    {
      "id": "field_103",
      "fieldValue": "United States"
    },
    {
      "id": "field_104",
      "fieldValue": "Excellent"
    },
    {
      "id": "field_105",
      "fieldValue": "Jane Smith"
    },
    {
      "id": "field_106",
      "fieldValue": "+1-555-0100"
    },
    {
      "id": "field_107",
      "fieldValue": "Single"
    }
  ]
}
```

### Step 1: Contact Info Retrieved

```python
contact = Contact.query.get('contact_123')

passenger.firstname = contact.firstname  # "John"
passenger.lastname = contact.lastname    # "Doe"
passenger.email = contact.email          # "john@example.com"
passenger.phone = contact.phone          # "+1-555-1234"
```

### Step 2: Custom Fields Parsed and Mapped

```python
# After field lookup:
custom_fields_dict = {
    'opportunity.passportnumber': 'AB123456',
    'opportunity.passportexpire': '2028-06-15T00:00:00.000Z',
    'opportunity.passportcountry': 'United States',
    'opportunity.healthstate': 'Excellent',
    'opportunity.contact1ufirstname': 'Jane Smith',
    'opportunity.contact1uphone': '+1-555-0100',
    'opportunity.roomoccupancy': 'Single'
}

# After mapping:
mapped_fields = {
    'passport_number': 'AB123456',
    'passport_expire': date(2028, 6, 15),    # Converted to date
    'passport_country': 'United States',
    'health_state': 'Excellent',
    'contact1_ufirst_name': 'Jane Smith',
    'contact1_uphone': '+1-555-0100',
    'room_occupancy': 'Single'
}
```

### What Gets Saved to Database:

```sql
INSERT INTO passengers (
    id,
    contact_id,
    firstname,
    lastname,
    email,
    phone,
    passport_number,
    passport_expire,
    passport_country,
    health_state,
    contact1_ufirst_name,
    contact1_uphone,
    room_occupancy
) VALUES (
    'pass_xyz789',
    'contact_123',
    'John',
    'Doe',
    'john@example.com',
    '+1-555-1234',
    'AB123456',
    '2028-06-15',
    'United States',
    'Excellent',
    'Jane Smith',
    '+1-555-0100',
    'Single'
);
```

---

## Type Conversion Examples

### Dates

**GHL Format:**
```json
"2025-03-15T00:00:00.000Z"
```

**After Conversion:**
```python
date(2025, 3, 15)
```

**In Database:**
```sql
'2025-03-15'
```

---

### Integers

**GHL Format:**
```json
"25"
```

**After Conversion:**
```python
25
```

**In Database:**
```sql
25
```

---

### Decimals

**GHL Format:**
```json
"2500.00"
```

**After Conversion:**
```python
2500.0
```

**In Database:**
```sql
2500.00
```

---

### Booleans

**GHL Format (various):**
```json
"true"
"yes"
"1"
true
```

**After Conversion:**
```python
True
```

**In Database:**
```sql
true
```

---

## Before vs After Comparison

### Before Field Mapping Integration:

**Code:**
```python
# Manual parsing for each field
arrival_date_str = custom_fields.get('opportunity.arrivaldate')
if arrival_date_str:
    try:
        trip.start_date = datetime.fromisoformat(arrival_date_str.replace('Z', '+00:00')).date()
    except:
        trip.start_date = date.today()
else:
    trip.start_date = date.today()

# Repeat 30+ times for each field...
```

**Result:** Only 3-5 fields synced per entity

---

### After Field Mapping Integration:

**Code:**
```python
# One-liner for ALL fields
custom_fields_dict = parse_ghl_custom_fields(opp_data.get('customFields', []))
mapped_fields = map_trip_custom_fields(custom_fields_dict)

# Apply all fields
for column, value in mapped_fields.items():
    if hasattr(trip, column) and value is not None:
        setattr(trip, column, value)
```

**Result:** 30+ fields synced automatically with proper type conversion!

---

## Real Data Flow

```
┌─────────────────┐
│   GHL API       │
│  (Raw JSON)     │
└────────┬────────┘
         │
         │ 1. Fetch opportunities
         │
         ▼
┌─────────────────────────────────┐
│ parse_ghl_custom_fields()       │
│ - Converts array to dict        │
│ - Looks up field keys           │
└───────────┬─────────────────────┘
            │
            │ 2. Parse custom fields
            │
            ▼
┌─────────────────────────────────┐
│ map_trip_custom_fields()        │
│ - Maps to database columns      │
│ - Converts types                │
└───────────┬─────────────────────┘
            │
            │ 3. Map & convert
            │
            ▼
┌─────────────────────────────────┐
│ setattr(trip, column, value)    │
│ - Sets all fields on model      │
└───────────┬─────────────────────┘
            │
            │ 4. Apply to model
            │
            ▼
┌─────────────────────────────────┐
│ db.session.commit()             │
│ - Saves to PostgreSQL           │
└─────────────────────────────────┘
```

---

## Summary

**Before:**
- ❌ Manual field mapping
- ❌ Repeated date parsing code
- ❌ Only 3-5 fields per entity
- ❌ No type safety

**After:**
- ✅ Automatic field mapping
- ✅ Centralized type conversion
- ✅ 30+ trip fields, 25+ passenger fields
- ✅ Type-safe conversions
- ✅ Easy to add new fields

**Result:**
- 🎯 Complete trip information (dates, capacity, pricing, vendor, lodging)
- 🎯 Complete passenger information (passport, health, emergency contacts, room prefs)
- 🎯 Maintainable, DRY code
- 🎯 Consistent handling across all entities
