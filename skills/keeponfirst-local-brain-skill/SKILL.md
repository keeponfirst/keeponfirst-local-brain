---
name: keeponfirst-local-brain-skill
description: Local-first brain capture system. Triggers: /kof-cap, /kof-decision, /kof-idea, /kof-backlog, /kof-worklog, /kof-note
---

# Keeponfirst Local Brain Skill

A local-first brain capture system with AI assistance.

## Triggers

| Trigger | Action |
|---------|--------|
| `/kof-cap` | Capture with auto-classification |
| `/kof-decision` | Force decision record |
| `/kof-idea` | Force idea record |
| `/kof-backlog` | Force backlog record |
| `/kof-worklog` | Force worklog record |
| `/kof-note` | Raw capture (fallback) |

### MCP-Powered Features (Read/Search)

> [!NOTE]
> These features require Notion MCP Server to be configured. See [docs/NOTION_MCP_SETUP.md](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/docs/NOTION_MCP_SETUP.md).

| Trigger | Action |
|---------|--------|
| `/search <query>` | Search all records in Notion |
| `/recall <timeframe>` | Summarize past records by time/topic |
| `/trace <topic>` | Track idea evolution timeline |
| Context-aware capture | Auto-reference related records when capturing |

---

## Installation

```bash
git clone https://github.com/keeponfirst/keeponfirst-local-brain.git
cp -r keeponfirst-local-brain/skills/keeponfirst-local-brain-skill ~/.gemini/antigravity/skills/
```

---

## First-Time Setup (Per Project)

```bash
~/.gemini/antigravity/skills/keeponfirst-local-brain-skill/scripts/init.sh
```

This creates:
- `.env` from template
- `records/` directory structure
- Python virtual environment

Configure `.env`:
```env
NOTION_TOKEN=secret_xxxxx
NOTION_PARENT=your-page-id-here
NOTION_MODE=page
```

---

## Central Log Configuration
This skill uses a Central Log to track execution history across different workspaces.

**Resolution Priority:**
1. `ANTIGRAVITY_LOG_HOME` environment variable
2. `config.json` in skill directory (set via interactive prompt)
3. Auto-detection (looks for `.agentic/CENTRAL_LOG_MARKER` in parent directories)
4. Interactive Prompt (asks you to specify location on first run)

**Default Location:** `keeponfirst-local-brain/.agentic/logs/`

---

## Record Types

| Type | Emoji | Use For |
|------|-------|---------|
| **Decision** | ⚖️ | Choices, trade-offs, rationale |
| **Worklog** | 📝 | Daily activities, learnings |
| **Idea** | 💡 | Inspirations, possibilities |
| **Backlog** | 📋 | Future tasks, TODOs |
| **Note** | 📄 | Raw capture, unclassified |

---

## Capture Workflow

### Step 1: Capture
User provides natural language input with trigger.

### Step 2: Interpret
- `/kof-cap` → AI determines type automatically
- `/kof-decision|idea|backlog|worklog` → Force specific type
- `/kof-note` → Raw capture without structure

### Step 3: Draft
Generate structured content with appropriate template.

### Step 4: Preview & Confirm ⚠️ CRITICAL

**ALWAYS show preview before writing:**

```
我判斷這是一筆【TYPE】記錄，整理如下：

---
**TITLE**

BODY
---

Tags: TAGS
Date: DATE

請選擇：
✅ 確認寫入
✏️ 修改
❌ 取消
```

**DO NOT WRITE WITHOUT USER CONFIRMATION.**

### Step 5: Execute

Only after user confirms:

1. Write draft JSON to temp file `/tmp/kof_record.json`
### Step 5: Execute

Only after user confirms:

1. Write draft JSON to temp file `/tmp/kof_record.json`
2. Run the script from the global skill directory:

```bash
SKILL_ROOT="$HOME/.gemini/antigravity/skills/keeponfirst-local-brain-skill"
# Execute using the skill's own virtual environment
$SKILL_ROOT/.venv/bin/python $SKILL_ROOT/scripts/write_record.py --input /tmp/kof_record.json
```

> [!NOTE]
> Using `--input` with a temp file is more reliable than `--stdin`.
> Using absolute paths ensures the skill works from any directory.

Draft JSON format:
```json
{
  "type": "decision|worklog|idea|backlog|note",
  "title": "Concise title",
  "body": "Structured markdown content",
  "source_text": "Original user input",
  "date": "YYYY-MM-DD",
  "tags": ["tag1", "tag2"]
}
```

> [!TIP]
> **Rich Content Support**:
> - **Code Blocks**: \`\`\`python ... \`\`\` will be rendered as native Notion code blocks.
> - **Link Previews**: Standalone URLs on their own line (e.g. `https://github.com/...`) will be rendered as Notion Bookmarks.

### Step 6: Report

```
✅ 記錄完成！

📝 Remote: {url}
💾 本地: {local_path}

Type: {TYPE}
Title: {TITLE}
```

---

## Templates

### Decision ⚖️
```markdown
## Context
<why this decision was needed>

## Options Considered
- Option A: ...
- Option B: ...

## Chosen
<what was chosen>

## Rationale
<why this choice>

## Trade-offs
<what was sacrificed>
```

### Worklog 📝
```markdown
## Activities
- <what was done>

## Learnings
<insights gained>

## Blockers
<obstacles encountered>

## Next Steps
<what to do next>
```

### Idea 💡
```markdown
## Description
<the idea>

## Inspiration
<where it came from>

## Potential
<what it could become>

## Maturity
<raw | developing | ready>
```

### Backlog 📋
```markdown
## Description
<what needs to be done>

## Priority
<high | medium | low>

## Effort
<small | medium | large>

## Dependencies
- <prerequisite items>
```

### Note 📄
```markdown
<raw content as provided>
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init.sh` | Initialize project |
| `scripts/write_record.py` | Write record |
| `scripts/notion_api.py` | Notion client |
| `scripts/config.py` | Configuration |
