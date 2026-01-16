---
description: Quick capture for Worklog records - daily activities and progress
---

# /worklog - Quick Worklog Capture

Shortcut for capturing Worklog records. Uses the main `/capture` workflow with type pre-set.

## Usage

User says something like:
- "今天做了 API 重構"
- "Worklog: 修完了那個 bug，學到要先看 log"
- "早上開會討論了架構，下午寫測試"

## Workflow

1. **Capture** - Accept the worklog input
2. **Interpret** - Type is pre-set to `worklog`
3. **Draft** - Structure using Worklog template:

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

4. **Preview & Confirm** ⚠️ MUST ASK

```
我判斷這是一筆【Worklog】記錄，整理如下：

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
