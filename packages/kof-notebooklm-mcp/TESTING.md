# kof-notebooklm-mcp 測試計畫

> 最後更新：2026-01-28

本文件包含 kof-notebooklm-mcp 的測試策略、手動測試清單和自動化測試說明。

---

## 測試策略

### 測試金字塔

```
        /\
       /  \     E2E 測試（手動）
      /----\    - 真實 NotebookLM 互動
     /      \   - 需要認證
    /--------\
   /          \ 整合測試（部分自動化）
  /            \ - 瀏覽器啟動
 /--------------\- 頁面物件驗證
/                \
/==================\ 單元測試（全自動化）
- 設定管理
- 輸入驗證
- 重試邏輯
- 速率限制
- 斷路器
- 錯誤處理
```

### 測試分類

| 類型 | 執行方式 | 頻率 | 需要認證 |
|------|----------|------|----------|
| 單元測試 | `pytest tests/unit/` | 每次提交 | 否 |
| 整合測試 | `pytest tests/integration/` | 每次提交 | 否 |
| E2E 測試 | 手動執行 | 發布前 | 是 |

---

## 手動測試清單

### 前置條件

- [ ] Python 3.10+ 已安裝
- [ ] 已執行 `pip install -e ".[dev]"`
- [ ] 已執行 `playwright install chromium`
- [ ] 擁有 NotebookLM 存取權限的 Google 帳號
- [ ] 帳號中至少有一個筆記本（含來源）

---

### M1：認證流程

#### TC-M1-01：首次安裝

- [ ] 執行 `pip install -e ".[dev]"`
- [ ] 確認無錯誤訊息
- [ ] 執行 `playwright install chromium`
- [ ] 確認瀏覽器安裝成功

#### TC-M1-02：初始化認證

- [ ] 執行 `kof-notebooklm-init`
- [ ] 確認瀏覽器視窗開啟
- [ ] 手動登入 Google 帳號
- [ ] 確認導航到 NotebookLM 首頁
- [ ] 關閉瀏覽器視窗
- [ ] 確認顯示「認證成功」訊息
- [ ] 確認 `~/.kof-notebooklm/profile/` 目錄已建立

#### TC-M1-03：健康檢查（成功）

- [ ] 執行 `kof-notebooklm-health`
- [ ] 確認回傳 JSON 格式
- [ ] 確認 `status` 為 `"healthy"`
- [ ] 確認 `authenticated` 為 `true`
- [ ] 確認 `browser_ok` 為 `true`

#### TC-M1-04：健康檢查（未認證）

- [ ] 刪除或重命名 `~/.kof-notebooklm/profile/`
- [ ] 執行 `kof-notebooklm-health`
- [ ] 確認 `status` 為 `"unhealthy"`
- [ ] 確認 `authenticated` 為 `false`
- [ ] 確認 `error` 包含認證相關訊息

#### TC-M1-05：工作階段持久性

- [ ] 完成認證（TC-M1-02）
- [ ] 執行 `kof-notebooklm-health` 確認健康
- [ ] 等待 5 分鐘
- [ ] 再次執行 `kof-notebooklm-health`
- [ ] 確認仍然健康（工作階段持續有效）

---

### M2：讀取操作

#### TC-M2-01：列出筆記本

- [ ] 啟動 MCP 伺服器或使用測試客戶端
- [ ] 呼叫 `list_notebooks`
- [ ] 確認回傳筆記本列表
- [ ] 確認每個筆記本包含 `id`、`name`
- [ ] 確認筆記本數量與 NotebookLM 網頁一致

#### TC-M2-02：列出筆記本（帶限制）

- [ ] 呼叫 `list_notebooks` 搭配 `limit=2`
- [ ] 確認回傳最多 2 個筆記本
- [ ] 確認 `total` 欄位反映實際總數

#### TC-M2-03：取得筆記本詳細資訊

- [ ] 從 TC-M2-01 取得一個筆記本 ID
- [ ] 呼叫 `get_notebook` 搭配該 ID
- [ ] 確認回傳包含 `id`、`name`、`source_count`
- [ ] 確認資訊與 NotebookLM 網頁一致

#### TC-M2-04：取得筆記本（無效 ID）

- [ ] 呼叫 `get_notebook` 搭配 `notebook_id="invalid_id_12345"`
- [ ] 確認回傳錯誤
- [ ] 確認錯誤碼為 `NOT_FOUND` 或 `TIMEOUT`

