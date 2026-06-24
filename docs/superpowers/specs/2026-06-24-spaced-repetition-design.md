# 間隔重複（Spaced Repetition）— 設計文件

- **日期**：2026-06-24
- **狀態**：設計已確認，待寫實作計畫
- **Phase**：Roadmap Phase 1（見 [企畫書](../../企畫書.md)）
- **前置**：MVP 已完成（見 [MVP 設計](2026-06-23-study-drill-platform-design.md)）

> 實作由他人進行。本文件為設計依據；逐步實作步驟見對應的
> [實作計畫](../plans/)（writing-plans 產出）。動工前請先讀
> [AGENTS.md](../../../AGENTS.md) 與 [HANDOFF.md](../../HANDOFF.md)。

---

## 1. 目的

讓系統根據你的作答歷史，自動安排「哪些題該在今天複習」，把答錯/不熟的題用遞增的間隔反覆resurface，答對就拉長間隔。解決「學過就忘、不知道何時該回頭複習」的問題。

這是 MVP「錯題本」的演進：錯題本只會列出「最近一次答錯的題」；間隔重複則為**每一題**維護一個遞增的複習排程。

## 2. 核心設計決策（已確認）

1. **排程模型：Leitner 盒子（二元），資料結構預留 SM-2。** 判分是二元（對/錯），Leitner 比硬套 SM-2 更貼合且更簡單。`box` 欄位之外保留升級空間，但本 Phase 不實作 SM-2。
2. **統一模型：任何一次作答都更新排程。** 不論在練習頁或複習頁作答，都會更新該題的盒號與到期日。複習頁只是「把今天到期的撈出來」的檢視。
3. **不設每日上限；以排序處理 backlog。** 到期題全部顯示，按「最逾期 → 盒號低 → id」排序，讓有限時間先花在最該複習的題上。
4. **排程狀態存獨立 `schedule` 表（衍生狀態）。** `attempts`（事實紀錄）不動；`schedule` 每次作答後更新。不違反「題目永不進 DB」鐵則——`schedule` 只存 question_id 與排程數字。

## 3. 範圍

### 本 Phase 做
- `schedule` 資料表（每題一列：box / due_date / last_reviewed）
- `scheduler_service.py`：純函式 Leitner 邏輯（吃「目前盒號 + 對錯」→「新盒號 + 新到期日」）
- `schedule` repository：讀寫 schedule 表、查今日到期題
- `POST /attempts` 整合：每次作答後更新該題排程
- `GET /review`：回傳今天到期的題目清單（已排序）
- `GET /stats` 調整：多回一個 `due_today` 計數
- 前端：新增「複習」頁、導覽列加「複習」連結、儀表板加「今天待複習」入口

### 本 Phase 不做（YAGNI，明確排除）
- 每日複習上限 / 超量順延
- 新卡（never-seen）介紹佇列 / 每日新卡數
- 自評信心等級、答題秒數等額外訊號
- SM-2 演算法本身（只預留 `box` 以外的彈性，不寫公式）
- 複習提醒通知 / 連續天數 streak

## 4. Leitner 演算法（精確規格）

### 盒號與間隔
五個盒子，間隔（天）固定如下：

| box | interval（天） |
|---|---|
| 1 | 1 |
| 2 | 3 |
| 3 | 7 |
| 4 | 16 |
| 5 | 35 |

`MAX_BOX = 5`。

### 狀態轉移
給定一次作答的 `is_correct` 與該題「作答前的目前盒號 `box`」（若該題尚無排程，視為**尚未建立**）：

1. 若該題尚無 `schedule` 列：先以 `box = 1` 建立（代表「剛進入排程」的起點）。
2. 套用轉移到「作答前盒號」：
   - **答對**：`new_box = min(box + 1, MAX_BOX)`
   - **答錯**：`new_box = 1`
3. `new_due_date = today + INTERVALS[new_box]` 天
4. 寫回：`box = new_box`、`due_date = new_due_date`、`last_reviewed = today`

> 注意轉移作用在「作答前盒號」。第一次作答時起點 box=1，故：
> - 第一次**答對** → box 1→2，due = today + 3 天
> - 第一次**答錯** → box 1→1，due = today + 1 天
> 兩者不同，符合直覺。

### 純函式介面（建議）
```python
# scheduler_service.py
INTERVALS = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}
MAX_BOX = 5

def next_schedule(current_box: int, is_correct: bool, today: date) -> tuple[int, date]:
    """回傳 (new_box, new_due_date)。current_box 為作答前盒號（新題傳 1）。"""
```
此函式不碰 DB、不碰 today 以外的時間——`today` 由呼叫端傳入，方便測試。

## 5. 資料模型

新增表（題庫內容仍不進 DB）：

```sql
CREATE TABLE IF NOT EXISTS schedule (
    question_id   TEXT PRIMARY KEY,
    box           INTEGER NOT NULL,
    due_date      TEXT    NOT NULL,   -- 'YYYY-MM-DD'
    last_reviewed TEXT    NOT NULL    -- 'YYYY-MM-DD'
);
```

