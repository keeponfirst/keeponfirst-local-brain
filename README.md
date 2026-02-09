# keeponfirst-local-brain

🧠 A local-first brain capture system with AI assistance.

> **Capture happens at the moment of thought, not after.**

[![中文文檔](https://img.shields.io/badge/文檔-繁體中文-blue)](./docs/README_zh-TW.md)

## ☕ Support this project

If this project helps you, you can support development here:

👉 https://buymeacoffee.com/keeponfirst

---

## Project Introduction: KOF-LocalBrain

KOF-LocalBrain is a **Local-first** brain capture system designed for developers, solving the problem of context loss during development. Unlike cloud-dependent note-taking tools, it keeps data ownership completely local, ensuring maximum privacy and security.

**Core Value:**
1. **IDE-First Workflow**: Capture fleeting thoughts without leaving your coding environment.
2. **AI-Assisted Structuring**: Uses existing IDE AI to transform raw notes into standardized records (decisions, worklogs, backlogs) with explicit human confirmation.

### NotebookLM MCP: Research-to-Action

With **NotebookLM MCP**, KOF-LocalBrain expands from "thought capture" to deep "knowledge integration":

* **Dedicated Research Workspace**: Use NotebookLM to digest external knowledge without cluttering your local context.
* **Seamless Context Retrieval**: Talk to your external knowledge base directly from your IDE via MCP.
* **Structured Action**: Transform insights from NotebookLM into local structured records (e.g., generate a Decision record from research docs), closing the loop between research and development.

---

## Philosophy

- **Capture at the moment of thought** — Not after, when context is lost
- **AI assists, never writes without permission** — Human-in-the-loop always
- **Local-first** — Your data stays on your machine
- **Preview & Confirm** — Every write requires explicit approval

---

## 🚀 New Features (v1.3)

### 1. Resilient Local-First Write (NEW)
- **Notion Fallback**: When Notion API fails (DNS, auth, network), records are still saved locally with `notion_sync_status: PENDING`.
- **Zero Data Loss**: Local capture never fails due to remote service issues.

### 2. Health Check Command (NEW)
- **`/kof-health`**: One-command diagnostic for all dependencies (Notion API, local storage, MCP config).
- **Actionable Hints**: Clear error messages with resolution steps.

### 3. Hybrid Brain Architecture (Read, Search, Write)
Powered by **Official Notion MCP**, your agent creates a seamless loop between local files and Notion knowledge base.

- **/search <query>** - Search across your entire brain
- **/recall <timeframe>** - Summarize past activities (e.g., "Recall last week")
- **/trace <topic>** - Visualize the timeline of an idea (Idea → Decision → Worklog)
- **Context-Aware Capture** - Automatically suggests related past records.
- **Publishing** - One-command publishing of local markdowns to Notion pages.

### 4. Rich Content Rendering
- **Code Blocks**: Syntax highlighting for 20+ languages
- **Link Previews**: Standalone URLs become visual bookmarks

### 5. NotebookLM Integration
- **Programmatic Control**: Create notebooks, add sources, and query content via MCP tools.
- **Auto-Research**: Turn research questions into structured local decisions.

---

## MCP Integrations

This project supports MCP (Model Context Protocol) servers for extended capabilities.

| MCP Server | Status | Purpose |
|------------|--------|---------|
| **Notion MCP** | ✅ Ready | Read/search past records from Notion |
| **NotebookLM MCP** | ✅ Ready | Use Google NotebookLM as research workspace |

### Notion MCP (Official)
Enables full interaction with your Notion brain. See [Notion MCP Setup](docs/NOTION_MCP_SETUP.md).

**Capabilities:**
- `post_page`: Create rich pages with blocks
- `post_search`: Global search
- `append_block`: Add content to existing pages

### NotebookLM MCP (Ready)
Use Google NotebookLM as a research scratchpad with AI-powered Q&A.

- **Standalone Repo**: [keeponfirst/kof-notebooklm-mcp](https://github.com/keeponfirst/kof-notebooklm-mcp)
- **PyPI**: [kof-notebooklm-mcp](https://pypi.org/project/kof-notebooklm-mcp/)
  - [README.md](https://github.com/keeponfirst/kof-notebooklm-mcp/blob/main/README.md) - 安裝與使用指南

**Available tools:**
- `health_check` - Verify connection and authentication
- `list_notebooks` - List all notebooks
- `get_notebook` - Get notebook details
- `list_sources` - List sources in a notebook
- `add_source` - Add URL or text sources
- `create_notebook` - Create new notebooks programmatically
- `ask` - Query notebook with AI and get cited answers

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/keeponfirst/keeponfirst-local-brain.git
cd keeponfirst-local-brain

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt

# Configure environment
cp .env.example .env
```

### 2. Configure Backend (Notion)

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration, copy the token
3. Create a page in Notion, share it with your integration

Edit `.env`:
```env
NOTION_TOKEN=secret_xxxxx
NOTION_PARENT=your-page-id-here
NOTION_MODE=page
```

NOTION_MODE=page
```

### 3. Configure Notion MCP (Optional but Recommended)
To enable read/search capabilities:

1. Follow the [Notion MCP Setup Guide](docs/NOTION_MCP_SETUP.md)
2. Restart your agent environment
3. Try `/search Hello` to verify

### 4. Configure NotebookLM MCP (Research)
To enable NotebookLM research tools, add to your `mcp_config.json`:

```json
"kof-notebooklm-mcp": {
  "command": "uvx",
  "args": ["kof-notebooklm-mcp"]
}
```

### Centralized Storage & Logs

This system uses a **Central Home** for all your records and logs, regardless of where you capture them from.

- **Storage Location**: Records are saved to `records/` inside your Central Home.
- **Log Location**: Execution logs are saved to `.agentic/logs/` inside your Central Home.
- **Configuration**:
  - **Inside this repo**: Automatically detected via `.agentic/CENTRAL_LOG_MARKER`.
  - **Outside this repo**: You will be asked to specify the Central Home location once (stored in `config.json`).

This allows you to use `/kof-cap` in any project directory, and notes will be consolidated back here.

---

## Verify Setup

```bash
# Quick health check
python scripts/health_check.py

# Or dry-run a record
source .venv/bin/activate
python scripts/write_record.py --dry-run --input tests/example_idea.json
```

---

## Install as Global Skill

Install once, use from **any workspace**:

```bash
cp -r skills/keeponfirst-local-brain-skill ~/.gemini/antigravity/skills/
```

### Initialize in a New Project

```bash
~/.gemini/antigravity/skills/keeponfirst-local-brain-skill/scripts/init.sh
```

### Triggers

| Trigger | Action |
|---------|--------|
| `/kof-cap` | Capture with auto-classification |
| `/kof-decision` | Force decision record |
| `/kof-idea` | Force idea record |
| `/kof-backlog` | Force backlog record |
| `/kof-worklog` | Force worklog record |
| `/kof-note` | Raw capture (fallback) |
| `/kof-health` | Run health check diagnostics |

**Example:**
```
/kof-cap Decided to use Supabase because pricing is more transparent
/kof-idea New feature: voice input for capture
```

---

## 🔄 Agentic Workflows

We provide pre-defined workflows for the Agent (`.agent/workflows/`):

### 1. Local Capture (Standard)
Triggered by `/kof-*` commands. Captures thoughts into structured local files.

### 2. Research-to-Action (NotebookLM)
1. Use NotebookLM MCP to query documents.
2. Agent summarizes findings into a local **Decision** record.

### 3. Morning Briefing (New)
*Trigger: "/brief"*
1. Search Notion for recent Worklogs and Backlog items.
2. Genereate a "Morning Briefing" summary (Yesterday's progress + Today's focus).

### 4. Publish Knowledge
*Trigger: "Publish [file] to Notion"*
1. Agent reads local Markdown file.
2. Formats it into Notion Blocks.
3. Uses `notion_post_page` to publish it to your "KeepOnFirst Brain".

---

## Record Types

| Type | Emoji | Use For |
|------|-------|---------|
| **Decision** | ⚖️ | Choices, trade-offs |
| **Worklog** | 📝 | Daily activities |
| **Idea** | 💡 | Inspirations |
| **Backlog** | 📋 | Future tasks |
| **Note** | 📄 | Raw capture |

---

## Project Structure

```
.
├── skills/
│   └── keeponfirst-local-brain-skill/
│       ├── SKILL.md
│       └── scripts/
├── scripts/
│   ├── config.py
│   ├── notion_api.py
│   ├── write_record.py
│   ├── health_check.py        # NEW: Diagnostic tool
│   └── init_brain.py
├── packages/
│   └── kof-notebooklm-mcp/
├── docs/
│   ├── NOTION_MCP_SETUP.md
│   └── kof-notebooklm-mcp/
├── records/
│   ├── decisions/
│   ├── worklogs/
│   ├── ideas/
│   └── backlogs/
├── .env.example
└── README.md
```

---

## Troubleshooting

### Notion Write Failures

| Symptom | Cause | Solution |
|---------|-------|----------|
| DNS resolution failed | Network issue | `ping api.notion.com` |
| 401 Unauthorized | Invalid token | Regenerate at [notion.so/my-integrations](https://notion.so/my-integrations) |
| 404 Not Found | No permission | Share page with Integration via "..." → "Connections" |

> **Note**: When Notion fails, records are saved locally with `notion_sync_status: PENDING`.

### MCP Configuration

> ⚠️ MCP config changes require **IDE restart** to take effect.

Run `/kof-health` to diagnose MCP setup issues.

---

## Local Storage

Every record saves locally:
- `{timestamp}_{type}_{slug}.md` — Human-readable
- `{timestamp}_{type}_{slug}.json` — Machine-readable

**Your data stays on your machine.**

---

## License

MIT
