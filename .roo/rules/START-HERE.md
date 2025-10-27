# ⚠️ MANDATORY PRE-FLIGHT CHECKLIST ⚠️

**READ THIS BEFORE EVERY SINGLE ACTION**

This checklist is **NON-NEGOTIABLE**. Violations will result in wasted time, broken code, and terminal chaos.

---

## 🚨 CRITICAL STOP POINTS - CHECK BEFORE PROCEEDING

### ✋ BEFORE EXECUTING ANY COMMAND

**STEP 1: CHECK ENVIRONMENT_DETAILS**
```
Look for the "Actively Running Terminals" section in environment_details.
If it exists, you MUST reuse that terminal!
```

**STEP 2: VERIFY WORKING DIRECTORY**
```
Check what directory the existing terminal is in.
If it's already in the right place, DO NOT cd!
```

**STEP 3: CHOOSE COMMAND FORMAT**
```
❌ NEVER: cd [directory] && command
✅ ALWAYS: command (if terminal is already in [directory]/)
✅ ALWAYS: cd [directory] (once, then reuse terminal)
```

**CRITICAL: The TripBuilder application lives in `tripbuilder/` subdirectory!**

---

### ✋ BEFORE SWITCHING MODES

**STEP 1: CHECK CURRENT MODE**
```
Am I in the right mode for the files I need to edit?
```

**STEP 2: VERIFY FILE RESTRICTIONS**

| Mode | Can Edit | Purpose |
|------|----------|---------|
| **Architect** | `*.md` files only | Planning, documentation |
| **Code** | Python, HTML, CSS, JS | Implementation |
| **Debug** | All files | Troubleshooting |
| **Memory Manager** | `memory-bank/*.md`, `docs/*.md` | Doc updates |

**STEP 3: DECIDE IF SWITCH IS NEEDED**
```
Can my current mode handle this task?
If YES → Stay in current mode
If NO → Switch to appropriate mode
```

---

## 📋 MANDATORY CHECKLISTS

### Command Execution Checklist

Before executing EVERY command, verify:

- [ ] I checked `environment_details` for "Actively Running Terminals"
- [ ] I identified if a terminal already exists in the target directory
- [ ] I am NOT using `cd directory && command` syntax
- [ ] I understand this command will reuse an existing terminal OR create a new one
- [ ] I know what working directory this command will execute in
- [ ] For TripBuilder commands, I'm in the `tripbuilder/` directory

**If you cannot check ALL boxes, DO NOT EXECUTE THE COMMAND!**

---

### Mode Selection Checklist

Before switching modes, verify:

- [ ] I checked what file types I need to edit
- [ ] I verified the target mode can edit those file types
- [ ] I confirmed the target mode can execute commands (if needed)
- [ ] I have a clear reason for the mode switch
- [ ] I read the mode's role definition in `.roomodes`

**If you cannot check ALL boxes, DO NOT SWITCH MODES!**

---

### File Edit Checklist

Before editing ANY file, verify:

- [ ] I'm in the correct mode for this file type
- [ ] I understand the file's purpose in the project
- [ ] I've read related files for context
- [ ] I know if this affects sync operations (trips/passengers)
- [ ] I've considered error handling implications

**For TripBuilder-specific files:**
- [ ] Does this affect GHL sync? (if yes, update sync services)
- [ ] Does this affect field mapping? (if yes, update field_mapping.py)
- [ ] Does this affect file storage? (if yes, update file_manager.py)

---

## 🔴 RED ALERT: VIOLATIONS TO NEVER COMMIT

### Violation #1: Multiple `cd &&` Commands
```bash
# 🚫 WRONG - Creates 3 terminals!
cd tripbuilder && flask sync-ghl
cd tripbuilder && python app.py
cd tripbuilder && psql -U ridiculaptop -d tripbuilder

# ✅ CORRECT - Use one terminal
cd tripbuilder
# Wait for result...
flask sync-ghl
# Wait for result...
python app.py
```

### Violation #2: Editing Wrong File Type in Mode
```markdown
# 🚫 WRONG - In Architect mode, trying to edit Python
app.py needs a new route...  (CANNOT DO THIS IN ARCHITECT MODE!)

# ✅ CORRECT - Switch to Code mode first
Switch to Code mode → then edit app.py
```

### Violation #3: Ignoring Environment Details
```bash
# 🚫 WRONG - Didn't check environment_details
cd tripbuilder && python app.py
# (What if terminal is already in tripbuilder/?)

# ✅ CORRECT - Check first
# Read environment_details → Terminal #1 in tripbuilder/
python app.py  # Use existing terminal!
```

