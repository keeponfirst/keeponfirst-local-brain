---
description: Track an idea or topic from inception to completion
---

# /trace - Trace Topic Evolution

Follow an idea, decision, or task from its inception through to completion, showing the complete timeline.

## Usage

User says something like:
- `/trace automated testing`
- "Trace the history of the API refactor"
- "Show me how the authentication decision evolved"

## Workflow

1. **Parse Topic** - Extract the topic to trace

2. **Search All Records** - Find everything related
   - Use `notion_search` with topic keywords
   - Cast a wide net to catch all mentions

3. **Read and Extract Dates** - Get full content and timestamps
   - Use `notion_read_page` for each result
   - Extract creation date from page properties

4. **Sort Chronologically** - Order by date (oldest first)

5. **Present Timeline** - Show evolution with context

```
🔍 Timeline for "automated testing":

📅 2026-01-10 | 💡 Idea
└─ "Consider adding E2E tests"
   Initial thought about improving test coverage

📅 2026-01-12 | 📋 Backlog  
└─ "Research Playwright vs Cypress"
   Added to backlog for investigation

📅 2026-01-15 | ⚖️ Decision
└─ "Chose Playwright for E2E Testing"
   Decision made based on TypeScript support and speed
   
📅 2026-01-18 | 📝 Worklog
└─ "Set up first Playwright test suite"
   Implemented login flow tests

📅 2026-01-20 | 📝 Worklog
└─ "Added CI integration for tests"
   Tests now run on every PR
```

6. **Identify Gaps** - Note if evolution is incomplete

```
💡 Observation: This idea moved from Idea → Backlog → Decision → Implementation
Status: ✅ Complete
```

or

```
⚠️ Observation: This idea is still in Backlog phase
Status: 🔄 In Progress
```

## Notes

- Include record type emoji for visual clarity
- Show brief excerpt or key point from each record
- Highlight transitions between stages (Idea → Backlog → Decision → Worklog)
- If topic appears in many records (>10), ask user if they want full timeline or just key milestones