#### TC-M2-05：列出來源

- [ ] 選擇一個有來源的筆記本
- [ ] 呼叫 `list_sources` 搭配該筆記本 ID
- [ ] 確認回傳來源列表
- [ ] 確認每個來源包含 `id`、`title`、`type`
- [ ] 確認來源數量與 NotebookLM 網頁一致

#### TC-M2-06：列出來源（空筆記本）

- [ ] 建立或使用一個無來源的筆記本
- [ ] 呼叫 `list_sources`
- [ ] 確認回傳空列表 `[]`
- [ ] 確認 `total` 為 `0`

---

### M3：寫入操作

#### TC-M3-01：新增 URL 來源

- [ ] 選擇一個筆記本
- [ ] 記錄目前來源數量
- [ ] 呼叫 `add_source` 搭配：
  - `source_type="url"`
  - `url="https://en.wikipedia.org/wiki/Artificial_intelligence"`
- [ ] 確認回傳 `success: true`
- [ ] 確認 `processing_status` 為 `"complete"` 或 `"processing"`
- [ ] 在 NotebookLM 網頁確認來源已新增

#### TC-M3-02：新增文字來源

- [ ] 選擇一個筆記本
- [ ] 呼叫 `add_source` 搭配：
  - `source_type="text"`
  - `text="# 測試文件\n\n這是一段測試文字，用於驗證文字來源功能。"`
  - `title="測試文字來源"`
- [ ] 確認回傳 `success: true`
- [ ] 在 NotebookLM 網頁確認來源已新增

#### TC-M3-03：新增來源（無效 URL）

- [ ] 呼叫 `add_source` 搭配：
  - `source_type="url"`
  - `url="not-a-valid-url"`
- [ ] 確認回傳錯誤
- [ ] 確認錯誤碼為 `INVALID_URL`

#### TC-M3-04：新增來源（危險 URL）

- [ ] 呼叫 `add_source` 搭配：
  - `source_type="url"`
  - `url="javascript:alert(1)"`
- [ ] 確認回傳錯誤
- [ ] 確認錯誤碼為 `INVALID_URL`
- [ ] 確認錯誤訊息提及「不安全」

#### TC-M3-05：新增來源（空文字）

- [ ] 呼叫 `add_source` 搭配：
  - `source_type="text"`
  - `text=""`
- [ ] 確認回傳錯誤
- [ ] 確認錯誤碼為 `INVALID_INPUT`

#### TC-M3-06：新增來源（無效筆記本 ID）

- [ ] 呼叫 `add_source` 搭配：
  - `notebook_id="invalid_notebook_id"`
  - `source_type="url"`
  - `url="https://example.com"`
- [ ] 確認回傳錯誤

---

### M4：查詢操作

#### TC-M4-01：基本提問

- [ ] 選擇一個有來源的筆記本
- [ ] 呼叫 `ask` 搭配：
  - `question="這個筆記本的主要內容是什麼？"`
- [ ] 確認回傳包含 `answer`
- [ ] 確認 `answer` 非空且相關

#### TC-M4-02：提問並取得引用

- [ ] 呼叫 `ask` 搭配：
  - `question="請總結主要論點"`
  - `include_citations=true`
- [ ] 確認回傳包含 `citations` 陣列
- [ ] 確認引用包含 `source_id`、`source_title`

#### TC-M4-03：提問不含引用

- [ ] 呼叫 `ask` 搭配：
  - `question="簡單描述內容"`
  - `include_citations=false`
- [ ] 確認回傳不包含 `citations` 或 `citations` 為空

#### TC-M4-04：提問（空筆記本）

- [ ] 使用一個無來源的筆記本
- [ ] 呼叫 `ask` 搭配任意問題
- [ ] 確認回傳錯誤
- [ ] 確認錯誤碼為 `NO_SOURCES` 或 `CHAT_UNAVAILABLE`

#### TC-M4-05：提問（長問題）

- [ ] 呼叫 `ask` 搭配超長問題（>10000 字元）
- [ ] 確認回傳錯誤
- [ ] 確認錯誤碼為 `QUESTION_TOO_LONG`

#### TC-M4-06：建議問題

- [ ] 呼叫 `ask` 搭配任意問題
- [ ] 檢查回傳是否包含 `follow_up_questions`
- [ ] 如有，確認為字串陣列

