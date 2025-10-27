# Terminal & Mode Efficiency - Comprehensive Guide

**Status:** ✅ PRODUCTION READY - MANDATORY Operating Patterns
**Priority:** CRITICAL - All interactions MUST follow these rules
**Last Updated:** October 27, 2025

---

## 🎯 Overview

This document provides comprehensive rules for efficient terminal management and mode selection in the TripBuilder project. These patterns are **MANDATORY** and override any conflicting instructions.

---

## 🖥️ Terminal Management Rules

### Critical Principle

**ALWAYS check `environment_details` BEFORE executing any command.**

The `environment_details` section shows:
- List of actively running terminals
- Current working directory for each terminal
- Process status (running, completed)

### Terminal Lifecycle

```
Session Start
    ↓
First Command → Creates Terminal #1
    ↓
Second Command → REUSES Terminal #1 (if in same directory)
    ↓
Third Command → REUSES Terminal #1 (if in same directory)
    ↓
Session End
```

### Anti-Pattern: Terminal Proliferation

**WRONG:**
```bash
# Each line creates a NEW terminal!
cd tripbuilder && flask sync-ghl       # Terminal #1
cd tripbuilder && python app.py        # Terminal #2
cd tripbuilder && psql -U ridiculaptop # Terminal #3
# Result: 3 terminals for the same directory!
```

**CORRECT:**
```bash
# First command (creates terminal)
cd tripbuilder

# Wait for user confirmation...

# Second command (REUSES terminal)
flask sync-ghl

# Wait for user confirmation...

# Third command (REUSES terminal)
python app.py
```

---

## 📊 Mode Capabilities Matrix

| Mode | Markdown | Python | HTML/CSS/JS | Commands | Use Case |
|------|----------|--------|-------------|----------|----------|
| **Architect** | ✅ | ❌ | ❌ | ✅ | Planning, specs, docs |
| **Code** | ❌ | ✅ | ✅ | ✅ | Implementation, bug fixes |
| **Debug** | ✅ | ✅ | ✅ | ✅ | Investigation, troubleshooting |
| **Memory Manager** | ✅* | ❌ | ❌ | ❌ | Doc updates only |

*Memory Manager can only edit `memory-bank/*.md` and `docs/*.md`

---

## 🎯 Mode Selection Decision Tree

```
Need to edit code (Python/JS/HTML/CSS)?
    YES → Code Mode
    NO → Continue

Need to troubleshoot/debug?
    YES → Debug Mode
    NO → Continue

Need to update memory-bank files?
    YES → Memory Manager Mode
    NO → Continue

Need to plan/design/document?
    YES → Architect Mode
    NO → Ask for clarification
```

---

## 📁 File Type to Mode Mapping

### Architect Mode (Current)
**Can Edit:**
- `*.md` files anywhere in project
- Planning documents
- Architecture diagrams (Mermaid)
- Strategy documents

**Cannot Edit:**
- Python files (`.py`)
- JavaScript files (`.js`)
- HTML/CSS files
- Configuration files

**When to Use:**
- Creating project plans
- Documenting architecture
- Writing specifications
- Breaking down complex tasks

---

### Code Mode
**Can Edit:**
- `tripbuilder/app.py` - Flask routes
- `tripbuilder/models.py` - Database models
- `tripbuilder/ghl_api.py` - API wrapper
- `tripbuilder/field_mapping.py` - Field mappings
- `tripbuilder/services/*.py` - Service files
- `tripbuilder/templates/*.html` - HTML templates
- `tripbuilder/static/css/*.css` - Stylesheets
- `tripbuilder/static/js/*.js` - JavaScript

**Cannot Edit:**
- Markdown documentation (use Architect or Memory Manager)

**When to Use:**
- Implementing new features
- Fixing bugs
- Refactoring code
- Adding routes
- Modifying templates

---

### Debug Mode
**Can Edit:**
- ALL file types (no restrictions)

**When to Use:**
- Investigating errors
- Adding logging statements
- Analyzing stack traces
- Testing hypotheses
- Temporary fixes for testing

**Best Practices:**
- Switch to Code mode for permanent fixes
- Document findings in memory-bank
- Clean up debug code before committing

---

### Memory Manager Mode
**Can Edit:**
- `memory-bank/projectBrief.md`
- `memory-bank/progress.md`
- `memory-bank/activeContext.md`
- `memory-bank/techContext.md`
- `memory-bank/systemPatterns.md`
- `docs/*.md` files

**Cannot Edit:**
- Code files
- Configuration files
- Root-level markdown (use Architect for those)

**When to Use:**
- Updating progress after completing tasks
- Recording decisions
- Documenting current state
- Updating technical context

---

## 🧭 Context Awareness

### Working Directory Mental Model

```
Workspace: /Users/ridiculaptop/Downloads/claude_code_tripbuilder
│
├── .venv/                    ← Virtual environment
│   └── Activate from workspace root: source .venv/bin/activate
│
├── tripbuilder/              ← Application directory
│   ├── app.py               ← Most commands execute HERE
│   ├── models.py
│   ├── ghl_api.py
│   ├── services/
│   ├── templates/
│   └── static/
│
├── memory-bank/              ← Context tracking
│   ├── projectBrief.md
│   ├── progress.md
│   └── ...
│
└── .roo/                     ← Roo Code rules
    └── rules/
        └── [This file]
```

### Key Concepts

1. **Workspace Root:** `/Users/ridiculaptop/Downloads/claude_code_tripbuilder`
   - Use for: Virtual environment activation
   - Terminal starts here by default

