# TripBuilder - Pipeline and Custom Field Data Reference

This document contains all pipeline, pipeline stage, and custom field data from the CSV files, along with instructions for retrieving this data from the GoHighLevel API v2 or MCP.

---

## Pipelines

| ID | Name |
|---|---|
| IlWdPtOpcczLpgsde2KF | TripBooking |
| fnsdpRtY9o83Vr4z15bE | Passenger |

### TripBooking Pipeline
- **Purpose**: Tracks the overall trip from inquiry to completion
- **Scope**: One opportunity per Trip (backend database record)
- **Use Case**: Manage trip-level details, vendor info, logistics

### Passenger Pipeline
- **Purpose**: Tracks each passenger's journey through trip preparation
- **Scope**: One opportunity per Contact-Trip enrollment
- **Use Case**: Manage passenger details, passport info, health records, emergency contacts

---

## Pipeline Stages

### Passenger Pipeline Stages (fnsdpRtY9o83Vr4z15bE)

| ID | Name | Position | Description |
|---|---|---|---|
| 62c0b80d-6e56-4775-9d93-fbc96fda92e7 | AddedToTrip | 0 | Contact added as passenger to a trip |
| 5019844d-b9bd-43ef-b027-e966f279bf96 | DetailsSubmitted | 1 | Personal/passport/health details collected |
| b55fba98-5ca4-4b5a-8c75-97c43ae1bab0 | TripDetailsSent | 2 | Trip information sent to passenger |
| d63f1360-81db-40ce-8a4c-ca00516f64d8 | TripReady | 3 | Passenger fully prepared for travel |
| 4b4a6f25-853d-487d-8db1-48371d427573 | TripInProgress | 4 | Passenger actively on trip |
| dfca0535-a466-4ded-af60-6c0c3a677b8c | TripComplete | 5 | Passenger completed trip |

### TripBooking Pipeline Stages (IlWdPtOpcczLpgsde2KF)

| ID | Name | Position | Description |
|---|---|---|---|
| 027508e9-939c-4646-bb59-66970fe674fe | FormSubmit | 0 | Initial trip inquiry/booking form submitted |
| 8927d13e-bdd8-45db-a55a-96b9057d3676 | TripFinalized | 1 | Trip details confirmed (destination, dates, vendor) |
| 635ba2fa-9270-40ac-8ff9-259a5487ce72 | TravelersAdded | 2 | Passengers/contacts linked to the trip |
| 19d3c6b2-cc55-40cb-973c-4ba603e6d19a | TripScheduled | 3 | All logistics confirmed and scheduled |
| 56c0708d-48ef-4cb5-873a-c7785b566448 | TripComplete | 4 | Trip concluded |

---

## Custom Field Groups

| ID | Name | Model | Pipeline ID | Description |
|---|---|---|---|---|
| **Passenger Pipeline Groups** |
| SgWPJJ0uHrmPR90kDv8R | Room Info | opportunity | fnsdpRtY9o83Vr4z15bE | Roommate preferences, occupancy |
| lKQQhGL4xhpd9Lpfnu1k | Passport Info | opportunity | fnsdpRtY9o83Vr4z15bE | Passport number, expiration, country, image |
| QlF3XC2zKJk6yepcGeCw | Health Details | opportunity | fnsdpRtY9o83Vr4z15bE | Health state, medical limitations, physician info, medications |
| d88EO8Sfm0E9h825Xhog | Emergency Contact | opportunity | fnsdpRtY9o83Vr4z15bE | Emergency contact name, relationship, address, phone |
| phpeRQgIExMgunGsnIMK | Legal | opportunity | fnsdpRtY9o83Vr4z15bE | Form submitted date, travel license, signature |
| C6JkkidhL39BMTCsKFqh | Files | opportunity | fnsdpRtY9o83Vr4z15bE | Reservation, MOU, Affidavit uploads |
| **TripBooking Pipeline Groups** |
| soiG10b9GQuVzF4B7aMK | Opportunity Details | opportunity | IlWdPtOpcczLpgsde2KF | Birth country, passenger ID/name/number, Trip ID/Name, dates, pricing |
| AsK8LH2JAKUGckXSCABk | Vendor Info | opportunity | IlWdPtOpcczLpgsde2KF | Trip vendor, vendor terms |
| iz2R5sVQnICgJApeIleV | Trip Details | opportunity | IlWdPtOpcczLpgsde2KF | Arrival/return dates, max passengers, travel category, pricing |
| mnGyltuJPG90Z4DZiJtd | Internal | opportunity | IlWdPtOpcczLpgsde2KF | Internal trip details |
| **Contact Groups** |
| aJt5rT3cuT8puG96aSlV | Additional Info | contact | (null) | Contact form message |
| eixFPD7T49Cpte0Ae2x1 | Trip Inquiry | contact | (null) | Trip type, trip request details |
| r5zUIuNnngzObwhT1y5j | Legal | contact | (null) | Parent/guardian name (if under 18), signature |

