# TripBuilder Rules Index

**Complete reference for all operational rules and patterns**

---

## 📚 Rules Documentation

### 1. [START-HERE.md](START-HERE.md) ⭐ **READ FIRST**
**Pre-flight checklists for EVERY action**

Critical checklists before:
- Executing any command
- Switching modes
- Editing files
- Starting new tasks

**Priority:** 🔴 CRITICAL - Read before every action

---

### 2. [project-rules.md](project-rules.md)
**TripBuilder-specific operational rules**

Topics covered:
- GHL sync requirements
- Database schema rules
- File storage patterns
- Field mapping conventions
- Error handling standards

**When to read:** Starting any TripBuilder development work

---

### 3. [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md)
**Detailed terminal management and mode selection**

Deep dive into:
- Terminal lifecycle management
- Mode capabilities matrix
- Context awareness patterns
- Anti-patterns to avoid
- Efficiency best practices

**When to read:** Confused about terminal/mode usage

---

### 4. [README.md](README.md)
**Rules system navigation guide**

Quick overview of:
- How to use this rules system
- When to read each file
- How rules are organized

**When to read:** First time using rules system

---

## 🎯 Quick Access by Situation

### "I'm about to execute a command"
→ Read: [START-HERE.md](START-HERE.md) - Command Execution Checklist

### "I need to switch modes"
→ Read: [START-HERE.md](START-HERE.md) - Mode Selection Checklist

### "I'm starting TripBuilder development"
→ Read: [project-rules.md](project-rules.md) - Project Setup

### "Terminals are proliferating!"
→ Read: [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md) - Terminal Management

### "I need to sync with GHL"
→ Read: [project-rules.md](project-rules.md) - GHL Sync Rules

### "I'm editing files"
→ Read: [START-HERE.md](START-HERE.md) - File Edit Checklist

---

## 📖 Reading Order for New Contributors

**Day 1:**
1. [README.md](README.md) - Overview
2. [START-HERE.md](START-HERE.md) - Critical checklists
3. [project-rules.md](project-rules.md) - TripBuilder specifics

**Day 2:**
4. [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md) - Deep dive

**Ongoing:**
- Re-read [START-HERE.md](START-HERE.md) before every session
- Reference [project-rules.md](project-rules.md) when working on specific features

---

## 🔍 Rules by Category

### Terminal Management
- [START-HERE.md](START-HERE.md) - Command Execution Checklist
- [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md) - Full guide

### Mode Selection
- [START-HERE.md](START-HERE.md) - Mode Selection Checklist
- [terminal-and-mode-efficiency.md](terminal-and-mode-efficiency.md) - Mode capabilities

### TripBuilder Development
- [project-rules.md](project-rules.md) - All project-specific rules
- [START-HERE.md](START-HERE.md) - TripBuilder-specific section

### File Editing
- [START-HERE.md](START-HERE.md) - File Edit Checklist
- [project-rules.md](project-rules.md) - File-specific rules

---

## ✅ Compliance Checklist

Use this to verify you're following all rules:

### Before Starting Work:
- [ ] Read START-HERE.md
- [ ] Checked environment_details for active terminals
- [ ] Identified current working directory
- [ ] Verified current mode capabilities
- [ ] Reviewed project-rules.md for relevant sections

### During Work:
- [ ] Using correct mode for file types
- [ ] Reusing existing terminals
- [ ] Following TripBuilder patterns
- [ ] Handling errors gracefully
- [ ] Updating documentation as needed

### After Completing Work:
- [ ] Updated memory-bank files
- [ ] Verified all changes work
- [ ] No orphaned terminals
- [ ] Documentation reflects reality

---

## 🚨 Emergency Reference

**Terminal proliferation happening?**
```
STOP! Check environment_details NOW.
Don't use cd && command.
Reuse existing terminals.
```

**Wrong mode for file?**
```
STOP! Check mode capabilities in START-HERE.md.
Switch to appropriate mode BEFORE editing.
```

**GHL sync failing?**
```
CHECK: field_mapping.py for correct mappings
CHECK: .env for valid credentials
READ: project-rules.md GHL section
```

**Database errors?**
```
CHECK: Current schema with \d table_name
READ: project-rules.md Database section
VERIFY: models.py matches actual schema
```

---

## 📈 Success Metrics

You're following the rules when:
- ✅ 1-2 terminals max per session
- ✅ Zero mode restriction violations
- ✅ Zero `cd && command` usage
- ✅ Context always clear
- ✅ Documentation stays current

---

**Last Updated:** October 27, 2025
**Status:** Active
**Compliance:** Mandatory