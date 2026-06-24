# Phase 4 — 新題型（翻牌卡 + 開放式自評）— 設計文件

- **日期**：2026-06-24
- **狀態**：設計已確認，待動工前產實作計畫
- **Phase**：Roadmap Phase 4
- **架構接縫**：[ARCHITECTURE §5.2（type 欄位 + 三掛點）](../../ARCHITECTURE.md)

> 實作由他人進行。動工前讀 [AGENTS.md](../../../AGENTS.md)、[ARCHITECTURE.md](../../ARCHITECTURE.md)。
> **本 Phase 是架構驗證**：證明「新題型只需加 type、收斂成二元 is_correct、加前端題卡」，
> 不必碰排程、不必新表。實作時若發現要改 scheduler 或加表，代表做錯了，回頭對照架構。

---

## 1. 目的

在既有選擇題引擎上，增加兩種題型：
- **翻牌卡（flashcard）**：正面問題、背面解答，使用者自評「會 / 不會」。適合背單字、口頭面試題。
- **開放式自評（open_ended）**：給題目與參考解答，使用者對照後自評「對 / 錯」。適合演算法推導、統計計算。

## 2. 核心架構決策（已確認，對照 [ARCHITECTURE §5.2](../../ARCHITECTURE.md)）

新題型一律走「**一個欄位 + 三個掛點**」，引擎主流程不得充滿 if-else：

1. **欄位 `type`**：題庫 YAML 的 `type`（目前 `mcq`，新增 `flashcard`、`open_ended`）。
2. **掛點 A — 判分（收斂成二元 `is_correct`）**：
   - `mcq`：`chosen == answer`（後端算）。
   - `flashcard` / `open_ended`：**使用者自評**，前端直接送 `is_correct`（後端不評，信任自評）。
3. **掛點 B — 排程映射**：所有題型的判分都收斂成 `is_correct` → 餵給**既有** attempts/schedule。
   **scheduler、attempts 表、schedule 表完全不變。**
4. **掛點 C — 前端渲染**：依 `type` 選對應題卡元件，共用「答完 → POST /attempts → 進下一題」外殼。

> 關鍵洞見：因為排程吃的是二元 `is_correct`，新題型**不需新表、不碰 scheduler**。這是 MVP 把判分
> 設計成二元的回報（[ARCHITECTURE §5.2 結論](../../ARCHITECTURE.md)）。

## 3. 範圍

### 本 Phase 做
- `schema.py`：用**可辨識聯集（discriminated by `type`）**驗證每種題型的必填欄位。
- `POST /attempts`：接受 mcq 的 `chosen` 或自評型的 `self_correct`，依題型收斂成 `is_correct`。
- 前端：題卡 dispatcher + `FlashCard`、`OpenEndedCard` 兩個新元件；練習頁/複習頁改用 dispatcher。
- 種子內容：每種新題型各加一個示範題庫檔（例如 `content/english/vocabulary-cards.yaml`）。

### 本 Phase 不做（YAGNI）
- 自動評分開放式題目（一律使用者自評）。
- 新的 DB 表 / 改 scheduler / 改 schedule 表。
- 富文本卡片（純 Markdown 即可）。

## 4. 題庫格式（各題型）

**mcq（不變）**：`question / options / answer / explanation`。

**flashcard（新）**：
```yaml
- id: en-card-001
  type: flashcard
  difficulty: basic
  tags: [vocabulary]
  front: |
    deprecated（軟體語境）
  back: |
    仍可用但不建議使用，未來版本可能移除。
```

**open_ended（新）**：
```yaml
- id: algo-proof-001
  type: open_ended
  difficulty: advanced
  tags: [sorting, proof]
  question: |
    證明比較排序的最差時間複雜度下界為 Ω(n log n)。
  reference: |
    決策樹有 n! 個葉節點，高度 ≥ log(n!) = Θ(n log n)，故下界 Ω(n log n)。
```

### schema 驗證（discriminated union）
- 共同欄位：`id, type, difficulty, tags`。
- 依 `type` 驗必填：`mcq`→`question/options/answer`；`flashcard`→`front/back`；`open_ended`→`question/reference`。
- `LoadedQuestion` 仍附 `subject/topic`。loader、`/questions`、`/review` 不需改（它們對題型不可知，
  只回 `model_dump()`；前端依 `type` 渲染）。

## 5. 作答契約（POST /attempts 調整）

目前 body：`{question_id, chosen}`。調整為相容多題型：

```
{ question_id, chosen?, self_correct? }
```
- `mcq`：必須帶 `chosen`；後端算 `is_correct = (chosen == answer)`（行為不變）。
- `flashcard` / `open_ended`：必須帶 `self_correct`（bool）；`is_correct = self_correct`。
- 後端依該題 `type` 決定取哪個欄位；缺對應欄位回 400。
- 之後流程不變：`record_attempt` + 重排程（Phase 1 邏輯）。回應沿用 `{is_correct, ...}`，
  並可附該題型需要的回顯（flashcard 回 `back`、open_ended 回 `reference` 供對照）。

> 判分收斂點就在這裡：不論題型，最終都產生一個 `is_correct` 交給既有 attempts/schedule。

## 6. 前端

- **題卡 dispatcher**：`QuestionView`（新）依 `question.type` 渲染：
  - `mcq` → 既有 `QuestionCard`（更名/保留皆可，行為不變）。
  - `flashcard` → `FlashCard`：顯示 front → 點「翻面」顯示 back → 使用者按「會 / 不會」→ 送 `self_correct`。
  - `open_ended` → `OpenEndedCard`：顯示 question → 使用者思考/作答 → 點「看參考解答」顯示 reference →
    按「我對了 / 我錯了」→ 送 `self_correct`。
- 練習頁、複習頁改成渲染 `QuestionView`（取代直接用 `QuestionCard`），其餘外殼（佇列、進下一題）不變。
- `api/client.js` 的 `postAttempt` 調整成可帶 `chosen` 或 `self_correct`。

## 7. 測試
- `schema`：三種 type 各自必填欄位驗證；缺欄位被拒；未知 type 被拒。
- `POST /attempts`：mcq 用 chosen、flashcard/open_ended 用 self_correct 正確收斂成 is_correct；
  缺對應欄位回 400；自評型仍正確觸發重排程（沿用 Phase 1 斷言）。
- 前端：build + 手動驗證（翻牌卡能翻面自評、開放式能看參考解答自評，且都會進排程）。

## 8. 檔案異動總覽
```
backend/app/
  content/schema.py     ← 修改：discriminated union 驗證三種 type
  api/attempts.py       ← 修改：依 type 取 chosen / self_correct 收斂 is_correct
backend/tests/
  test_schema.py        ← 修改：加 flashcard / open_ended 驗證
  test_attempts_api.py  ← 修改：加自評型作答 + 重排程斷言
content/                ← 新增各題型示範題庫檔
frontend/src/components/
  QuestionView.jsx      ← 新增：依 type 分派
  FlashCard.jsx OpenEndedCard.jsx ← 新增
frontend/src/pages/
  Practice.jsx Review.jsx ← 修改：改用 QuestionView
frontend/src/api/client.js ← 修改：postAttempt 支援 self_correct
```

## 9. 設計鐵則一致性（這份 spec 的重點）
- **scheduler、schedule 表、attempts 表完全不動** → 證明排程吃二元 is_correct 的設計成立。
- 新題型靠 `type` 欄位 + 三掛點，引擎主流程不堆 if-else。
- 題目仍只在 YAML、不進 DB。
- 前端呼叫集中 `api/client.js`。