- 日期一律存 `YYYY-MM-DD` 字串，比較用字串比較即可（ISO 格式字串可直接 `<=` 比較）。
- 「今天」取伺服器本地日期（`date.today()`）。

### schedule repository（建議介面）
```python
# db/schedule.py
def get_box(conn, question_id: str) -> int | None
    """回傳目前盒號；無排程回 None。"""

def upsert_schedule(conn, question_id: str, box: int, due_date: date, today: date) -> None
    """建立或更新一題的排程列。"""

def due_question_ids(conn, today: date) -> list[str]
    """回傳 due_date <= today 的 question_id，已按 (due_date ASC, box ASC, question_id ASC) 排序。"""

def due_count(conn, today: date) -> int
    """今天到期題數。"""
```

## 6. 整合與 API

### POST /attempts（修改）
在現有「記錄 attempt」之後，新增「更新排程」：
1. 查該題作答前盒號：`current = get_box(conn, qid)`；若 `None` 視為新題、`current = 1`。
2. `new_box, new_due = next_schedule(current, is_correct, today)`。
3. `upsert_schedule(conn, qid, new_box, new_due, today)`。
4. 回傳內容**不變**（`is_correct` / `answer` / `explanation`）。

### GET /review（新增）
- 取 `ids = due_question_ids(conn, today)`。
- 依 `ids` 的順序，從 `app.state.questions_by_id` 取出對應題目（保持排序）。
- 若某 id 在題庫已不存在（題被刪），跳過（與 stats 的 stale 處理一致）。
- 回傳格式同 `GET /questions`（前端可重用題卡）。

### GET /stats（修改）
- 既有回傳不變，**新增** `due_today: int`（= `due_count(conn, today)`）。

## 7. 前端

### 新增「複習」頁（`pages/Review.jsx`）
- 載入時 `GET /review`。
- **重用 `QuestionCard`**：一次一題、即時對錯+解析+看教學連結，與練習頁一致。
- 答完一題進下一題（`POST /attempts` 已順帶重排程）。
- 清單練完 → 「今天複習完成 🎉」。
- 清單為空 → 「今天沒有要複習的，去練習頁刷新題吧」。

### 導覽列與儀表板
- 導覽列加「複習」連結：**儀表板 · 練習 · 複習 · 瀏覽**。連結可顯示今日待複習數（badge）。
- 儀表板新增一塊「今天待複習：N 題」+ 進複習頁的入口（讀 `/stats` 的 `due_today`）。

### API client（`api/client.js`）
新增 `getReview()` 對應 `GET /review`。

## 8. 測試策略

- **`scheduler_service` 單元測試（核心，測最重）**：答對升盒、答錯歸 1、box 5 封頂不溢出、各盒到期日計算正確、第一次答對/答錯結果不同。`today` 以固定日期傳入。
- **schedule repository 測試**：upsert 後可讀回；`due_question_ids` 只回到期題且排序正確（最逾期優先、同期盒號低優先）。
- **POST /attempts 重排程整合測試**：答對後該題 due_date 往後推、答錯後明天到期；未作答題在 `schedule` 無列。
- **GET /review 整合測試**：只回到期題、排序正確、未作答題不出現、題庫已刪的 id 被跳過。
- **GET /stats** 整合測試：`due_today` 計數正確。
- **前端**：build 通過 + 手動驗證（複習頁能撈到期題、答完重排、空清單提示、儀表板數字）。

## 9. 檔案異動總覽

```
backend/app/
  scheduler_service.py     ← 新增：Leitner 純邏輯
  db/schedule.py           ← 新增：schedule repository
  db/database.py           ← 修改：init_db 多建 schedule 表
  api/attempts.py          ← 修改：作答後呼叫排程更新
  api/review.py            ← 新增：GET /review
  api/stats.py             ← 修改：stats 加 due_today（或於 stats_service 計算）
  stats_service.py         ← 修改：compute_stats 多回 due_today
  main.py                  ← 修改：掛 review router
backend/tests/
  test_scheduler_service.py  ← 新增
  test_schedule_repo.py      ← 新增
  test_review_api.py         ← 新增
  test_attempts_api.py       ← 修改：加重排程斷言
  test_stats_api.py          ← 修改：加 due_today 斷言
frontend/src/
  pages/Review.jsx         ← 新增
  api/client.js            ← 修改：加 getReview
  App.jsx                  ← 修改：加複習路由與導覽連結
  pages/Dashboard.jsx      ← 修改：加今日待複習區塊
```

## 10. 設計鐵則一致性檢查

- 題目內容仍只在 YAML；`schedule` 僅存 question_id 與排程數字 → 未違反「題目永不進 DB」。
- `attempts` 仍是事實來源、不變；`schedule` 為衍生狀態。
- `box`/`due_date` 為欄位，未來加 SM-2 訊號（信心、秒數）可擴充欄位而不需重構 → 與「欄位而非資料夾」精神一致。
- `scheduler_service` 為純函式、與 DB 分離 → 單一職責、好測。
