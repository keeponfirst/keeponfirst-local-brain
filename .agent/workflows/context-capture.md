---
description: Enhance capture workflows with context from past records
---

# Context-Aware Capture

Automatically search for and reference related past records when creating new ones.

## Trigger

This enhances existing capture workflows:
- `/capture`
- `/worklog`
- `/decision`
- `/idea`
- `/backlog`

## Workflow

### Phase 1: Context Discovery (Before Drafting)

1. **Extract Keywords** - From user's capture request
   - Title keywords
   - Tags mentioned
   - Topic indicators

2. **Search for Related Records** - Use MCP (`notion_post_search`)
   - Search for records with similar keywords
   - Filter by same record type (`object=page`)
   - Limit to recent records (last 30 days by default)

3. **Present Context** - If relevant records found

```
💡 Context Check:

I found related records:
- 📝 Worklog: "API Refactoring Progress" (3 days ago)
  You mentioned completing the /users endpoint

Would you like me to reference this in your new worklog?
```

4. **User Decision**
   - ✅ Yes → Include reference in draft
   - ❌ No → Proceed without context
   - 📖 Read → Show full content first

### Phase 2: Enhanced Drafting (If Context Accepted)

5. **Draft with Context** - Include reference in body

For Worklog:
```markdown
## Activities
- Continued API refactoring (following up on [previous worklog](url))
- Completed /posts endpoint
- ...
```

For Decision:
```markdown
## Context
This builds on the previous idea captured in [Idea: E2E Testing](url)
...
```

6. **Continue Normal Flow** - Preview & Confirm as usual

## Configuration

**Search Scope**:
- Default: Last 30 days
- Can be adjusted based on user preference

**Relevance Threshold**:
- Only suggest if 2+ keyword matches
- Prioritize same record type

**Auto-Reference Format**:
- Include clickable Notion link
- Brief description of related record

## Notes

- This is **opt-in** during each capture
- Does not slow down workflow (search happens in parallel)
- User can always decline context
- Gracefully degrades if MCP not available (skips context check)
