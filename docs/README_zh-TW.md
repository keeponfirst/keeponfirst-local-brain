# keeponfirst-local-brain

🧠 一個以本地優先的大腦擷取系統，配合 AI 輔助。

> **記錄發生在思考的當下，而非事後。**

[![English](https://img.shields.io/badge/Docs-English-blue)](../README.md)

## 專案簡介：KOF-LocalBrain

KOF-LocalBrain 是一款專為開發者打造的 **「本地優先（Local-first）」** 大腦捕捉系統，旨在解決開發過程中因切換工具而導致的脈絡遺失問題。與傳統依賴雲端的筆記軟體不同，KOF-LocalBrain 堅持將資料的所有權完全保留在用戶的本地機器上，確保極致的隱私與安全。

**核心價值：**
1. **IDE 優先的工作流**：開發者無需離開編程環境，即可隨時捕捉稍縱即逝的想法或決策。
2. **AI 輔助結構化**：系統利用現有的 IDE AI 智能，協助將原始筆記轉化為標準化的紀錄（如 Decision 決策、Worklog 日誌），並在寫入前經過用戶的明確批准（Human-in-the-loop）。

### NotebookLM MCP 整合效益：從研究到行動的閉環

透過引入 **NotebookLM MCP**，KOF-LocalBrain 將功能邊界從單純的「想法捕捉」擴展至深度的「知識整合」：

* **專屬的研究工作區**：利用 NotebookLM 強大的文檔理解能力，作為外部知識的消化中心。
* **無縫的知識調用**：藉由 Model Context Protocol (MCP)，開發者可在 IDE 內直接與這些外部知識進行對話。
* **結構化落地**：系統能將從 NotebookLM 獲取的洞察，直接轉化為 KOF-LocalBrain 的本地結構化格式（例如：根據研究文件生成一份 Decision 記錄），實現了真正的知識管理閉環。

---

## 設計理念

- **記錄發生在思考當下** — 不是事後，那時上下文早就消失了
- **AI 只輔助整理，不擅自寫入** — 永遠保持 Human-in-the-loop
- **Local-first** — 資料在你的機器上
- **Preview & Confirm** — 每次寫入都需要明確確認

---

## 🚀 新功能 (v1.2)

### 1. 混合大腦架構 (Hybrid Brain Architecture)
由 **Official Notion MCP** 驅動，實現本地檔案與 Notion 知識庫的無縫循環。
 
- **/search <query>** - 搜尋整個大腦
- **/recall <timeframe>** - 回顧活動 (例如: "Recall last week")
- **/trace <topic>** - 視覺化主題演變
- **Context-Aware Capture** - 自動建議相關的舊記錄連結。
- **Publishing** - 一鍵將本地 Markdown 發布為 Notion 頁面。

### 2. 豐富內容渲染 (Rich Content)
- **程式碼區塊 (Code Blocks)**：支援 20+ 種語言的語法高亮
- **連結預覽 (Link Previews)**：獨立網址會自動轉為視覺化書籤

### 3. NotebookLM 整合 (NotebookLM Integration)
- **程式化控制**：透過 MCP 工具直接建立筆記本、新增來源與查詢內容。
- **自動化研究**：將研究問題自動轉化為結構化的本地決策紀錄。

---

## MCP 整合 (Integrations)

本專案支援 **MCP (Model Context Protocol)** 伺服器，能大幅擴展 Agent 的能力。

| MCP Server | 狀態 | 用途 |
|------------|--------|---------|
| **Notion MCP** | ✅ Ready | 讀取/搜尋 Notion 中的歷史紀錄 |
| **NotebookLM MCP** | ✅ Ready | 使用 Google NotebookLM 作為研究工作區 |

### Notion MCP (官方版)
啟用與 Notion 大腦的完全互動。請參閱 [Notion MCP 設定指南](../docs/NOTION_MCP_SETUP.md)。
 
**核心能力:**
- `post_page`: 建立包含豐富區塊的頁面
- `post_search`: 全域搜尋
- `append_block`: 新增內容到現有頁面

### NotebookLM MCP (已就緒)
將 Google NotebookLM 作為研究草稿區，支援 AI 問答與引用。

- **獨立 Repo**: [keeponfirst/kof-notebooklm-mcp](https://github.com/keeponfirst/kof-notebooklm-mcp) (含完整文檔)
- **PyPI**: [kof-notebooklm-mcp](https://pypi.org/project/kof-notebooklm-mcp/)

**可用工具 (Tools):**
- `health_check` - 驗證連線與登入狀態
- `list_notebooks` - 列出所有筆記本
- `get_notebook` - 取得筆記本詳細資訊
- `list_sources` - 列出筆記本內的來源
- `add_source` - 新增網址或文字來源
- `create_notebook` - 程式化建立新筆記本
- `ask` - 詢問 AI 並獲得附帶引用的答案

---

## 快速開始

### 1. Clone & 設定

```bash
git clone https://github.com/keeponfirst/keeponfirst-local-brain.git
cd keeponfirst-local-brain

# 建立 Python 虛擬環境
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt

# 設定環境變數
cp .env.example .env
```

### 2. 設定後端 (Notion)

1. 前往 [Notion Integrations](https://www.notion.so/my-integrations)
2. 建立新的 integration，複製 token
3. 在 Notion 建立一個頁面，與你的 integration 分享

編輯 `.env`：
```env
NOTION_TOKEN=secret_xxxxx
NOTION_PARENT=your-page-id-here
NOTION_MODE=page
```

NOTION_MODE=page
```

### 3. 設定 Notion MCP (推薦選項)
若要啟用讀取/搜尋功能：

1. 請參考 [Notion MCP 設定指南](../docs/NOTION_MCP_SETUP.md)
2. 重新啟動您的 Agent 環境
3. 嘗試輸入 `/search Hello` 來驗證

### 中央存儲與日誌 (Centralized Storage & Logs)

本系統使用 **Central Home** 來統一管理所有筆記與執行日誌，無論你在哪裡觸發錄入。

- **筆記位置**：存於 Central Home 的 `records/` 目錄。
- **日誌位置**：存於 Central Home 的 `.agentic/logs/` 目錄。
- **設定方式**：
  - **在本 Repo 內**：透過 `.agentic/CENTRAL_LOG_MARKER` 自動偵測。
  - **在其他目錄**：首次執行時會詢問 Central Home 位置（設定存於 `config.json`）。

此功能讓你可以在任何專案目錄使用 `/kof-cap`，筆記都會統一歸檔回到這裡。

---

### 3. 驗證設定

```bash
source .venv/bin/activate
python scripts/write_record.py --dry-run --input tests/example_idea.json
```

---

## 安裝為全域 Skill

安裝一次，在**任何 workspace** 使用：

```bash
cp -r skills/keeponfirst-local-brain-skill ~/.gemini/antigravity/skills/
```

### 在新專案初始化

```bash
~/.gemini/antigravity/skills/keeponfirst-local-brain-skill/scripts/init.sh
```

### 觸發指令

| 觸發 | 動作 |
|------|------|
| `/kof-cap` | 自動分類擷取 |
| `/kof-decision` | 強制決策記錄 |
| `/kof-idea` | 強制想法記錄 |
| `/kof-backlog` | 強制待辦記錄 |
| `/kof-worklog` | 強制工作日誌 |
| `/kof-note` | 原始擷取 |

**範例：**
```
/kof-cap 今天決定用 Supabase 因為 pricing 更透明
/kof-idea 想到一個新的 feature：語音輸入擷取
```
 
---
 
## 🔄 Agentic Workflows (自動化流程)
 
我們提供了預定義的 Agent 工作流 (`.agent/workflows/`)：
 
### 1. 本地擷取 (Local Capture)
透過 `/kof-*` 指令觸發。將想法捕捉為結構化的本地檔案。
 
### 2. 研究轉行動 (Research-to-Action)
1. 使用 NotebookLM MCP 查詢文件。
2. Agent 將發現總結為本地 **Decision** 決策紀錄。
 
### 3. 晨間回顧 (Morning Briefing) [New]
*觸發語: "/brief"*
1. 搜尋 Notion 中最近的 Worklog 與 Backlog 項目。
2. 生成「晨間簡報」總結 (昨日進度 + 今日焦點)。
 
### 4. 知識發布 (Publish Knowledge)
*觸發語: "Publish [file] to Notion"*
1. Agent 讀取本地 Markdown 檔案。
2. 將其轉化為 Notion Blocks 格式。
3. 使用 `notion_post_page` 直接發布到您的 "KeepOnFirst Brain"。

---

## 記錄類型

| 類型 | Emoji | 用途 |
|------|-------|------|
| **Decision** | ⚖️ | 選擇、權衡 |
| **Worklog** | 📝 | 每日活動 |
| **Idea** | 💡 | 靈感 |
| **Backlog** | 📋 | 未來任務 |
| **Note** | 📄 | 原始擷取 |

---

## 專案結構

```
.
├── skills/
│   └── keeponfirst-local-brain-skill/
│       ├── SKILL.md
│       └── scripts/
├── scripts/
│   ├── config.py
│   ├── notion_api.py
│   ├── write_record.py
│   └── init_brain.py
├── records/
│   ├── decisions/
│   ├── worklogs/
│   ├── ideas/
│   └── backlogs/
├── .env.example
└── README.md
```

---

## 本地儲存

每筆記錄會儲存到本地：
- `{timestamp}_{type}_{slug}.md` — 人類可讀
- `{timestamp}_{type}_{slug}.json` — 機器可讀

**你的資料留在你的機器上。**

---

## 授權

MIT
