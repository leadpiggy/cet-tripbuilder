# 🚀 Quick Reference - TripBuilder

## Run the App

```bash
cd ~/Downloads/claude_code_tripbuilder
source .venv/bin/activate
cd tripbuilder
python app.py
```
→ http://localhost:5269

## Sync GHL Data

```bash
cd ~/Downloads/claude_code_tripbuilder
source .venv/bin/activate
cd tripbuilder
flask sync-ghl
```

## Check Database

```bash
psql -U ridiculaptop -d tripbuilder
```

```sql
-- Quick stats
SELECT 
    (SELECT COUNT(*) FROM pipelines) as pipelines,
    (SELECT COUNT(*) FROM pipeline_stages) as stages,
    (SELECT COUNT(*) FROM custom_fields) as fields,
    (SELECT COUNT(*) FROM contacts) as contacts,
    (SELECT COUNT(*) FROM trips) as trips;
```

## Project Structure

```
~/Downloads/claude_code_tripbuilder/
├── .venv/                      # Virtual environment
├── tripbuilder/                # Main app directory
│   ├── app.py                  # Flask application
│   ├── models.py               # Database models
│   ├── ghl_api.py             # GHL API wrapper
│   ├── services/
│   │   └── ghl_sync.py        # Sync service
│   ├── templates/             # HTML templates
│   └── static/                # CSS/JS assets
```

## Status

✅ Stage 1 Complete - Trip names working  
✅ Stage 2A Complete - GHL sync working  
⏳ Stage 2B Next - Trip → Opportunity creation

## Key URLs

- Dashboard: http://localhost:5269
- Trips: http://localhost:5269/trips
- Contacts: http://localhost:5269/contacts
- Create Trip: http://localhost:5269/trips/new

## Last Sync Results

- Pipelines: 2
- Stages: 11
- Custom Fields: 53
- **Contacts: 5,453** ✅

✅ All systems operational!
