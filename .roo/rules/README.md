# TripBuilder Rules System

**Welcome to the TripBuilder operational rules!**

This directory contains all the rules and patterns for efficient development of the TripBuilder project.

---

## 📚 Files in this Directory

1. **[START-HERE.md](START-HERE.md)** ⭐ **READ FIRST**
   - Mandatory pre-flight checklists
   - Must read before EVERY action
   - Terminal management rules
   - Mode selection guidelines

2. **[RULES-INDEX.md](RULES-INDEX.md)**
   - Complete index of all rules
   - Quick reference by situation
   - Compliance checklist
   - Emergency reference

3. **[project-rules.md](project-rules.md)**
   - TripBuilder-specific rules
   - GHL sync requirements
   - Database schema guidelines
   - Security and credentials
   - Error handling patterns

4. **[terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md)**
   - Detailed terminal management
   - Mode capabilities matrix
   - Anti-patterns to avoid
   - Best practices
   - Troubleshooting guide

5. **[README.md](README.md)** (this file)
   - Overview of rules system
   - How to use these files

---

## 🚀 Quick Start

### First Time Here?

1. Read [START-HERE.md](START-HERE.md) completely
2. Skim [RULES-INDEX.md](RULES-INDEX.md) to understand organization
3. Review [project-rules.md](project-rules.md) for TripBuilder specifics
4. Keep [START-HERE.md](START-HERE.md) open during work

### Every Session

**Before starting work:**
1. Read [START-HERE.md](START-HERE.md) checklists
2. Check `environment_details` for active terminals
3. Choose appropriate mode for your work

**During work:**
1. Follow the checklists in [START-HERE.md](START-HERE.md)
2. Reference [project-rules.md](project-rules.md) as needed
3. Update memory-bank files when completing tasks

**After work:**
1. Update `memory-bank/progress.md`
2. Update `memory-bank/activeContext.md`
3. Verify no orphaned terminals

---

## 🎯 Key Principles

### 1. Terminal Efficiency
- **Check `environment_details` before EVERY command**
- **Never use `cd directory && command` syntax**
- **Reuse existing terminals**
- Maximum 1-2 terminals per session

### 2. Mode Awareness
- **Verify mode can edit target file types**
- **Switch modes purposefully**
- **Stay in one mode for related tasks**
- Read mode restrictions before editing

### 3. TripBuilder Specifics
- **All code in `tripbuilder/` subdirectory**
- **Use field mapping utilities (never hardcode)**
- **Bidirectional sync is mandatory**
- **Graceful error handling always**

---

## 📖 When to Read Each File

### Read [START-HERE.md](START-HERE.md) when:
- ✅ Starting a work session
- ✅ About to execute a command
- ✅ About to switch modes
- ✅ About to edit any file
- ✅ Confused about what to do

### Read [RULES-INDEX.md](RULES-INDEX.md) when:
- ✅ Looking for specific rule category
- ✅ Need emergency reference
- ✅ Want to verify compliance
- ✅ Onboarding new team member

### Read [project-rules.md](project-rules.md) when:
- ✅ Starting TripBuilder development
- ✅ Working with GHL sync
- ✅ Modifying database schema
- ✅ Implementing new features
- ✅ Need error handling pattern

### Read [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md) when:
- ✅ Terminal count is increasing
- ✅ Confused about mode capabilities
- ✅ Want to understand deep details
- ✅ Troubleshooting efficiency issues

---

## 🚨 Emergency Situations

### "I have 5+ terminals!"
→ Read [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md) - Anti-Pattern #1

### "File edit was rejected!"
→ Read [START-HERE.md](START-HERE.md) - Mode Selection Checklist

### "GHL sync is failing!"
→ Read [project-rules.md](project-rules.md) - GHL Sync Rules

### "Database error!"
→ Read [project-rules.md](project-rules.md) - Database Rules

---

## 🎓 Learning Path

**Day 1:** Understanding the System
1. Read this README completely
2. Read [START-HERE.md](START-HERE.md) thoroughly
3. Skim other files to understand structure

**Day 2-7:** Building Habits
1. Use [START-HERE.md](START-HERE.md) checklists every time
2. Reference [project-rules.md](project-rules.md) as needed
3. Practice terminal reuse
4. Learn mode capabilities

**Week 2+:** Mastery
1. Rules become second nature
2. Efficient workflow established
3. Help others learn the system
4. Suggest improvements

---

## 📊 Success Metrics

You're following the rules when:
- ✅ 1-2 terminals max per session
- ✅ Zero `cd && command` usage
- ✅ Zero mode restriction violations
- ✅ Context always clear
- ✅ Documentation stays current
- ✅ No wasted actions

---

## 🔄 Rules Updates

**When rules change:**
- Last Updated date is updated in each file
- Changes are documented in that file
- Team is notified of significant changes

**Suggesting improvements:**
- Identify pattern that could be documented
- Note the situation and solution
- Submit suggestion for rules update

---

## 📁 Related Documentation

**Memory Bank (Active Context):**
- `memory-bank/projectBrief.md` - Requirements
- `memory-bank/progress.md` - What's done/next
- `memory-bank/activeContext.md` - Current work
- `memory-bank/techContext.md` - Technology stack
- `memory-bank/systemPatterns.md` - Code patterns

**TripBuilder Docs:**
- `tripbuilder/README.md` - Setup guide
- `tripbuilder/TWO_WAY_SYNC_COMPLETE.md` - Sync system
- `tripbuilder/PASSENGER_LINKING_COMPLETE.md` - Linking process

---

## ✅ Compliance

These rules are **MANDATORY** for all TripBuilder development.

**Violations indicate:**
- Rules not being read
- Lack of attention to detail
- Need for training/review

**Good compliance results in:**
- Efficient development
- Fewer errors
- Better code quality
- Easier onboarding
- Consistent codebase

---

## 🎯 The Golden Rule

**Read [START-HERE.md](START-HERE.md) before EVERY action.**

This single habit prevents 95% of issues and ensures efficient development.

---

**Last Updated:** October 27, 2025
**Status:** Active and Mandatory
**Compliance:** Required for all TripBuilder work