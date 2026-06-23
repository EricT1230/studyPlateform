# 個人刷題打底平台 — 設計文件

- **日期**：2026-06-23
- **狀態**：設計已確認，待寫實作計畫
- **使用者**：RD 工程師，目標是打實基礎、轉外商 / 升 Senior

## 1. 目的與定位

一個**給自己用**的「打底 + 刷題」工具，把分散的知識整理成有系統、能反覆練習的形式。

核心學習模式：**做中學（active recall）**。使用者直接讀書容易放空、不確定哪裡不會；透過解題逼自己主動回想，並把弱點外顯，遇到不會的再回頭補成筆記。

**非目標**：不是多人平台、不需要帳號系統、不需雲端規模化、不在網頁內跑程式碼（真正的程式練習在 LeetCode 做）。

### 價值優先序
1. **刷題 / 練習**（核心）
2. **實作 / 動手**（之後；程式執行外包給 LeetCode）
3. **整理 / 筆記**（掛在題目旁的附屬）

## 2. 範圍

### MVP（這一輪）
- 內容格式 + 種子題庫，兩條並列地基：
  - **技術線**：資料結構（演算法緊跟其後）
  - **職涯線**：工程師 / 外商英文（字彙閱讀 + 職場溝通「選最佳說法」）
- 題型：**選擇題（MCQ）** only
- FastAPI 後端：載入題庫、依條件出題、記錄作答、統計
- React 前端：儀表板 + 練習頁 + 教學頁 + 瀏覽頁
- **錯題本式**追蹤，資料結構預留升級成間隔重複

### 明確不做（各自為未來的小專案）
- 間隔重複演算法（Anki 邏輯）— 但資料已在累積
- CAG 解答小老師（吃題庫+筆記當知識源；也當英文口說對話教練）
- 翻牌卡、開放式自評題、線上跑程式碼
- 英文口說 / 即時對答（無法用 MCQ 自動批改，留給 CAG）
- 其他科目題庫（OS → 網路 → DB/分散式；ML/AI/PyTorch/統計）—— 架構好後「加科目」只是加檔案

### 地基科目的判斷依據
依賴圖：資料結構 → 演算法 → LeetCode；資料結構也是 DB/OS/網路/分散式的共同底層。
資料結構投資報酬率最高、每天都在用、是上 LeetCode 的真正前置知識。
英文與資料結構**並列**為地基：資料結構通過技術關，英文決定能否進外商。

## 3. 整體架構

三層，內容與程式徹底分離：

```
內容層 (純文字檔, git 管理)
  content/ 下 YAML 題目 + Markdown 教學/筆記
        │  後端啟動載入 / 開發熱重載
後端 (FastAPI + SQLite)
  · 讀題庫檔、提供篩選/出題 API
  · SQLite 只存「作答歷史」(進度)，不存題目
  · v2: CAG 解答小老師掛這層
        │  HTTP / JSON
前端 (React + Vite)
  · 刷題、看解析、做筆記、看「我哪裡不會」儀表板
```

**關鍵原則**：題庫（會一直長大、常改）與程式碼（穩定）分開。SQLite **只**存進度；題庫永遠是可讀純文字、能 git diff、換工具不怕。

## 4. 內容格式與目錄結構

目錄按 `科目 / 主題` 分；難度是題目標籤而非資料夾。

```
content/
  data-structures/
    arrays.yaml
    arrays.md            # (選用) 主題教學文章
    linked-lists.yaml
    trees.yaml
    hash-tables.yaml
  algorithms/
    sorting.yaml
    searching.yaml
  english/
    vocabulary.yaml      # 工程字彙 / 閱讀
    communication.yaml   # 職場溝通「選最得體說法」
```

一題（YAML）：

```yaml
- id: ds-arrays-001        # 穩定唯一 ID，進度靠它對應
  type: mcq                # 目前只 mcq，欄位預留未來題型
  difficulty: basic        # basic / intermediate / advanced / master
  tags: [arrays, complexity]
  question: |
    存取陣列中第 i 個元素的時間複雜度是？
  options:
    - O(1)
    - O(n)
    - O(log n)
    - O(n log n)
  answer: 0                # 正確選項索引 (0-based)
  explanation: |
    陣列為連續記憶體，可由位址直接計算，故為 O(1)。
```

**設計理由**：`id` 穩定→改題文進度不跑掉；`type`/`difficulty` 為欄位→未來加題型/難度免改架構；一主題一檔→批次生成方便。

筆記：MVP 存成 `content/` 下對應 Markdown，與題庫一起 git 管理。

## 5. 後端（FastAPI + SQLite）

SQLite 核心表（題庫本身不進 DB）：

```
attempts
  id            自動編號
  question_id   對應 YAML 的 id (字串)
  is_correct    對 / 錯
  chosen        選的選項索引
  answered_at   作答時間
```

存「每一次作答」而非僅「對錯次數」→ 未來升級間隔重複所需歷史，現在就在累積。

API：

| 方法 | 路徑 | 功能 |
|---|---|---|
| GET | `/subjects` | 列出科目/主題（掃檔案得出） |
| GET | `/questions?subject=&topic=&difficulty=&only_wrong=` | 依條件出題（含「只練錯過的」） |
| POST | `/attempts` | 記錄一次作答 |
| GET | `/stats` | 各科/各難度正確率、弱點排行 |
| GET | `/tutorials/{subject}/{topic}` | 取得主題 Markdown 教學 |

題庫於後端啟動時載入記憶體（純文字檔快），開發時熱重載。

## 6. 前端（React + Vite）四畫面

1. **儀表板**：「今天練什麼」入口 + 弱點一覽（哪科哪難度正確率最低、最常錯）。
2. **練習頁（核心）**：一次一題 → 選答案 → 立刻顯示對錯+解析 → 旁邊寫/看筆記 → 下一題。支援篩選（科目/主題/難度/只練錯過的）。
3. **教學頁**：渲染主題 Markdown，讀完可直接「練這主題」。
4. **瀏覽/管理頁**：列出題目、搜尋、看作答紀錄（編輯題目仍直接改 YAML）。

## 7. 測試策略

- 後端 API：pytest（出題篩選、作答記錄、統計計算正確）。
- 題庫檔：schema 驗證，防止生成的 YAML 格式跑掉。
- 前端：MVP 階段以手動驗證為主。

## 8. 技術選型

- 後端：**Python + FastAPI + SQLite**（理由：使用者要學的 ML/PyTorch/AI/統計皆 Python，工具本身即練習場；未來 CAG / 向量檢索 / 跑模型 Python 生態最順）。
- 前端：**React + Vite**。
- 內容：YAML（題目）+ Markdown（教學/筆記），git 管理。
