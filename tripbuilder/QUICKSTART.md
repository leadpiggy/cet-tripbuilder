# Quick Start Guide - TripBuilder

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- GoHighLevel account with Private Integration access

---

## Step 1: Setup Environment (2 minutes)

```bash
# Navigate to project
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder/tripbuilder

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Credentials (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

**Required values** (get from GoHighLevel → Settings → Private Integrations):
```env
GHL_API_TOKEN=your_actual_token_here
GHL_LOCATION_ID=your_actual_location_id_here
```

---

## Step 3: Initialize Database (30 seconds)

```bash
flask init-db
```

Expected output:
```
✅ Database tables created successfully!
```

---

## Step 4: Run Application (30 seconds)

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

---

## Step 5: Test It! (1 minute)

Open your browser and go to: **http://localhost:5000**

### What You Can Do Right Now:

1. **Dashboard** (`/`)
   - View trip/contact/passenger counts
   - See recent trips

2. **Create a Trip** (`/trips/new`)
   - Fill in destination, dates, capacity
   - Submit → Saved to local database

3. **View Trips** (`/trips`)
   - See all trips in card format
   - Click to view details

4. **Enroll a Passenger** (from trip detail page)
   - Fill in contact information
   - Submit → Contact created in GHL! ✨
   - Passenger linked to trip

5. **View Contacts** (`/contacts`)
   - See all contacts (after enrolling passengers)

---

## What Works vs. What's Coming

### ✅ Working Now (Stage 1 Complete)
- Trip management (create, view, edit, delete)
- Passenger enrollment (creates contacts in GHL)
- Contact viewing
- Responsive UI with Bootstrap 5
- Flash message feedback
- Form validation

### ⏳ Coming Next (Stage 2A+)
- `flask sync-ghl` command to pull existing GHL data
- Trip → TripBooking opportunity creation
- Passenger → Passenger opportunity creation  
- Custom field forms (passport, health, etc.)
- Stage progression controls

---

## Troubleshooting

### "Module not found" error?
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Can't connect to database?
```bash
# Reinitialize database
rm tripbuilder.db  # Delete old database
flask init-db      # Create fresh one
```

### GHL API errors when enrolling passengers?
- Check `GHL_API_TOKEN` in `.env` is correct
- Check `GHL_LOCATION_ID` in `.env` is correct
- Ensure token has proper scopes (contacts.write at minimum)

### Port 5000 already in use?
```bash
# Edit app.py and change the port
# At the bottom, change:
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

---

## Next Steps

### To Continue Development:

1. **Read Stage 2A Implementation**:
   - See `IMPLEMENTATION_PLAN_V2.md`
   - Focus on Stage 2A section

2. **Implement GHL Sync**:
   - Edit `services/ghl_sync.py`
   - Implement the TODO methods
   - Test with `flask sync-ghl`

3. **Test Thoroughly**:
   - Create multiple trips
   - Enroll multiple passengers
   - Verify contacts in GHL dashboard

---

## Useful Commands

```bash
# Start application
python app.py

# Initialize database (creates all tables)
flask init-db

# Sync from GHL (Stage 2A - not yet implemented)
flask sync-ghl

# Python shell with app context
flask shell

# Deactivate virtual environment
deactivate
```

---

## File Structure Reference

```
tripbuilder/
├── app.py              # Main Flask app
├── models.py           # Database models
├── ghl_api.py          # GHL API wrapper
├── requirements.txt    # Dependencies
├── .env               # Your credentials (DO NOT COMMIT)
├── .env.example       # Template
└── services/
    └── ghl_sync.py    # Sync service (Stage 2A focus)
```

---

## Getting Help

1. Check `README.md` for full documentation
2. Check `STAGE_1_COMPLETE.md` for what's implemented
3. Check `IMPLEMENTATION_PLAN_V2.md` for roadmap
4. Check `ARCHITECTURE.md` for system design

---

**You're ready to go! 🎉**

Visit http://localhost:5000 and start creating trips!
