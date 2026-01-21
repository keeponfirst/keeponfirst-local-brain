---
description: Retrieve and summarize past records by time period or topic
---

# /recall - Recall Past Records

Retrieve and summarize your past records filtered by time period or topic.

## Usage

User says something like:
- `/recall last week`
- "What did I do this month?"
- "Recall all decisions about authentication"
- "Summarize my worklogs from January"

## Workflow

1. **Parse Request** - Extract time range or topic filter
   - Time: "last week", "this month", "January 2026"
   - Topic: "authentication", "API", "database"

2. **Search via MCP** - Find matching records
   - Use `notion_search` with appropriate query
   - If time-based, include date in search or filter results

3. **Read Full Content** - Use `notion_read_page` for each result
   - Get complete content, not just snippets
   - Preserve structure (Activities, Learnings, etc.)

4. **Synthesize Summary** - Generate comprehensive overview

```
📊 Summary for [timeframe/topic]:

## Overview
Found X records (Y worklogs, Z decisions, ...)

## Key Activities
- Completed API refactoring
- Fixed 5 critical bugs
- Researched Notion MCP integration

## Important Decisions
- Chose PostgreSQL over MongoDB
- Decided to use Playwright for E2E testing

## Learnings
- MCP enables bi-directional workflows
- Code blocks need custom parsing in Notion API

## Blockers
- None currently active
```

5. **Offer Details** - Ask if user wants specifics

```
Would you like me to elaborate on any of these items?
```

## Notes

- For time-based queries, use ISO date format in searches
- Group by record type for better organization
- Preserve original structure from templates (Activities, Learnings, etc.)
- If too many results (>20), ask user to narrow down
