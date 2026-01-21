# keeponfirst-local-brain

🧠 A local-first brain capture system with AI assistance.

> **Capture happens at the moment of thought, not after.**

[![中文文檔](https://img.shields.io/badge/文檔-繁體中文-blue)](./docs/README_zh-TW.md)

## Why This Project?

After trying Notion AI for 2 days, I discovered it only offers **20 free uses total** — not a daily or monthly quota, just 20 uses and you're done.

That's when it hit me: I'm already using AI-IDE (like Antigravity/Cursor) every single day. Why not build a **local brain** that:

1. **Captures thoughts at the moment they happen** — right in the IDE where I'm already working
2. **Uses AI to structure and organize** — leveraging the AI I'm already paying for
3. **Syncs to Notion via API** — getting the best of both worlds
4. **Stays local-first** — not locked into any single service

This way, if Notion changes or I want to switch backends, my data is still mine.

---

## Philosophy

- **Capture at the moment of thought** — Not after, when context is lost
- **AI assists, never writes without permission** — Human-in-the-loop always
- **Local-first** — Your data stays on your machine
- **Preview & Confirm** — Every write requires explicit approval

---

## 🚀 New Features (v1.1)

### 1. Bi-Directional Brain (Read & Search)
Powered by **Notion MCP**, your agent can now read your past records to provide context-aware assistance.

- `/search <query>` - Search across your entire brain
- `/recall <timeframe>` - Summarize past activities (e.g., "Recall last week")
- `/trace <topic>` - Visualize the timeline of an idea (Idea → Decision → Worklog)
- **Context-Aware Capture** - Automatically suggests related past records when you're writing.

### 2. Rich Content Rendering
- **Code Blocks**: Syntax highlighting for 20+ languages
- **Link Previews**: Standalone URLs become visual bookmarks

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

### Centralized Storage & Logs

This system uses a **Central Home** for all your records and logs, regardless of where you capture them from.

- **Storage Location**: Records are saved to `records/` inside your Central Home.
- **Log Location**: Execution logs are saved to `.agentic/logs/` inside your Central Home.
- **Configuration**:
  - **Inside this repo**: Automatically detected via `.agentic/CENTRAL_LOG_MARKER`.
  - **Outside this repo**: You will be asked to specify the Central Home location once (stored in `config.json`).

This allows you to use `/kof-cap` in any project directory, and notes will be consolidated back here.

---

## Record Typesrify Setup

```bash
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

**Example:**
```
/kof-cap Decided to use Supabase because pricing is more transparent
/kof-idea New feature: voice input for capture
/kof-worklog Completed API integration
```

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
│   └── init_brain.py
├── records/
│   ├── decisions/
│   ├── worklogs/
│   ├── ideas/
│   └── backlogs/
├── .env.example
└── README.md
```

---

## Local Storage

Every record saves locally:
- `{timestamp}_{type}_{slug}.md` — Human-readable
- `{timestamp}_{type}_{slug}.json` — Machine-readable

**Your data stays on your machine.**

---

## License

MIT
