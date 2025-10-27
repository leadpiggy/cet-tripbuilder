# Roo Code Guide for TripBuilder

**How to work efficiently with Roo Code on the TripBuilder project**

---

## 🎯 Quick Start

### Before Every Session

1. **Read the Pre-Flight Checklist:**
   - Open [`.roo/rules/START-HERE.md`](../.roo/rules/START-HERE.md)
   - Review checklists before executing commands or switching modes

2. **Check Project State:**
   - Read [`memory-bank/activeContext.md`](../memory-bank/activeContext.md) - What's happening now
   - Review [`memory-bank/progress.md`](../memory-bank/progress.md) - What's done, what's next

3. **Understand the Context:**
   - Check [`memory-bank/projectBrief.md`](../memory-bank/projectBrief.md) - Requirements
   - Review [`memory-bank/techContext.md`](../memory-bank/techContext.md) - Tech stack

---

## 📁 Documentation Structure

### Memory Bank (Living Documentation)
**Location:** `memory-bank/`

These files are **actively maintained** and represent the current project state:

- **`projectBrief.md`** - Requirements, scope, technology decisions
- **`progress.md`** - Completed milestones, what's next, known issues
- **`activeContext.md`** - Current focus, immediate next steps
- **`techContext.md`** - Technology stack, configuration, commands
- **`systemPatterns.md`** - Code patterns, best practices, anti-patterns

**Update these after every major change!**

### Rules System
**Location:** `.roo/rules/`

Operational rules for efficient development:

- **`START-HERE.md`** ⭐ **READ FIRST** - Mandatory pre-flight checklists
- **`RULES-INDEX.md`** - Complete index of all rules
- **`project-rules.md`** - TripBuilder-specific rules
- **`terminal-and-mode-efficiency.md`** - Terminal/mode best practices
- **`README.md`** - Rules navigation guide

### Old Documentation
**Location:** Root directory (`.md` files)

**⚠️ OUTDATED - DO NOT UPDATE**

These files are from earlier project phases:
- `PROJECT_DESCRIPTION.md`
- `TECH_STACK.md`
- `ARCHITECTURE.md`
- `FEATURES.md`

**Use memory-bank files instead for current information.**

---

## 🎨 Custom Modes

TripBuilder has 8 custom modes for specialized workflows:

### 1. 🏗️ Architect Mode
**Use for:** Planning, documentation, strategy
**Can edit:** `*.md` files only
**Can execute commands:** Yes

**When to use:**
- Creating project plans
- Writing specifications
- Documenting architecture
- Breaking down complex tasks

### 2. 💻 Code Mode
**Use for:** Implementation, bug fixes
**Can edit:** Python, JS, HTML, CSS, JSON, YAML
**Can execute commands:** Yes

**When to use:**
- Implementing features
- Fixing bugs
- Modifying templates
- Updating configurations

### 3. 🪲 Debug Mode
**Use for:** Troubleshooting, investigation
**Can edit:** All files
**Can execute commands:** Yes

**When to use:**
- Investigating errors
- Adding logging
- Testing hypotheses
- Temporary fixes

### 4. 📝 Memory Manager Mode
**Use for:** Documentation updates
**Can edit:** `memory-bank/*.md`, `docs/*.md`
**Can execute commands:** No

**When to use:**
- Updating progress after tasks
- Recording decisions
- Documenting current state

### 5. 🪃 Orchestrator Mode
**Use for:** Complex multi-step projects
**Can edit:** All files
**Can execute commands:** Yes

**When to use:**
- Coordinating multiple subtasks
- Breaking down large projects
- Delegating to other modes

### 6. 🗄️ Database Mode
**Use for:** Database operations
**Can edit:** Python models, SQL files
**Can execute commands:** Yes

**When to use:**
- Schema changes
- Migrations
- Query optimization

### 7. 📁 File Manager Mode
**Use for:** S3 file operations
**Can edit:** Python services, HTML templates
**Can execute commands:** Yes

**When to use:**
- Implementing file uploads
- Working with S3
- Image processing

### 8. 🔌 API Integration Mode
**Use for:** GHL API work
**Can edit:** Python files
**Can execute commands:** Yes

**When to use:**
- Working with GHL API
- API error handling
- Rate limiting

---

## 🖥️ Terminal Management

### The Golden Rule
**Check `environment_details` before EVERY command!**

### Right Way vs Wrong Way

**❌ WRONG (Creates 3 Terminals):**
```bash
cd tripbuilder && flask sync-ghl
cd tripbuilder && python app.py
cd tripbuilder && psql -U ridiculaptop -d tripbuilder
```

**✅ RIGHT (Reuses 1 Terminal):**
```bash
# First command (creates terminal)
cd tripbuilder

# Wait for confirmation...

# Second command (reuses terminal)
flask sync-ghl

# Wait for confirmation...

# Third command (reuses terminal)
python app.py
```

