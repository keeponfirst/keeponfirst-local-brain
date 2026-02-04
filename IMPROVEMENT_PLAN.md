# Improvement Plan: keeponfirst-local-brain

> **For AI Agents**: This document contains actionable improvement items. Each item includes exact file paths, line numbers, and expected changes. Execute items in priority order.

---

## 🔴 Priority 1: Fix Existing Bugs

### 1.1 Fix README.md Typo (Line 103)

**File**: [README.md](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/README.md#L103)

**Problem**: Line 103 contains `## Record Typesrify Setup` which is a concatenation error.

**Action**: Replace line 103 with two separate sections:
```diff
-## Record Typesrify Setup
+## Verify Setup
```

---

### 1.2 Remove Duplicate Content in SKILL.md (Lines 130-146)

**File**: [SKILL.md](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/skills/keeponfirst-local-brain-skill/SKILL.md#L130-L151)

**Problem**: "Step 5: Execute" section is duplicated (lines 130-146 repeat lines 135-151).

**Action**: Delete lines 130-134 (the duplicate header and first part), keeping only one "Step 5" block.

---

## 🟡 Priority 2: Improve Maintainability

### 2.1 Create Sync Script for Code Duplication

**Problem**: `scripts/` and `skills/keeponfirst-local-brain-skill/scripts/` contain duplicate files that must be manually synced.

**Action**: Create [scripts/sync.sh](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/scripts/sync.sh):
```bash
#!/bin/bash
# Sync scripts to skill directory
SKILL_DIR="skills/keeponfirst-local-brain-skill/scripts"
cp scripts/config.py "$SKILL_DIR/"
cp scripts/notion_api.py "$SKILL_DIR/"
cp scripts/write_record.py "$SKILL_DIR/"
cp scripts/log_manager.py "$SKILL_DIR/"
cp scripts/search.py "$SKILL_DIR/"
echo "✅ Scripts synced to skill directory"
```

---

### 2.2 Add Structured Error Codes to write_record.py

**File**: [write_record.py](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/scripts/write_record.py#L244-L254)

**Problem**: Exceptions only return generic error strings.

**Action**: Add error codes in the except block (around line 248):
```python
except Exception as e:
    error_code = "UNKNOWN_ERROR"
    if "NOTION_TOKEN" in str(e):
        error_code = "NOTION_AUTH_FAILED"
    elif "Invalid" in str(e):
        error_code = "INVALID_INPUT"
    print(json.dumps({
        "success": False,
        "error_code": error_code,
        "error": str(e)
    }, indent=2))
```

---

### 2.3 Move Debug Scripts to tests/

**Problem**: Debug scripts exist in `scripts/`:
- `scripts/simulate_capture.py`
- `scripts/debug_log_resolution.py`

**Action**:
```bash
mv scripts/simulate_capture.py tests/
mv scripts/debug_log_resolution.py tests/
```

---

## 🟢 Priority 3: Enhancements

### 3.1 Create CHANGELOG.md

**Action**: Create [CHANGELOG.md](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/CHANGELOG.md):
```markdown
# Changelog

## [1.1.0] - 2026-01-21
### Added
- Bi-directional brain: `/search`, `/recall`, `/trace` commands
- Rich content rendering (code blocks, link previews)
- `PRIMARY_LANGUAGE` setting for localized record generation
- Context-aware capture with related record suggestions

### Fixed
- Central storage resolution for cross-project usage

## [1.0.0] - 2026-01-15
### Added
- Initial release
- Record types: Decision, Worklog, Idea, Backlog, Note
- Notion API integration (page mode)
- Local-first storage with JSON + Markdown
```

---

### 3.2 Improve .gitignore

**File**: [.gitignore](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/.gitignore)

**Action**: Append these lines:
```gitignore
# Mac
.DS_Store

# Python
__pycache__/
*.pyc
.venv/

# IDE
.idea/
.vscode/

# Temp
*.tmp
/tmp/
```

---

### 3.3 Add Agent Language Instruction to SKILL.md

**File**: [SKILL.md](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/skills/keeponfirst-local-brain-skill/SKILL.md#L102-L104)

**Problem**: `PRIMARY_LANGUAGE` is documented but Agent may not actively read `.env`.

**Action**: Add this note after line 104:
```markdown
> [!IMPORTANT]
> Before generating any record, check if `PRIMARY_LANGUAGE` is set in the project's `.env` file. If set to `zh-TW`, all titles and body content MUST be written in Traditional Chinese.
```

---

## 📋 Checklist for AI Execution

- [ ] 1.1 Fix README.md typo
- [ ] 1.2 Remove SKILL.md duplicate
- [ ] 2.1 Create sync.sh
- [ ] 2.2 Add error codes
- [ ] 2.3 Move debug scripts
- [ ] 3.1 Create CHANGELOG.md
- [ ] 3.2 Improve .gitignore
- [ ] 3.3 Add language instruction

---

## Post-Execution

After completing all items:
1. Run `bash scripts/sync.sh` to sync changes to skill directory
2. Run `cp -r skills/keeponfirst-local-brain-skill ~/.gemini/antigravity/skills/` to update global installation
3. Commit with message: `refactor: Apply improvement plan (fix bugs, add changelog, improve maintainability)`