---

### M5：錯誤處理與保護機制

#### TC-M5-01：速率限制

- [ ] 快速連續呼叫 15 次 `list_notebooks`
- [ ] 確認某次呼叫回傳 `RATE_LIMITED` 錯誤
- [ ] 確認錯誤包含 `retry_after_seconds`
- [ ] 等待指定時間後重試成功

#### TC-M5-02：斷路器（需要模擬失敗）

- [ ] 設定 `NOTEBOOKLM_TIMEOUT=1`（極短逾時）
- [ ] 連續呼叫多次操作導致失敗
- [ ] 確認第 6 次後回傳「服務暫時不可用」
- [ ] 等待 60 秒後恢復

#### TC-M5-03：無頭模式

- [ ] 設定 `NOTEBOOKLM_HEADLESS=true`
- [ ] 執行 `kof-notebooklm-health`
- [ ] 確認無瀏覽器視窗出現
- [ ] 確認操作成功

#### TC-M5-04：除錯模式

- [ ] 設定 `NOTEBOOKLM_HEADLESS=false`
- [ ] 設定 `NOTEBOOKLM_SLOW_MO=500`
- [ ] 執行 `list_notebooks`
- [ ] 確認瀏覽器視窗出現
- [ ] 確認操作明顯放慢

---

### M6：整合測試

#### TC-M6-01：完整工作流程

- [ ] 執行 `kof-notebooklm-init`（如需要）
- [ ] 執行 `kof-notebooklm-health`
- [ ] 呼叫 `list_notebooks`
- [ ] 選擇一個筆記本，呼叫 `get_notebook`
- [ ] 呼叫 `list_sources`
- [ ] 呼叫 `add_source`（URL）
- [ ] 呼叫 `add_source`（文字）
- [ ] 呼叫 `ask`
- [ ] 確認所有操作成功

#### TC-M6-02：MCP 客戶端整合

- [ ] 設定 Claude Desktop 的 MCP 設定
- [ ] 重啟 Claude Desktop
- [ ] 在對話中使用 NotebookLM 工具
- [ ] 確認工具呼叫成功
- [ ] 確認回應正確顯示

---

## 自動化測試

### 執行單元測試

```bash
# 執行所有單元測試
pytest tests/unit/ -v

# 執行特定測試檔案
pytest tests/unit/test_validation.py -v

# 顯示覆蓋率
pytest tests/unit/ --cov=kof_notebooklm_mcp --cov-report=html
```

### 測試檔案清單

| 檔案 | 測試內容 |
|------|----------|
| `test_config.py` | 設定載入、環境變數 |
| `test_validation.py` | URL、文字、標題驗證 |
| `test_health_check.py` | HealthCheckResult 資料類別 |
| `test_page_objects.py` | NotebookInfo、SourceInfo 等 |
| `test_ask.py` | AskResult、Citation、信心估計 |
| `test_retry.py` | 重試邏輯、指數退避 |
| `test_rate_limit.py` | Token bucket、速率限制 |
| `test_circuit_breaker.py` | 斷路器狀態轉換 |
| `test_errors.py` | 錯誤分類、標準化回應 |

### 預期覆蓋率目標

- 單元測試：>80% 行覆蓋率
- 關鍵路徑：100% 覆蓋

---

## 測試環境清理

每次測試後建議清理：

```bash
# 移除測試時新增的來源（手動在 NotebookLM 網頁執行）

# 重置瀏覽器設定檔（如需要）
rm -rf ~/.kof-notebooklm/profile/
```

---

## 問題回報

發現問題時，請記錄：

1. 測試案例編號（如 TC-M2-03）
2. 執行環境（OS、Python 版本）
3. 完整錯誤訊息
4. 重現步驟
5. 預期 vs 實際結果

---

## 附錄：測試資料

### 測試用 URL

```
https://en.wikipedia.org/wiki/Artificial_intelligence
https://docs.python.org/3/tutorial/
https://www.example.com
```

### 測試用文字

```markdown
# 測試文件

## 簡介
這是一份用於測試的文件。

## 內容
- 項目一
- 項目二
- 項目三

## 結論
測試完成。
```

### 測試用問題

```
1. 這份文件的主要內容是什麼？
2. 請總結三個重點。
3. 有哪些關鍵概念？
4. 這和人工智慧有什麼關係？
```
