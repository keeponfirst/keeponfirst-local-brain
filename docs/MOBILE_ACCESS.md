# 手機端存取策略 (Mobile Access)

## 現況

- **桌面 / IDE**：Python 腳本（CLI）、Tauri commands（IPC）、MCP（Notion / NotebookLM）
- **手機**：目前沒有專案提供的 REST API，無法直接呼叫 `write_record.py` 或 Tauri

## 建議方案：以 Notion 為手機入口（優先）

不額外架設 API 伺服器的前提下，推薦做法：

1. **手機端**：使用 **Notion 官方 App** 或網頁，在「KeepOnFirst Brain」底下直接新增頁面或資料庫項目（當作 Decision / Idea / Worklog / Note）。
2. **桌面端**：沿用現有流程；必要時可用 **Notion MCP** 或本機 `search.py` / `publish_to_notion.py` 做 pull、搜尋或同步。
3. **優點**：無需維護 API、無 auth 層、與現有 `notion_api.py` 架構一致；Notion 已提供離線與同步。

### 實作要點

- 在 Notion 建立一個「手機快速捕捉」資料庫或固定子頁面，並在 SKILL / README 說明：手機上把想法記在這裡即可。
- 若未來要「從 Notion 拉回本地 records」：可再實作一個小腳本，用 Notion API 讀取該資料庫/頁面，轉成本地 `records/**/*.json` 格式（可選功能）。

## 替代方案：輕量 REST API（未來可選）

若日後需要「手機 App 直接打 API」而非透過 Notion：

- 可加一層 **FastAPI**（或 Cloud Functions）提供例如：
  - `POST /capture`：接收 draft JSON，後端呼叫 `write_record` 或 Notion API，再回傳結果。
- 需自行處理 **認證**（API key 或 OAuth）、**部署**與 **HTTPS**，維運成本較高。

目前建議先採用 **Notion 為手機入口**，待實際需求明確再考慮 REST API。