---

## Custom Fields (Selected Examples)

### Passport Info Group (lKQQhGL4xhpd9Lpfnu1k)

| Field Name | Data Type | Field Key | Placeholder | Position |
|---|---|---|---|---|
| Passport Number | TEXT | opportunity.passportnumber | Passport Number | 50 |
| Passport Expiration | DATE | opportunity.passportexpire | | 150 |
| Passport Image | FILEUPLOAD | opportunity.passportfile | | 100 |
| Passport Country | SINGLEOPTIONS | opportunity.passportcountry | | 200 |

**Passport Country Options**: United States of America, Afghanistan, Albania, Algeria, ... (250+ countries)

### Health Details Group (QlF3XC2zKJk6yepcGeCw)

| Field Name | Data Type | Field Key | Placeholder | Position |
|---|---|---|---|---|
| How is your general state of health? | LARGETEXT | opportunity.healthstate | How is your general state of health? | 100 |
| Special medical, physical, dietary limitations, or allergies? | LARGETEXT | opportunity.healthmedicalinfo | Special medical, physical, dietary limitations, or allergies? | 250 |
| Primary Physician | TEXT | opportunity.primaryphy | Primary Physician | 200 |
| Physicians Phone Number | TEXT | opportunity.physicianphone | Physicians Phone Number | 150 |
| List all Rx medications recommended | LARGETEXT | opportunity.medicationlist | List all Rx medications recommended | 50 |

### Emergency Contact Group (d88EO8Sfm0E9h825Xhog)

| Field Name | Data Type | Field Key | Placeholder | Position |
|---|---|---|---|---|
| Emergency Contact First Name | TEXT | opportunity.contact1ufirstname | Emergency Contact First Name | 100 |
| Emergency Contact Last Name | TEXT | opportunity.contact1ulastname | Emergency Contact Last Name | 50 |
| Emergency Contact Relationship To You | TEXT | opportunity.contact1urelationship | Emergency Contact Relationship To You | 150 |
| Emergency Contact Mailing Address | TEXT | opportunity.contact1umailingaddress | Emergency Contact Mailing Address | 400 |
| Emergency Contact City | TEXT | opportunity.contact1ucity | Emergency Contact City | 300 |
| Emergency Contact State | SINGLEOPTIONS | opportunity.contact1ustate | State | 500 |
| Emergency Contact Zip | TEXT | opportunity.contact1uzip | Emergency Contact Zip | 200 |
| Emergency Contact Email Address | TEXT | opportunity.contact1uemail | Emergency Contact Email Address | 450 |
| Emergency Contact Phone Number | TEXT | opportunity.contact1uphone | Emergency Contact Phone Number | 250 |
| Emergency Contact Mobile Number | TEXT | opportunity.contact1umobnumber | Emergency Contact Mobile Number | 350 |

**Emergency Contact State Options**: Alaska, Alabama, Arizona, Arkansas, California, Colorado, ... (50 states + DC)

### Room Info Group (SgWPJJ0uHrmPR90kDv8R)

| Field Name | Data Type | Field Key | Placeholder | Options | Position |
|---|---|---|---|---|---|
| Roomate | TEXT | opportunity.userroomate | Roomate | | 50 |
| Preferred Occupancy | SINGLEOPTIONS | opportunity.roomoccupancy | Choose Occupancy | Single Occupancy, Double Occupancy | 100 |

### Vendor Info Group (AsK8LH2JAKUGckXSCABk)

| Field Name | Data Type | Field Key | Placeholder | Options | Position |
|---|---|---|---|---|---|
| Trip Vendor | SINGLEOPTIONS | opportunity.tripvendor | | Vendor-A | 50 |
| Vendor Terms | LARGETEXT | opportunity.vendorterms | | | 100 |

### Trip Details Group (iz2R5sVQnICgJApeIleV)

| Field Name | Data Type | Field Key | Placeholder | Position |
|---|---|---|---|---|
| Arrival Date | DATE | opportunity.arrivaldate | | 150 |
| Return Date | DATE | opportunity.returndate | | 100 |
| Max Passengers | NUMERICAL | opportunity.maxpassengers | | 50 |
| Travel Category | SINGLEOPTIONS | opportunity.travelcategory | | 300 |
| Trip Standard Level Pricing | MONETORY | opportunity.tripstandardlevelpricing | | 350 |
| Passenger Count | NUMERICAL | opportunity.passengercount | | 400 |

