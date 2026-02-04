---
name: keeponfirst-local-brain-skill
description: "Local-first brain capture system. Triggers: /kof-cap, /kof-decision, /kof-idea, /kof-backlog, /kof-worklog, /kof-note"
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
| `/kof-health` | Run health check diagnostics |

### MCP-Powered Features (Read/Search)

> These features require Notion MCP Server to be configured. See [docs/NOTION_MCP_SETUP.md](file:///Users/pershing/Documents/henry/Fun/WorkSpace/keeponfirst-local-brain/docs/NOTION_MCP_SETUP.md).
> For NotebookLM features, add this to your MCP config:
> ```json
> "kof-notebooklm-mcp": {
>   "command": "uvx",
>   "args": ["kof-notebooklm-mcp"]
> }
> ```

| Trigger | Action |
|---------|--------|
| `/search <query>` | Search all records in Notion |
| `/recall <timeframe>` | Summarize past records by time/topic |
| `/brief` | Morning briefing (Yesterday's Log + Today's Focus) |
| `/trace <topic>` | Track idea evolution timeline |
| Context-aware capture | Auto-reference related records when capturing |
| `Publish [file] to Notion` | Create Notion page from local file (Official MCP) |
| `/research` | Research topic using NotebookLM |

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

### Step 2.5: Context Search (Optional)
If Notion MCP is available, search for related context *before* drafting.
1. Extract keywords from user input.
2. Use `notion_post_search` to find related records.
3. If matches found, display them as "💡 Related Context" in the Preview step.

### Step 3: Draft
Generate structured content with appropriate template.

#### Record Generation Rules
1. **Language**: Always check `PRIMARY_LANGUAGE` in the environment. If set to `zh-TW`, generate all titles and bodies in Traditional Chinese. Default to the user's input language if not specified.
2. **Preview & Confirm**: Always show a preview of the structured record before writing.

### Step 4: Preview & Confirm ⚠️ CRITICAL

**ALWAYS show preview before writing:**

```
我判斷這是一筆【TYPE】記錄，整理如下：

---
**TITLE**

BODY
---

💡 Context: [Link to related Page A] | [Link to related Page B]
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

---

## NotebookLM Research Workflow

Integrates NotebookLM into the PLAN → ASSETS → CODE workflow.

### 1. Research Scratchpad (PLAN Phase)

**Workflow**: Deep Research for Technical Decision
1. Create notebook for research topic
2. Add sources (Docs, Blog posts, GitHub repos)
3. Ask synthesizing questions (Tradeoffs, Summaries)
4. Capture decision in KOF (`/kof-decision` with citations)

**Prompt Pattern**:
```
Use kof-notebooklm-mcp to research [TOPIC]:
1. checks - verify connection/notebooks
2. add_source - add URLs
3. ask - "What are the main approaches to...?"
4. Return findings formatted for /kof-decision
```

### 2. Citations Provider (ASSETS Phase)

**Workflow**: Generate Documentation with Citations
1. Query existing research notebook
2. Ask specific questions
3. Format as markdown with citation links

**Prompt Pattern**:
```
Query notebook "[NOTEBOOK_NAME]" for documentation:
1. ask - "[QUESTION] - cite your sources"
2. Format response with [source_title](source_url) links
```

### 3. Technical Reference (CODE Phase)

**Workflow**: Implementation Guidance
1. Add technical docs to notebook
2. Ask implementation questions ("Show example code", "Edge cases")
3. Incorporate guidance into code

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
| `scripts/health_check.py` | Diagnostic check |
| `scripts/add_research_to_notebooklm.py` | Add research note to NotebookLM |

---

## Troubleshooting

### Notion 寫入失敗

| 症狀 | 可能原因 | 解決方式 |
|-----|---------|----------|
| DNS 解析失敗 | 網路問題 | `ping api.notion.com` 確認連線 |
| 401 Unauthorized | Token 無效 | 到 [notion.so/my-integrations](https://notion.so/my-integrations) 重新生成 |
| 404 Not Found | 頁面不存在或無權限 | 在 Notion 頁面「...」→「Connections」加入 Integration |

> [!TIP]
> Notion 寫入失敗時，系統會自動寫入本地並標記 `notion_sync_status: PENDING`，不會遺失資料。

### MCP 設定未生效

> [!WARNING]
> MCP 設定變更後需**重啟 IDE**才會載入新設定。

- 檢查 `.mcp.json` 或 `mcp_config.json` JSON 語法
- 確認 `notion-mcp-server` 路徑正確
- 執行 `/kof-health` 檢查 MCP 狀態

### 快速診斷

```bash
# 執行健康檢查
SKILL_ROOT="$HOME/.gemini/antigravity/skills/keeponfirst-local-brain-skill"
$SKILL_ROOT/.venv/bin/python $SKILL_ROOT/scripts/health_check.py
```
