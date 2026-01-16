---
description: Unified capture workflow for Keeponfirst_LocalNotion - handles Decision, Worklog, Idea, and Backlog records
---

# /capture - Unified Record Capture Workflow

This workflow captures any type of record (Decision, Worklog, Idea, Backlog) using a strict 6-step pipeline.

## Prerequisites
- `.env` file configured with `NOTION_TOKEN`, `NOTION_PARENT`, and `NOTION_MODE`
- Python environment with dependencies installed (`pip install -r scripts/requirements.txt`)

---

## Step 1: Capture

User provides natural language input. **DO NOT write to Notion yet.**

Accept the input as-is. It may be:
- A clear statement with explicit type (e.g., "Decision: 我決定用 Supabase 而非 Firebase")
- An ambiguous thought without type specified
- A list of items
- A brain dump

---

## Step 2: Interpret

Analyze the input and determine:

1. **Is this worth recording?** (If clearly not, ask user to confirm skip)

2. **Record Type** - Infer from content:
   - **Decision**: Contains choices, trade-offs, "decided to", "選擇了", reasoning
   - **Worklog**: Contains activities, "今天做了", progress, learnings, blockers
   - **Idea**: Contains "想到", "如果...", possibilities, inspirations, unformed thoughts
   - **Backlog**: Contains "之後要", "TODO", future tasks, dependencies

3. **Structure the content** using Gemini CLI if needed:
   - Call Gemini for: structuring, rewriting, formatting
   - If image prompts needed, save to `assets/prompts/`
   - **Gemini MUST NOT call Notion API directly**

---

## Step 3: Draft

Generate a structured Draft in this format:

```json
{
  "type": "<decision|worklog|idea|backlog>",
  "title": "<concise title>",
  "body": "<structured markdown content>",
  "source_text": "<original user input>",
  "date": "<YYYY-MM-DD or null>",
  "tags": ["tag1", "tag2"]
}
```

### Body Templates by Type

**Decision:**
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

**Worklog:**
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

**Idea:**
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

**Backlog:**
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

---

## Step 4: Preview & Confirm ⚠️ CRITICAL GATE

**YOU MUST ALWAYS ASK FOR CONFIRMATION. NO EXCEPTIONS.**

Present the draft to user:

```
我判斷這是一筆【{TYPE}】記錄，整理如下：

---
**{TITLE}**

{BODY_PREVIEW}
---

Tags: {TAGS}
Date: {DATE}

請選擇：
✅ 確認寫入 Notion
✏️ 修改（請告訴我要改什麼）
❌ 取消（不寫入、不保留）
```

### User Response Handling:

- **✅ 確認** → Proceed to Step 5
- **✏️ 修改** → Return to Step 3 with modification request, generate new Draft
- **❌ 取消** → Stop workflow, do not write anything

**IF USER HAS NOT EXPLICITLY CONFIRMED, DO NOT PROCEED TO STEP 5.**

---

## Step 5: Execute

Only after explicit confirmation:

// turbo
```bash
cd $PROJECT_ROOT
echo '<DRAFT_JSON>' | python scripts/write_record.py --stdin
```

Replace `<DRAFT_JSON>` with the actual JSON draft.

Capture the output which includes:
- `notion_page_id`
- `notion_url`
- `local_md` path
- `local_json` path

---

## Step 6: Local Sync (Automatic)

The `write_record.py` script automatically:
1. Writes to Notion
2. Saves `.md` file to `records/{type}s/`
3. Saves `.json` file to `records/{type}s/`

Filename format: `{YYYYMMDD_HHMMSS}_{type}_{slug}.{ext}`

---

## Completion

Report to user:

```
✅ 記錄完成！

📝 Notion: {notion_url}
💾 本地: {local_md_path}

Type: {TYPE}
Title: {TITLE}
```

---

## Error Handling

- **Notion API error**: Show error, ask if user wants to retry or save locally only
- **Missing .env**: Prompt user to create `.env` from `.env.example`
- **Invalid type**: Default to "idea" and confirm with user