**Travel Category Options**: People To People, Support For The Cuban People, Other

### Opportunity Details Group (soiG10b9GQuVzF4B7aMK)

| Field Name | Data Type | Field Key | Position |
|---|---|---|---|
| birth country | SINGLEOPTIONS | opportunity.birthcountry | 1550 |
| is child | CHECKBOX | opportunity.ischild | 1700 |
| Passenger Number | NUMERICAL | opportunity.passengernumber | 1800 |
| Passenger Id | TEXT | opportunity.passengerid | 1850 |
| Passenger First Name | TEXT | opportunity.passengerfirstname | 1900 |
| Passenger Last Name | TEXT | opportunity.passengerlastname | 1950 |
| Trip ID | NUMERICAL | opportunity.tripid | 2000 |
| Trip Name | SINGLEOPTIONS | opportunity.tripname | 2050 |
| Nights Total | NUMERICAL | opportunity.nightstotal | 2300 |
| Lodging | RADIO | opportunity.lodging | 2350 |
| Lodging Notes | LARGETEXT | opportunity.lodgingnotes | 2400 |
| Deposit Date | DATE | opportunity.depositdate | 2450 |
| Final Payment | DATE | opportunity.finalpayment | 2500 |
| Trip Description | LARGETEXT | opportunity.tripdescription | 2550 |
| Travel Business Used | SINGLEOPTIONS | opportunity.travelbusinessused | 2600 |
| Start Date | DATE | opportunity.startdate | 2650 |
| End Date | DATE | opportunity.enddate | 2700 |

**Trip Name Options**: (500+ trip names - see full list in custom_fields.csv)

### Legal Group - Opportunities (phpeRQgIExMgunGsnIMK)

| Field Name | Data Type | Field Key | Position |
|---|---|---|---|
| Form Submitted Date | DATE | opportunity.formsubmitteddate | 100 |
| Travel Category License | SINGLEOPTIONS | opportunity.travelcategorylicense | 50 |
| Passenger Signature | SIGNATURE | opportunity.passengersignature | 150 |

**Travel Category License Options**: 
- None
- Visiting Close Relatives - 515.561
- Official Government Business - 515.562
- Journalistic Activities - 515.563
- Professional Research and Professional Meetings - 515.564
- U.S. Religious Organizations - 515.566
- Public Performances, Clinics, Workshops, Athletic, and Other Competitions and Exhibitions - 515.567
- Support for the Cuban People - 515.574
- Humanitarian Projects - 515.575
- Private Foundations or Research or Educational Institutes - 515.576
- Exportation/Importation of Informational Materials - 515.545
- Exportation of BIS Authorized or Licensed Goods - 515.533, 515.559
- Educational Activities - 515.565a
- People to People travel 515.565b

### Files Group (C6JkkidhL39BMTCsKFqh)

| Field Name | Data Type | Field Key | Document Type | Position |
|---|---|---|---|---|
| Reservation | FILEUPLOAD | opportunity.reservation | .pdf | 50 |
| MOU | FILEUPLOAD | opportunity.mou | .pdf | 100 |
| Affidavit | FILEUPLOAD | opportunity.affidavit | .pdf | 150 |

### Contact Custom Fields

#### Trip Inquiry Group (eixFPD7T49Cpte0Ae2x1)

| Field Name | Data Type | Field Key | Options | Position |
|---|---|---|---|---|
| Trip Type | SINGLEOPTIONS | contact.triptype | Family/Friends, School, Business/Organization, Forum, Open Sign-Up, Other | 50 |
| Trip Request Details | LARGETEXT | contact.triprequestdetails | | 100 |

#### Additional Info Group (aJt5rT3cuT8puG96aSlV)

| Field Name | Data Type | Field Key | Position |
|---|---|---|---|
| ContactForm Message | LARGETEXT | contact.contactformmessage | 50 |

#### Legal Group - Contacts (r5zUIuNnngzObwhT1y5j)

| Field Name | Data Type | Field Key | Position |
|---|---|---|---|
| Parent/Guardian Full Name, if passenger is under 18. | TEXT | contact.parentguardianfullnameifpassengerisunder18 | 50 |
| Signature | SIGNATURE | contact.signature | 100 |

---

## Data Type Definitions

