---
description: Search across all Notion records using MCP
---

# /search - Search Your Brain

Search across all records in your Notion workspace using natural language queries.

## Usage

User says something like:
- `/search api refactoring`
- "Search my brain for decisions about databases"
- "Find all worklogs from last week"

## Workflow

1. **Parse Query** - Extract search terms from user input

2. **Search via MCP** - Use Notion MCP to search workspace
   - Use the `notion_search` MCP tool
   - Query across all pages in the workspace

3. **Present Results** - Format and display findings

```
Found X results for "query":

1. [⚖️ Decision: Title](notion_url) - 2026-01-15
   Snippet: ...relevant excerpt...

2. [📝 Worklog: Title](notion_url) - 2026-01-18
   Snippet: ...relevant excerpt...

...
```

4. **Offer Deep Dive** - Ask if user wants to read full content

```
Would you like me to read the full content of any of these pages?
```

5. **Read if Requested** - Use `notion_read_page` to get full content

## Notes

- If MCP is not configured, inform user to set it up via `docs/NOTION_MCP_SETUP.md`
- Results are sorted by relevance (Notion's default)
- Include page type emoji (⚖️📝💡📋) for quick visual scanning
