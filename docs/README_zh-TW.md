# keeponfirst-local-brain

🧠 一個以本地優先的大腦擷取系統，配合 AI 輔助。

> **記錄發生在思考的當下，而非事後。**

[![English](https://img.shields.io/badge/Docs-English-blue)](../README.md)

## 為什麼做這個專案？

試用了 Notion AI 兩天後，我發現它只提供 **20 次免費使用** — 不是每日或每月額度，就是總共 20 次用完就沒了。

這時我想到：我每天都在用 AI-IDE（像是 Antigravity/Cursor），為什麼不做一個 **Local Brain**：

1. **在想法發生的當下擷取** — 就在我已經在用的 IDE 裡
2. **用 AI 來結構化和整理** — 利用我已經在付費的 AI
3. **透過 API 同步到 Notion** — 兩邊的好處都拿到
4. **保持 Local-first** — 不被任何單一服務綁死

這樣一來，如果 Notion 有變動或我想換後端，我的資料還是我的。

---

## 設計理念

- **記錄發生在思考當下** — 不是事後，那時上下文早就消失了
- **AI 只輔助整理，不擅自寫入** — 永遠保持 Human-in-the-loop
- **Local-first** — 資料在你的機器上
- **Preview & Confirm** — 每次寫入都需要明確確認

---

## 🚀 新功能 (v1.1)

### 1. 雙向大腦 (讀取與搜尋)
透過 **Notion MCP** 整合，Agent 現在可以讀取您過去的記錄，提供具備上下文的協助。

- `/search <query>` - 搜尋整個大腦中的記錄
- `/recall <timeframe>` - 回顧並總結過去的活動 (例如: "Recall last week")
- `/trace <topic>` - 視覺化主題的演變時間軸 (Idea → Decision → Worklog)
- **Context-Aware Capture** - 寫入新記錄時，自動建議相關的舊記錄連結。

### 2. 豐富內容渲染 (Rich Content)
- **程式碼區塊 (Code Blocks)**：支援 20+ 種語言的語法高亮
- **連結預覽 (Link Previews)**：獨立網址會自動轉為視覺化書籤

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
/kof-worklog 完成了 API 整合
```

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
