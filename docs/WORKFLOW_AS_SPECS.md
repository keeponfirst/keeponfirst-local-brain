# KOF-LocalBrain 工作流規格（OpenSpec 格式）

本文件將 keeponfirst-local-brain 現有的捕捉工作流與記錄類型以 OpenSpec 規格格式記錄，供團隊參考與未來規格化使用。

---

## 1. 捕捉工作流（6 步驟）

### 流程規格

```
觸發 → 分類 → 結構化 → 預覽 → 確認 → 寫入
```

| 步驟 | 名稱 | 說明 | 角色 |
|------|------|------|------|
| 1 | **觸發** | 開發中產生想法、決策、問題 | 使用者 |
| 2 | **分類** | AI 自動判斷記錄類型（decision/worklog/idea/backlog/note） | AI |
| 3 | **結構化** | AI 將原始想法轉換為標準化 JSON/MD 格式 | AI |
| 4 | **預覽** | 使用者檢視 AI 生成的結構化內容 | 使用者 |
| 5 | **確認** | 使用者明確批准寫入（human-in-the-loop） | 使用者 |
| 6 | **寫入** | 寫入 Central Home 檔案系統 + 可選 Notion 同步 | 系統 |

### Acceptance Criteria

- **AC-1**：任何步驟失敗不得遺失使用者原始輸入
- **AC-2**：步驟 5（確認）為必要步驟，AI 永不自動寫入
- **AC-3**：步驟 6 寫入失敗時，記錄保存在本地（`notion_sync_status: PENDING`）
- **AC-4**：完整流程應在 10 秒內完成（不含使用者等待時間）

### Edge Cases

- 分類不確定（信心 < 0.7）→ 預設為 `note`，提示使用者確認
- Notion 不可用 → 本地寫入成功，標記待同步
- 使用者中途取消 → 不寫入，不留殘留資料

---

## 2. 記錄類型規格（5 種）

### 2.1 Decision（決策）

**目錄**：`records/decisions/`

**結構**：
```json
{
  "record_type": "decision",
  "title": "string",
  "created_at": "ISO-8601",
  "source_text": "原始輸入",
  "final_body": "結構化內容（含 context, options, rationale, trade-offs）",
  "tags": ["string"],
  "date": "YYYY-MM-DD"
}
```

**觸發指令**：`/kof-decision`

**必含欄位**：context（背景）、options（選項）、rationale（理由）、trade-offs（取捨）

### 2.2 Worklog（工作日誌）

**目錄**：`records/worklogs/`

**結構**：
```json
{
  "record_type": "worklog",
  "title": "string",
  "created_at": "ISO-8601",
  "source_text": "原始輸入",
  "final_body": "結構化內容（含 activities, learnings, blockers）",
  "tags": ["string"],
  "date": "YYYY-MM-DD"
}
```

**觸發指令**：`/kof-worklog`

**必含欄位**：activities（今日活動）、learnings（學到的事）、blockers（阻礙）

### 2.3 Idea（靈感）

**目錄**：`records/ideas/`

**結構**：
```json
{
  "record_type": "idea",
  "title": "string",
  "created_at": "ISO-8601",
  "source_text": "原始輸入",
  "final_body": "結構化內容（含 description, inspiration, potential）",
  "tags": ["string"],
  "date": "YYYY-MM-DD"
}
```

**觸發指令**：`/kof-idea`

**必含欄位**：description（描述）、inspiration（啟發來源）、potential（潛力評估）

### 2.4 Backlog（待辦）

**目錄**：`records/backlogs/`

**結構**：
```json
{
  "record_type": "backlog",
  "title": "string",
  "created_at": "ISO-8601",
  "source_text": "原始輸入",
  "final_body": "結構化內容（含 priority, effort, acceptance criteria）",
  "tags": ["string"],
  "date": "YYYY-MM-DD"
}
```

**觸發指令**：`/kof-backlog`

**必含欄位**：priority（優先級）、effort（工時預估）、acceptance criteria（驗收條件）

### 2.5 Note（筆記）

**目錄**：`records/other/`

**結構**：
```json
{
  "record_type": "note",
  "title": "string",
  "created_at": "ISO-8601",
  "source_text": "原始輸入",
  "final_body": "原始內容（最小結構化）",
  "tags": ["string"],
  "date": "YYYY-MM-DD"
}
```

**觸發指令**：`/kof-note`

**說明**：最輕量的記錄類型，用於無法歸類的想法或快速筆記

---

## 3. 自動分類規格

**觸發指令**：`/kof-cap`（自動分類）

### 分類邏輯

| 關鍵詞模式 | 分類結果 |
|-----------|---------|
| 「決定」「選擇」「比較」「vs」 | decision |
| 「今天」「完成」「進度」「遇到」 | worklog |
| 「如果」「可以」「想到」「靈感」 | idea |
| 「需要」「待辦」「任務」「TODO」 | backlog |
| 其他 | note |

### Acceptance Criteria

- **AC-1**：分類結果在預覽步驟展示給使用者，可手動修改
- **AC-2**：分類不改變原始輸入內容
- **AC-3**：新 session 中 `/kof-cap` 可正常使用（不依賴前次 session 狀態）

---

## 4. 儲存層規格

### Central Home 結構

```
<central_home>/
├── records/
│   ├── decisions/*.json + *.md
│   ├── worklogs/*.json + *.md
│   ├── ideas/*.json + *.md
│   ├── backlogs/*.json + *.md
│   └── other/*.json + *.md
├── .agentic/
│   ├── logs/*.json
│   └── kofnote_search.sqlite
```

### 寫入規則

- 每筆記錄同時產生 `.json`（結構化資料）和 `.md`（人類可讀）
- 檔名格式：`YYYY-MM-DD_<slug>.json`
- 寫入為原子操作（先寫暫存檔，再 rename）
- SQLite FTS5 索引在寫入成功後非同步更新

### Notion 同步規格

| 欄位 | 用途 |
|------|------|
| `notion_page_id` | Notion 頁面 ID |
| `notion_url` | Notion 頁面 URL |
| `notion_sync_status` | `SYNCED` / `PENDING` / `FAILED` / `NOT_SYNCED` |
| `notion_error` | 最後一次同步錯誤訊息 |
| `notion_last_synced_at` | 最後成功同步時間 |
| `notion_last_edited_time` | Notion 端最後編輯時間 |
| `notion_last_synced_hash` | 同步內容 hash（偵測變更） |

---

## 5. 與 OpenSpec 的對應

| Local-Brain 概念 | OpenSpec 對應 |
|------------------|--------------|
| 捕捉工作流 | change lifecycle（new → apply → verify → archive） |
| 記錄類型 | artifact types（proposal, specs, design, tasks） |
| 自動分類 | config.yaml rules（per-artifact 約束） |
| Central Home | openspec/ 目錄結構 |
| Notion 同步 | 無直接對應（OpenSpec 為本地工具） |

---

## 6. 可操作指令摘要

| 指令 | 用途 | 記錄類型 |
|------|------|---------|
| `/kof-cap` | 自動分類捕捉 | 自動判斷 |
| `/kof-decision` | 記錄決策 | decision |
| `/kof-worklog` | 記錄工作日誌 | worklog |
| `/kof-idea` | 記錄靈感 | idea |
| `/kof-backlog` | 新增待辦 | backlog |
| `/kof-note` | 快速筆記 | note |
| `/kof-health` | 系統健康檢查 | — |
