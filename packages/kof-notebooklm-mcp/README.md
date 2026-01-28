# kof-notebooklm-mcp

> MCP 伺服器：整合 Google NotebookLM 到 KOF 工作流程

**狀態**: ✅ MVP 完成

---

## 概述

此 MCP 伺服器讓 KOF 工作流程能夠程式化存取 Google NotebookLM，實現：

- 列出和查詢筆記本
- 新增來源（URL 和文字內容）
- 提問並取得 AI 生成的回答與引用

## 文件

- **[PLAN.md](../../docs/kof-notebooklm-mcp/PLAN.md)** - 實作計畫、架構、里程碑
- **[TOOLS.md](../../docs/kof-notebooklm-mcp/TOOLS.md)** - MCP 工具規格
- **[DECISIONS.md](../../docs/kof-notebooklm-mcp/DECISIONS.md)** - 架構決策記錄
- **[TESTING.md](./TESTING.md)** - 測試計畫與清單

## 系統需求

- Python 3.10+
- 擁有 NotebookLM 存取權限的 Google 帳號
- Chromium 瀏覽器（由 Playwright 自動安裝）

## 安裝

```bash
# 從專案根目錄
cd packages/kof-notebooklm-mcp

# 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安裝開發模式
pip install -e ".[dev]"

# 安裝 Playwright 瀏覽器
playwright install chromium
```

## 初始設定

首次使用前，必須完成 Google 帳號認證：

```bash
# 開啟瀏覽器進行手動登入
kof-notebooklm-init
```

執行步驟：
1. 瀏覽器視窗將會開啟
2. 登入您的 Google 帳號
3. 確認可以看到 NotebookLM 筆記本列表
4. 關閉瀏覽器視窗

工作階段將儲存至 `~/.kof-notebooklm/profile/`，可跨重啟使用。

### 驗證設定

```bash
# 檢查連線狀態
kof-notebooklm-health
```

成功輸出範例：
```json
{
  "status": "healthy",
  "authenticated": true,
  "latency_ms": 1523,
  "browser_ok": true,
  "error": null
}
```

## MCP 客戶端設定

### Claude Desktop

新增至 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "kof-notebooklm": {
      "command": "kof-notebooklm-mcp",
      "env": {
        "NOTEBOOKLM_HEADLESS": "true"
      }
    }
  }
}
```

### 使用 uvx（推薦）

```json
{
  "mcpServers": {
    "kof-notebooklm": {
      "command": "uvx",
      "args": ["--from", "/path/to/packages/kof-notebooklm-mcp", "kof-notebooklm-mcp"],
      "env": {
        "NOTEBOOKLM_HEADLESS": "true"
      }
    }
  }
}
```

## 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `NOTEBOOKLM_PROFILE_PATH` | `~/.kof-notebooklm/profile` | 瀏覽器設定檔位置 |
| `NOTEBOOKLM_HEADLESS` | `true` | 是否使用無頭模式 |
| `NOTEBOOKLM_TIMEOUT` | `30000` | 預設逾時（毫秒） |
| `NOTEBOOKLM_SLOW_MO` | `0` | 操作延遲（毫秒，用於除錯） |
| `NOTEBOOKLM_RATE_LIMIT` | `10` | 每分鐘最大請求數 |

## 可用工具

| 工具 | 說明 | 狀態 |
|------|------|------|
| `health_check` | 驗證連線和認證狀態 | ✅ |
| `list_notebooks` | 列出所有筆記本 | ✅ |
| `get_notebook` | 取得筆記本詳細資訊 | ✅ |
| `list_sources` | 列出筆記本中的來源 | ✅ |
| `add_source` | 新增 URL 或文字來源 | ✅ |
| `ask` | 向筆記本提問並取得回答 | ✅ |

詳細規格請參閱 [TOOLS.md](../../docs/kof-notebooklm-mcp/TOOLS.md)。

## 使用範例

### 檢查連線

```
使用 health_check 工具驗證 NotebookLM 是否可存取。
```

### 研究工作流程

```
1. list_notebooks - 尋找現有研究筆記本
2. add_source - 新增 URL: https://example.com/docs
3. ask - "這份文件的主要論點是什麼？"
```

### 新增筆記作為來源

```
add_source 使用 source_type="text"，並傳入會議記錄的 markdown 內容
```

### 取得帶引用的回答

```
ask 搭配 include_citations=true 以取得來源參考
```

## CLI 指令

```bash
# 主要指令
kof-notebooklm init      # 互動式 Google 登入
kof-notebooklm health    # 檢查連線狀態
kof-notebooklm serve     # 啟動 MCP 伺服器

