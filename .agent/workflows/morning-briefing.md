---
description: Retrieve and summarize recent activities and tasks for a morning briefing
---

# /brief - Morning Briefing

Generates a summary of yesterday's progress and today's focus.

## Usage

User says:
- "/brief"
- "Morning briefing"
- "What did I do yesterday?"

## Workflow

1. **Search Recent Worklogs**
   - Use `notion_post_search` to find pages with "Worklog" in the title.
   - Sort by `last_edited_time` descending.
   - Limit to the top 3 results to capture recent context.

2. **Search Active Tasks**
   - Use `notion_post_search` to find pages with "Backlog" or "budo" (if using specific project codes) in the title.
   - *Alternative*: If a specific Task Database is known, use `notion_query_data_source` to find items with status="In Progress".

3. **Synthesize Briefing**
   - Read the content of the found Worklogs (using `notion_retrieve_block_children`).
   - Read the titles/status of the Backlog items.
   - Generate a summary in the following format:

```markdown
# 🌅 Morning Briefing

## 📅 Yesterday's Highlights
- [Summary of key achievements from previous worklogs]
- [Mention of any blockers identified]

## 🚀 Focus for Today
- [List of active/high-priority backlog items]
- [Suggestions based on "Next Steps" from previous worklogs]

## 💡 Context
- [Links to relevant Notion pages found]
```

4. **Present to User**
   - Output the summary directly in the chat.
