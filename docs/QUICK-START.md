# TripBuilder Quick Start Guide

**Get started with TripBuilder development in 5 minutes**

---

## 🚀 First-Time Setup

### 1. Prerequisites

- Python 3.x installed
- PostgreSQL 14+ running
- Git (optional)
- VS Code with Roo Code extension

### 2. Clone or Navigate to Project

```bash
# If you have the code
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder

# If cloning
git clone <repo-url>
cd claude_code_tripbuilder
```

### 3. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows
```

### 4. Install Dependencies

```bash
cd tripbuilder
pip install -r requirements.txt
```

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# You need:
# - GHL_API_TOKEN (from GoHighLevel Settings → Private Integrations)
# - GHL_LOCATION_ID (your GHL location ID)
# - SECRET_KEY (generate random string)
```

### 6. Initialize Database

```bash
# Make sure PostgreSQL is running
# Create database (first time only)
createdb tripbuilder

# Initialize tables
flask init-db
```

### 7. Sync Data from GoHighLevel

```bash
# Import all existing data
flask sync-ghl

# This will import:
# - 2 pipelines, 11 stages
# - 53 custom fields
# - ~5,453 contacts
# - ~693 trips
# - ~6,477 passengers
```

### 8. Run the Application

```bash
python app.py

# Visit: http://localhost:5269
```

---

## 📖 Understanding the Documentation

### Read These First (In Order):

1. **[`memory-bank/projectBrief.md`](../memory-bank/projectBrief.md)**
   - What the project does
   - Core requirements
   - Technology stack

2. **[`.roo/rules/START-HERE.md`](../.roo/rules/START-HERE.md)**
   - Mandatory checklists
   - **READ BEFORE EVERY ACTION**

3. **[`memory-bank/activeContext.md`](../memory-bank/activeContext.md)**
   - What's happening now
   - Immediate next steps

4. **[`docs/ROO-CODE-GUIDE.md`](ROO-CODE-GUIDE.md)**
   - How to work with Roo Code
   - Mode selection
   - Workflow patterns

### Reference as Needed:

- **[`memory-bank/progress.md`](../memory-bank/progress.md)** - Completed milestones
- **[`memory-bank/techContext.md`](../memory-bank/techContext.md)** - Tech details
- **[`memory-bank/systemPatterns.md`](../memory-bank/systemPatterns.md)** - Code patterns
- **[`.roo/rules/project-rules.md`](../.roo/rules/project-rules.md)** - TripBuilder rules

---

## 🎯 Your First Task

### Example: Create a New Trip

1. **Open Roo Code** in VS Code

2. **Read the pre-flight checklist:**
   - Open `.roo/rules/START-HERE.md`

3. **Check current context:**
   - Read `memory-bank/activeContext.md`

4. **Switch to Code mode** (if not already there)

5. **Navigate to the trip creation flow:**
   - Open `tripbuilder/app.py`
   - Find the `trip_new()` route
   - Understand how it works

6. **Test creating a trip:**
   ```bash
   # Make sure app is running
   cd tripbuilder
   python app.py
   
   # Visit http://localhost:5269/trips/new
   # Fill out form and submit
   ```

7. **Verify GHL sync:**
   - Check Flask console for sync messages
   - Log into GoHighLevel
   - Verify TripBooking opportunity was created

8. **Update documentation:**
   - Switch to Memory Manager mode
   - Update `memory-bank/progress.md` if this was a significant change

---

## 🔄 Daily Workflow

### Morning Routine

```bash
# 1. Navigate to project
cd /Users/ridiculaptop/Downloads/claude_code_tripbuilder

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Navigate to application
cd tripbuilder

# 4. Read context
# Open memory-bank/activeContext.md in Roo Code
# Review what you were working on

# 5. Start application (if needed)
python app.py
```

### During Development

1. **Check environment_details** before every command
2. **Reuse terminals** (don't create new ones)
3. **Use appropriate mode** for file types
4. **Follow TripBuilder patterns** from system

Patterns.md
5. **Update documentation** as you go

### End of Day

```bash
# 1. Update progress
# Switch to Memory Manager mode
# Update memory-bank/progress.md

# 2. Update active context
# Update memory-bank/activeContext.md

# 3. Commit changes (if using git)
git add .
git commit -m "Description of changes"

# 4. Deactivate virtual environment
deactivate
```

---

## 🛠️ Common Commands

### Application

```bash
# Run development server
python app.py

# Access database
psql -U ridiculaptop -d tripbuilder

# Initialize database
flask init-db

# Sync from GoHighLevel
flask sync-ghl
```

### Database

```bash
# Connect to database
psql -U ridiculaptop -d tripbuilder

# List tables
\dt

# Describe table
\d trips

# Check counts
SELECT COUNT(*) FROM trips;
SELECT COUNT(*) FROM passengers;
SELECT COUNT(*) FROM contacts;

# Exit
\q
```

### Python/Dependencies

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Reinstall all dependencies
pip install -r requirements.txt
```

---

## 🚨 Troubleshooting

### "Database doesn't exist"

```bash
createdb tripbuilder
flask init-db
```

### "Module not found"

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "GHL API error"

```bash
# Check .env file
cat .env

# Verify credentials are correct
# GHL_API_TOKEN should be from Private Integrations
# GHL_LOCATION_ID should match your location
```

### "Too many terminals"

**Problem:** Used `cd directory && command` syntax

**Solution:** 
- Check environment_details before commands
- Reuse existing terminals
- Read `.roo/rules/START-HERE.md`

---

## 📚 Learning Path

### Week 1: Setup & Basics
- [ ] Complete first-time setup
- [ ] Read all memory-bank files
- [ ] Understand project structure
- [ ] Create a test trip
- [ ] Enroll a test passenger

### Week 2: GHL Integration
- [ ] Understand bidirectional sync
- [ ] Read TWO_WAY_SYNC_COMPLETE.md
- [ ] Understand field mapping
- [ ] Test sync operations

### Week 3: Development
- [ ] Make first code change
- [ ] Follow TripBuilder patterns
- [ ] Update documentation
- [ ] Test changes thoroughly

### Week 4: Advanced
- [ ] Implement new feature
- [ ] Database migrations
- [ ] Error handling
- [ ] Performance optimization

---

## ✅ Checklist: Am I Ready?

Before starting development, verify:

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] PostgreSQL running
- [ ] Database initialized
- [ ] .env file configured
- [ ] Read memory-bank/projectBrief.md
- [ ] Read .roo/rules/START-HERE.md
- [ ] Read memory-bank/activeContext.md
- [ ] Know which mode to use
- [ ] Application runs successfully

---

## 🎯 Next Steps

Once you're set up:

1. **Read the Roo Code Guide:**
   - [`docs/ROO-CODE-GUIDE.md`](ROO-CODE-GUIDE.md)

2. **Understand the patterns:**
   - [`memory-bank/systemPatterns.md`](../memory-bank/systemPatterns.md)

3. **Review project rules:**
   - [`.roo/rules/project-rules.md`](../.roo/rules/project-rules.md)

4. **Start your first task:**
   - Check `memory-bank/activeContext.md` for what's next

---

**Last Updated:** October 27, 2025

**Need Help?** Check [`docs/ROO-CODE-GUIDE.md`](ROO-CODE-GUIDE.md) or [`.roo/rules/RULES-INDEX.md`](../.roo/rules/RULES-INDEX.md)