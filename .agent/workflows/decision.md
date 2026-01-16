---
description: Quick capture for Decision records - important choices and trade-offs
---

# /decision - Quick Decision Capture

Shortcut for capturing Decision records. Uses the main `/capture` workflow with type pre-set.

## Usage

User says something like:
- "決定用 X 而不是 Y"
- "Decision: 選擇了 Supabase"
- "我們決定延後這個 feature"

## Workflow

1. **Capture** - Accept the decision input
2. **Interpret** - Type is pre-set to `decision`
3. **Draft** - Structure using Decision template:

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

4. **Preview & Confirm** ⚠️ MUST ASK

```
我判斷這是一筆【Decision】記錄，整理如下：

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