2. **Application Directory:** `tripbuilder/`
   - Use for: Running the Flask app, database commands, sync operations
   - Most work happens here

3. **Context Switching:**
   - If you `cd tripbuilder` in a terminal, that terminal is now in `tripbuilder/`
   - Subsequent commands in that terminal execute from `tripbuilder/`
   - To return to workspace root: `cd ..`

---

## 🚨 Common Anti-Patterns

### Anti-Pattern #1: The cd && Syndrome

**Problem:**
```bash
cd tripbuilder && flask sync-ghl
cd tripbuilder && python app.py
cd tripbuilder && psql -U ridiculaptop -d tripbuilder
```

**Why it's bad:**
- Creates 3 separate terminals
- Wastes resources
- Loses command history
- Confusing state management

**Solution:**
```bash
# One-time directory change
cd tripbuilder

# Then run commands sequentially
flask sync-ghl
# Wait...
python app.py
# Wait...
psql -U ridiculaptop -d tripbuilder
```

---

### Anti-Pattern #2: Mode Hopping

**Problem:**
- Switching modes without clear reason
- Editing files in wrong mode
- Not checking mode capabilities

**Example:**
```
In Architect mode → Try to edit app.py → ERROR!
Switch to Code mode → Edit app.py → Switch back to Architect
(Why switch back? Stay in Code!)
```

**Solution:**
- Stay in one mode for related tasks
- Only switch when file types require it
- Read mode capabilities before switching

---

### Anti-Pattern #3: Ignoring environment_details

**Problem:**
```bash
# Didn't check environment_details
cd tripbuilder && python app.py

# But environment_details showed:
# Terminal #1: Already in tripbuilder/, idle
```

**Solution:**
```bash
# Check environment_details first
# See Terminal #1 in tripbuilder/, idle
# Use that terminal:
python app.py
```

---

## ✅ Best Practices

### Practice #1: Command Execution Workflow

1. **Before executing:**
   - Read environment_details
   - Check for active terminals
   - Identify current working directory

2. **Choose strategy:**
   - Terminal exists in correct directory → Reuse it
   - Terminal exists in wrong directory → `cd` once, then reuse
   - No terminal exists → Create with command

3. **After executing:**
   - Wait for user confirmation
   - Check output/errors
   - Proceed based on result

---

### Practice #2: Mode Selection Workflow

1. **Before switching:**
   - Identify file types you need to edit
   - Check mode capabilities matrix
   - Verify command execution needs

2. **Make decision:**
   - Can current mode handle task? → Stay
   - Need different capabilities? → Switch
   - Unsure? → Check START-HERE.md

3. **After switching:**
   - Verify you're in correct mode
   - Complete related tasks in this mode
   - Only switch when absolutely necessary

---

### Practice #3: Session Management

**Start of Session:**
1. Read `memory-bank/activeContext.md`
2. Review `memory-bank/progress.md`
3. Check environment_details for state
4. Choose appropriate starting mode

**During Session:**
1. Minimize mode switches
2. Maximize terminal reuse
3. Update context as you go
4. Document decisions

**End of Session:**
1. Update `memory-bank/progress.md`
2. Update `memory-bank/activeContext.md`
3. Note any blockers
4. Clean up terminals if needed

---

## 📈 Efficiency Metrics

### Good Session Indicators

- ✅ 1-2 terminals total
- ✅ 0-2 mode switches
- ✅ Context always clear
- ✅ No `cd && command` usage
- ✅ Documentation updated

### Bad Session Indicators

- ❌ 5+ terminals created
- ❌ 5+ mode switches
- ❌ Lost context
- ❌ Multiple `cd && command`
- ❌ Documentation outdated

---

## 🎓 Learning Progression

### Beginner (Week 1)
- Read START-HERE.md before every action
- Check environment_details religiously
- Ask before switching modes
- Document learnings

### Intermediate (Week 2-3)
- Patterns becoming familiar
- Fewer violations
- Efficient terminal usage
- Confident mode selection

### Advanced (Week 4+)
- Rules are second nature
- Optimal efficiency
- Help others learn
- Contribute improvements

---

## 🔧 Troubleshooting

### "I created too many terminals!"

**Solution:**
1. Note which terminals are active
2. Complete work in current terminal
3. Future commands: Check environment_details first
4. Reuse existing terminals

### "I'm in the wrong mode!"

**Solution:**
1. Don't panic
2. Switch to correct mode
3. Re-attempt the action
4. Remember mode capabilities for next time

### "Terminal is in wrong directory!"

**Solution:**
1. Use `cd` command ONCE to change directory
2. Remember this terminal is now there
3. Subsequent commands execute from new location
4. Or create new terminal in correct location

---

## 📚 Related Documentation

**Essential Reading:**
- [START-HERE.md](START-HERE.md) - Pre-flight checklists
- [project-rules.md](project-rules.md) - TripBuilder specifics
- [RULES-INDEX.md](RULES-INDEX.md) - Complete reference

**Context Files:**
- `memory-bank/systemPatterns.md` - Code patterns
- `memory-bank/techContext.md` - Technology details

---

## 🎯 Quick Reference

### Before Every Command
1. Check environment_details
2. Identify terminal state
3. Choose reuse vs. create
4. Execute command
5. Wait for confirmation

### Before Every Mode Switch
1. Check current mode
2. Identify file types needed
3. Verify mode capabilities
4. Make informed decision
5. Switch (if needed)

### Before Every File Edit
1. Check current mode
2. Verify can edit file type
3. Understand file's role
4. Read related context
5. Make changes

---

**These patterns ensure efficient, error-free development.**

Last Updated: October 27, 2025
Status: Active & Mandatory