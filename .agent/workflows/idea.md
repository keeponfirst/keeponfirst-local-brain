---
description: Quick capture for Idea records - unformed thoughts and inspirations
---

# /idea - Quick Idea Capture

Shortcut for capturing Idea records. Uses the main `/capture` workflow with type pre-set.

## Usage

User says something like:
- "想到一個點子：如果能自動..."
- "Idea: 用 LLM 來產生測試案例"
- "突然想到可以把這個流程自動化"

## Workflow

1. **Capture** - Accept the idea input
2. **Interpret** - Type is pre-set to `idea`
3. **Draft** - Structure using Idea template:

```markdown
## Description
<the idea>

## Inspiration
<where it came from>

## Potential
<what it could become>

## Maturity
<raw | developing | ready>
```

4. **Preview & Confirm** ⚠️ MUST ASK

```
我判斷這是一筆【Idea】記錄，整理如下：

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