### Terminal Checklist

Before executing any command:

1. [ ] Check `environment_details` for "Actively Running Terminals"
2. [ ] Identify if terminal exists in target directory
3. [ ] Do NOT use `cd directory && command` syntax
4. [ ] Know which directory command will execute in

---

## 🔄 Workflow Patterns

### Starting a New Feature

1. **Switch to Architect Mode**
   - Plan the feature
   - Document requirements
   - Break into steps

2. **Switch to Code Mode**
   - Implement the feature
   - Follow TripBuilder patterns
   - Add error handling

3. **Test the Feature**
   - Run application
   - Verify GHL sync
   - Check database

4. **Switch to Memory Manager Mode**
   - Update `progress.md`
   - Update `activeContext.md`
   - Document decisions

### Fixing a Bug

1. **Switch to Debug Mode**
   - Investigate error
   - Add logging
   - Test hypotheses

2. **Switch to Code Mode**
   - Implement permanent fix
   - Remove debug code
   - Add tests

3. **Switch to Memory Manager Mode**
   - Document the fix
   - Update known issues

### Working with Database

1. **Switch to Database Mode**
   - Verify current schema
   - Create migration script
   - Test migration

2. **Run migration**
   - Apply to development DB
   - Verify schema matches models

3. **Switch to Memory Manager Mode**
   - Document schema changes
   - Update tech context

---

## 📋 Daily Workflow

### Morning Routine

1. Read `memory-bank/activeContext.md`
2. Review `memory-bank/progress.md`
3. Check `.roo/rules/START-HERE.md`
4. Choose appropriate mode

### During Work

1. Follow pre-flight checklists
2. Reuse terminals
3. Update context as you go
4. Document decisions

### End of Day

1. Update `memory-bank/progress.md`
2. Update `memory-bank/activeContext.md`
3. Note any blockers
4. Clean up terminals

---

## ✅ Success Indicators

You're doing it right when:

- ✅ 1-2 terminals max per session
- ✅ Zero `cd && command` usage
- ✅ Zero mode restriction violations
- ✅ Context always clear
- ✅ Documentation stays current
- ✅ No wasted actions

---

## 🚨 Common Mistakes to Avoid

### 1. Terminal Proliferation
**Problem:** Using `cd directory && command` creates new terminals every time

**Solution:** `cd` once, then run commands sequentially

### 2. Wrong Mode for File Type
**Problem:** Trying to edit Python in Architect mode

**Solution:** Check mode capabilities before editing

### 3. Ignoring Environment Details
**Problem:** Not checking if terminal exists before creating new one

**Solution:** Always check `environment_details` first

### 4. Hardcoding Field Keys
**Problem:** Using `opportunity.tripname` directly in code

**Solution:** Use field mapping utilities from `field_mapping.py`

### 5. Outdated Documentation
**Problem:** Updating root `.md` files instead of memory-bank

**Solution:** Always update memory-bank files

---

## 🎓 Learning Resources

### Essential Reading (In Order)

1. [`.roo/rules/START-HERE.md`](../.roo/rules/START-HERE.md) - **READ FIRST**
2. [`.roo/rules/project-rules.md`](../.roo/rules/project-rules.md) - TripBuilder rules
3. [`memory-bank/systemPatterns.md`](../memory-bank/systemPatterns.md) - Code patterns

### Reference Documentation

- [`.roo/rules/RULES-INDEX.md`](../.roo/rules/RULES-INDEX.md) - Complete rules reference
- [`.roo/rules/terminal-and-mode-efficiency.md`](../.roo/rules/terminal-and-mode-efficiency.md) - Deep dive
- [`tripbuilder/TWO_WAY_SYNC_COMPLETE.md`](../tripbuilder/TWO_WAY_SYNC_COMPLETE.md) - Sync system

---

## 💡 Pro Tips

1. **Keep START-HERE.md open** in a separate window during work
2. **Use Memory Manager mode** to update docs immediately after completing tasks
3. **Read activeContext.md** at the start of every session
4. **Check environment_details** before every single command
5. **Stay in one mode** for related tasks
6. **Document as you go** instead of at the end

---

## 🆘 Getting Help

### Emergency Reference

**Terminal issues?**
→ [`.roo/rules/terminal-and-mode-efficiency.md`](../.roo/rules/terminal-and-mode-efficiency.md)

**Mode restrictions?**
→ [`.roo/rules/START-HERE.md`](../.roo/rules/START-HERE.md)

**GHL sync failing?**
→ [`.roo/rules/project-rules.md`](../.roo/rules/project-rules.md)

**Database errors?**
→ [`.roo/rules/project-rules.md`](../.roo/rules/project-rules.md)

---

**Last Updated:** October 27, 2025

**Remember:** This system is designed for efficiency. Follow the rules, and you'll save time and avoid errors!