- **TEXT**: Single-line text input
- **LARGETEXT**: Multi-line textarea
- **SINGLEOPTIONS**: Dropdown select (single choice)
- **MULTIPLE_SELECT_OPTIONS**: Multi-select dropdown or checkboxes
- **CHECKBOX**: Boolean checkbox
- **RADIO**: Radio button selection
- **FILEUPLOAD**: File upload field
- **DATE**: Date picker
- **NUMERICAL**: Number input
- **MONETORY**: Currency/money input
- **SIGNATURE**: Signature field

---

## How to Retrieve This Data from GoHighLevel API v2

### 1. Get Pipelines

**Endpoint**: `GET https://services.leadconnectorhq.com/opportunities/pipelines`

**Headers**:
```
Authorization: Bearer YOUR_API_TOKEN
Version: 2021-07-28
```

**Required Scope**: `opportunities.readonly`

**Example Request (Python)**:
```python
import requests

url = "https://services.leadconnectorhq.com/opportunities/pipelines"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Version": "2021-07-28"
}

response = requests.get(url, headers=headers)
pipelines = response.json()

for pipeline in pipelines['pipelines']:
    print(f"Pipeline: {pipeline['name']} (ID: {pipeline['id']})")
    for stage in pipeline['stages']:
        print(f"  - Stage: {stage['name']} (ID: {stage['id']}, Position: {stage['position']})")
```

**Example Response**:
```json
{
  "pipelines": [
    {
      "id": "IlWdPtOpcczLpgsde2KF",
      "name": "TripBooking",
      "stages": [
        {
          "id": "027508e9-939c-4646-bb59-66970fe674fe",
          "name": "FormSubmit",
          "position": 0
        },
        ...
      ]
    }
  ]
}
```