---

## 🎯 CONTEXT AWARENESS RULES

### Understanding Working Directory

**Project Root:** `/Users/ridiculaptop/Downloads/claude_code_tripbuilder`

**Application Code:** `tripbuilder/` subdirectory

**Mental Model:**
```
/Users/ridiculaptop/Downloads/claude_code_tripbuilder/  ← Workspace root
├── .venv/                    ← Virtual environment (activate from here)
├── memory-bank/              ← Roo Code context
├── .roo/                     ← Roo Code rules (you are here!)
├── tripbuilder/              ← APPLICATION CODE (most work here)
│   ├── app.py               ← Flask application
│   ├── models.py            ← Database models
│   ├── ghl_api.py           ← GHL API wrapper
│   ├── services/            ← Sync services
│   ├── templates/           ← HTML templates
│   └── static/              ← CSS, JavaScript
└── [Old root docs]          ← Outdated (use memory-bank instead)
```

**Key Rules:**
1. **Virtual environment activation:** From workspace root (`source .venv/bin/activate`)
2. **Application commands:** From `tripbuilder/` directory (`cd tripbuilder`, then run commands)
3. **File edits:** Paths relative to workspace root, but most code in `tripbuilder/`

---

## 📖 QUICK REFERENCE GUIDE

### When to Create New Terminal vs Reuse

**Create New Terminal When:**
- No active terminals exist
- Need to work in a different directory permanently
- Previous terminal has a long-running process

**Reuse Existing Terminal When:**
- Terminal exists in correct directory (CHECK environment_details!)
- Previous command completed
- Working in same project area (most common case)

---

### Mode Quick Guide

| Task | Recommended Mode | Why |
|------|-----------------|-----|
| Update memory-bank files | Memory Manager | Can only edit .md in memory-bank/ |
| Create architectural plan | Architect | Planning and design docs |
| Implement new feature | Code | Edit Python/HTML/CSS/JS |
| Fix a bug | Code or Debug | Debug for investigation, Code for fix |
| Update progress docs | Memory Manager or Architect | Both can edit docs |
| Add route to app.py | Code | Python file editing |
| Modify template | Code | HTML file editing |

---

## 🎓 TripBuilder-Specific Rules

### Before Any GHL-Related Work:

1. **Read sync documentation:**
   - [`tripbuilder/TWO_WAY_SYNC_COMPLETE.md`](../tripbuilder/TWO_WAY_SYNC_COMPLETE.md)
   - [`memory-bank/systemPatterns.md`](../memory-bank/systemPatterns.md)

2. **Understand field mappings:**
   - Review [`tripbuilder/field_mapping.py`](../tripbuilder/field_mapping.py)
   - Check TRIP_FIELD_MAP and PASSENGER_FIELD_MAP

3. **Know the pipelines:**
   - TripBooking: `IlWdPtOpcczLpgsde2KF` (5 stages)
   - Passenger: `fnsdpRtY9o83Vr4z15bE` (6 stages)

### Before Any Database Work:

1. **Check current schema:**
   ```bash
   psql -U ridiculaptop -d tripbuilder
   \dt  # List tables
   \d trips  # Describe trips table
   ```

2. **Understand relationships:**
   - Trips ← Passengers (via trip_id and trip_name)
   - Passengers → Contacts (via contact_id)
   - Passengers → PipelineStages (via stage_id)

### Before Any File Storage Work (S3):

1. **Verify S3 is implemented:**
   - Check if `services/file_manager.py` exists
   - Check if AWS credentials are in `.env`
   - Status: **PLANNED** (not yet implemented)

2. **Understand directory structure:**
   ```
   s3://tripbuilder-files/
   └── trips/{trip-name}/
       └── passengers/{passenger-name}/
           ├── passports/
           ├── signatures/
           └── documents/
   ```

---

## ✅ SUCCESS INDICATORS

You're following the rules when:

- ✅ Terminal count stays at 1-2 per session
- ✅ Zero `cd && command` violations
- ✅ Mode switches are purposeful and minimal
- ✅ All file edits respect mode restrictions
- ✅ Environment details checked before every command
- ✅ Context always maintained across sessions

---

**Status:** Active - Use This Before EVERY Action
**Priority:** CRITICAL - Non-Negotiable
**Location:** `.roo/rules/START-HERE.md`

---

**Read this checklist BEFORE:**
- Executing any command
- Switching modes
- Editing any file
- Starting a new task

**Your efficiency depends on following these rules!**

Last Updated: October 27, 2025