# 直接啟動伺服器
kof-notebooklm-mcp
```

## 開發

```bash
# 執行測試
pytest

# 執行特定測試
pytest tests/unit/test_retry.py -v

# 類型檢查
mypy src

# 程式碼風格檢查
ruff check src

# 格式化
ruff format src
```

### 專案結構

```
packages/kof-notebooklm-mcp/
├── pyproject.toml              # 套件設定
├── README.md                   # 本文件
├── TESTING.md                  # 測試計畫
├── src/kof_notebooklm_mcp/
│   ├── __init__.py
│   ├── config.py               # 設定管理
│   ├── server.py               # MCP 伺服器進入點
│   ├── cli.py                  # CLI 指令
│   ├── client/                 # 瀏覽器自動化層
│   │   ├── browser.py          # Playwright 管理
│   │   ├── session.py          # 工作階段管理
│   │   └── pages/              # 頁面物件模型
│   │       ├── base.py
│   │       ├── notebooks.py
│   │       └── notebook_detail.py
│   ├── tools/                  # MCP 工具實作
│   │   ├── health_check.py
│   │   ├── list_notebooks.py
│   │   ├── get_notebook.py
│   │   ├── list_sources.py
│   │   ├── add_source.py
│   │   └── ask.py
│   └── utils/                  # 工具函式
│       ├── validation.py       # 輸入驗證
│       ├── retry.py            # 重試邏輯
│       ├── rate_limit.py       # 速率限制
│       ├── circuit_breaker.py  # 斷路器
│       └── errors.py           # 錯誤處理
└── tests/
    ├── unit/                   # 單元測試
    ├── integration/            # 整合測試
    └── e2e/                    # 端對端測試
```

## 錯誤處理

### 常見錯誤碼

| 錯誤碼 | 說明 | 可恢復 |
|--------|------|--------|
| `AUTH_REQUIRED` | 需要重新認證 | 否 |
| `SESSION_EXPIRED` | 工作階段已過期 | 否 |
| `TIMEOUT` | 操作逾時 | 是 |
| `RATE_LIMITED` | 超過速率限制 | 是 |
| `NOT_FOUND` | 找不到資源 | 否 |
| `INVALID_INPUT` | 輸入驗證失敗 | 否 |
| `NETWORK_ERROR` | 網路連線問題 | 是 |

### 自動保護機制

- **重試邏輯**：可恢復錯誤自動重試（最多 3 次，指數退避）
- **速率限制**：防止過度請求（10 請求/分鐘）
- **斷路器**：連續失敗時暫停請求（5 次失敗後開啟，60 秒恢復）

## 已知限制

- **無官方 API**：使用瀏覽器自動化，NotebookLM UI 變更可能導致中斷
- **工作階段過期**：Google 工作階段約 2-4 週過期，需要重新認證
- **僅限本地**：設計為本地開發使用，非雲端部署
- **單一使用者**：每個伺服器實例一個 Google 帳號
- **串列操作**：操作依序處理（瀏覽器限制）
- **延遲**：瀏覽器操作每次約 2-10 秒

## 疑難排解

### 「Session expired」錯誤

```bash
kof-notebooklm-init  # 重新認證
```

### 瀏覽器無法啟動

```bash
playwright install chromium  # 確認已安裝
```

### 逾時問題

```bash
export NOTEBOOKLM_TIMEOUT=60000  # 增加逾時時間
```

### 除錯模式

```bash
export NOTEBOOKLM_HEADLESS=false  # 顯示瀏覽器
export NOTEBOOKLM_SLOW_MO=500     # 放慢操作
```

### 查看速率限制狀態

如果收到 `RATE_LIMITED` 錯誤，等待回應中指示的秒數後重試。

## 授權

MIT

## 相關連結

- [keeponfirst-local-brain](../../README.md) - 主專案
- [MCP 規格](https://modelcontextprotocol.io) - Model Context Protocol
- [Playwright 文件](https://playwright.dev/python/) - 瀏覽器自動化