**API Documentation**: [Get Pipelines](https://marketplace.gohighlevel.com/docs/ghl/opportunities/get-pipelines/)[23]

---

### 2. Get Custom Fields

**Endpoint**: `GET https://services.leadconnectorhq.com/locations/{locationId}/customFields`

**Headers**:
```
Authorization: Bearer YOUR_API_TOKEN
Version: 2021-07-28
```

**Required Scope**: `locations.readonly`

**Query Parameters**:
- `model` (optional): Filter by model type (`contact` or `opportunity`)

**Example Request (Python)**:
```python
import requests

url = f"https://services.leadconnectorhq.com/locations/{LOCATION_ID}/customFields"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Version": "2021-07-28"
}

# Get all opportunity custom fields
params = {"model": "opportunity"}
response = requests.get(url, headers=headers, params=params)
custom_fields = response.json()

for field in custom_fields['customFields']:
    print(f"Field: {field['name']}")
    print(f"  Key: {field['fieldKey']}")
    print(f"  Type: {field['dataType']}")
    print(f"  Group: {field.get('customFieldGroupId', 'N/A')}")
    if field.get('picklistOptions'):
        print(f"  Options: {', '.join(field['picklistOptions'])}")
    print()
```

**Example Response**:
```json
{
  "customFields": [
    {
      "id": "cH65SxcblktQe7hRx1yx",
      "name": "Passport Number",
      "fieldKey": "opportunity.passportnumber",
      "dataType": "TEXT",
      "model": "opportunity",
      "placeholder": "Passport Number",
      "position": 50,
      "customFieldGroupId": "lKQQhGL4xhpd9Lpfnu1k"
    },
    {
      "id": "Qpop7wW0NP3ceiSslH8n",
      "name": "Passport Country",
      "fieldKey": "opportunity.passportcountry",
      "dataType": "SINGLEOPTIONS",
      "model": "opportunity",
      "picklistOptions": ["United States of America", "Afghanistan", ...],
      "position": 200,
      "customFieldGroupId": "lKQQhGL4xhpd9Lpfnu1k"
    }
  ]
}
```

**API Documentation**: [Get Custom Fields](https://marketplace.gohighlevel.com/docs/ghl/locations/get-custom-fields/)[32]

---

### 3. Get Custom Field Groups

**Note**: There is no dedicated endpoint for custom field groups in the public API. Groups are returned as part of the custom fields response via the `customFieldGroupId` property. You can infer groups by:

1. Fetching all custom fields
2. Grouping by `customFieldGroupId`
3. Mapping group IDs to names (you may need to maintain this mapping from initial setup)

**Alternative**: Use the MCP `locations_get-custom-fields` tool, which may return more structured group data.

---

## How to Retrieve This Data Using MCP

### Prerequisites
- GoHighLevel MCP Server configured (see MCP_INTEGRATION.md)
- Private Integration Token with appropriate scopes
- MCP client initialized (LangGraph, Claude Desktop, etc.)

### 1. Get Pipelines via MCP

**MCP Tool**: `opportunities_get-pipelines`

**Example (Python with LangGraph)**:
```python
import asyncio
from services.mcp_service import mcp

async def get_pipelines():
    prompt = "Get all pipelines including their stages, IDs, and positions"
    response = await mcp.query(prompt)
    return response

pipelines = asyncio.run(get_pipelines())
print(pipelines)
```

**Natural Language Query Examples**:
- "Show me all pipelines and their stages"
- "What are the stage IDs for the Passenger pipeline?"
- "List all stages in the TripBooking pipeline in order"

---

### 2. Get Custom Fields via MCP

**MCP Tool**: `locations_get-custom-fields`

**Example (Python with LangGraph)**:
```python
async def get_custom_fields():
    prompt = """
    Get all custom fields for opportunities in the Passenger pipeline.
    Group them by field group and include:
    - Field name
    - Field key (for API updates)
    - Data type
    - Options (if dropdown/radio)
    - Placeholder text
    """
    response = await mcp.query(prompt)
    return response

fields = asyncio.run(get_custom_fields())
print(fields)
```

**Natural Language Query Examples**:
- "Show me all custom fields in the Passport Info group"
- "What are the field keys for emergency contact fields?"
- "List all file upload fields for passengers"
- "Get the options for the Travel Category License field"

---

## Common Use Cases

### Use Case 1: Seed Database with Pipeline Data

```python
import requests

# Fetch pipelines
url = f"https://services.leadconnectorhq.com/opportunities/pipelines"
headers = {"Authorization": f"Bearer {API_TOKEN}", "Version": "2021-07-28"}
response = requests.get(url, headers=headers)
pipelines_data = response.json()

# Insert into database
for pipeline in pipelines_data['pipelines']:
    # Insert Pipeline record
    db_pipeline = Pipeline(id=pipeline['id'], name=pipeline['name'])
    db.session.add(db_pipeline)
    
    for stage in pipeline['stages']:
        # Insert PipelineStage record
        db_stage = PipelineStage(
            id=stage['id'],
            name=stage['name'],
            position=stage['position'],
            pipeline_id=pipeline['id']
        )
        db.session.add(db_stage)

db.session.commit()
```

### Use Case 2: Generate Dynamic Forms from Custom Fields

```python
# Fetch custom fields for Passenger pipeline
url = f"https://services.leadconnectorhq.com/locations/{LOCATION_ID}/customFields"
params = {"model": "opportunity"}
response = requests.get(url, headers=headers, params=params)
fields_data = response.json()

# Filter by group (e.g., Passport Info)
passport_group_id = "lKQQhGL4xhpd9Lpfnu1k"
passport_fields = [f for f in fields_data['customFields'] if f.get('customFieldGroupId') == passport_group_id]

# Render form fields in Jinja2 template
for field in sorted(passport_fields, key=lambda x: x['position']):
    if field['dataType'] == 'TEXT':
        # Render text input
    elif field['dataType'] == 'SINGLEOPTIONS':
        # Render dropdown with options from field['picklistOptions']
    elif field['dataType'] == 'FILEUPLOAD':
        # Render file upload input
```

### Use Case 3: Update Custom Field Values

```python
# Update passport number for a Passenger opportunity
opportunity_id = "xyz123"
field_key = "opportunity.passportnumber"
value = "AB1234567"

url = f"https://services.leadconnectorhq.com/opportunities/{opportunity_id}/upsert"
payload = {
    "customFields": {
        field_key: value
    }
}

response = requests.put(url, headers=headers, json=payload)
```

---

## Important Notes

- **Pipeline IDs and Stage IDs are immutable** once created in GHL. Use these IDs consistently across your application.
- **Custom Field Keys** (e.g., `opportunity.passportnumber`) are the API identifiers. Use these in API calls, not the display names.
- **Position** determines the order fields appear in the UI. Lower numbers appear first.
- **Model** indicates whether a field belongs to `contact` or `opportunity`. They are not interchangeable.
- **Picklist Options** for dropdown fields must match exactly when updating values via API.
- **File Upload Fields** return URLs to uploaded files, not the files themselves.

---

## References

- GoHighLevel API v2 Documentation: https://marketplace.gohighlevel.com/docs/[14]
- Get Pipelines Endpoint: https://marketplace.gohighlevel.com/docs/ghl/opportunities/get-pipelines/[23]
- Get Custom Fields Endpoint: https://marketplace.gohighlevel.com/docs/ghl/locations/get-custom-fields/[32]
- Custom Fields V2 API: https://marketplace.gohighlevel.com/docs/ghl/custom-fields/custom-fields-v-2-api/[30]
- MCP Integration Guide: See MCP_INTEGRATION.md