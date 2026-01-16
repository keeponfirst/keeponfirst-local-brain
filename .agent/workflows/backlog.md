---
description: Quick capture for Backlog records - future tasks and TODOs
---

# /backlog - Quick Backlog Capture

Shortcut for capturing Backlog records. Uses the main `/capture` workflow with type pre-set.

## Usage

User says something like:
- "之後要重構這段 code"
- "Backlog: 加上 dark mode 支援"
- "TODO: 研究一下 WebSocket 的 scaling"

## Workflow

1. **Capture** - Accept the backlog input
2. **Interpret** - Type is pre-set to `backlog`
3. **Draft** - Structure using Backlog template:

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

4. **Preview & Confirm** ⚠️ MUST ASK

```
我判斷這是一筆【Backlog】記錄，整理如下：

---
**{TITLE}**

{BODY}
---

✅ 確認寫入 | ✏️ 修改 | ❌ 取消
```

5. **Execute** - Only after confirmation:

// turbo
```bash
cd $PROJECT_ROOT
echo '<DRAFT_JSON>' | python scripts/write_record.py --stdin
```

6. **Report** - Show Notion URL and local path
