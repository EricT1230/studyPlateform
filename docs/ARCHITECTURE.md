# ARCHITECTURE — 系統架構與演進北極星

> 這份文件是**所有 Phase 的共同約束**。任何新功能在動工前，要先確認它「從哪個接縫接進來」、
> 「有沒有違反鐵則」。Phase 各自的細節在各自的 spec；本文件管的是「整體怎麼長在一起」。
>
> 讀者：規劃者、審查者、以及每一位接手的實作者（搭配 [AGENTS.md](../AGENTS.md)）。
> 最後更新：2026-06-24

---

## 1. 一句話架構

**內容（YAML/Markdown，git）→ 後端（FastAPI，記憶體中的題庫 + SQLite 中的行為狀態）→ 前端（React）。**
題目是資料、不是程式；SQLite 只存「使用者行為衍生的狀態」（作答歷史、排程）；任何新功能都掛在這三層的既有接縫上。

```
┌─ 內容層 content/ ───────────────────────────────────────────┐
│  <科目>/<主題>.yaml  題目（題庫）                              │
│  <科目>/<主題>.md    教學/筆記                                 │
│  ＝ 唯一的「題目與知識」真實來源，純文字、可 diff、可 git      │
└───────────────┬─────────────────────────────────────────────┘
        啟動載入到記憶體（app.state.questions / questions_by_id）
┌───────────────▼─ 後端 app/ ─────────────────────────────────┐
│  content/   schema + loader（驗證、載入題庫）                 │
│  scheduler_service / *_service   純邏輯（無 I/O，好測）        │
│  db/        只存「行為衍生狀態」：attempts（事實）、schedule    │
│  api/       一個端點一個檔，靠 app.state 取題庫與 DB           │
└───────────────┬─────────────────────────────────────────────┘
                 HTTP / JSON
┌───────────────▼─ 前端 frontend/src ─────────────────────────┐
│  api/client.js     所有後端呼叫集中於此                       │
│  pages/ components/ 一頁一檔、可重用題卡                       │
└─────────────────────────────────────────────────────────────┘
```

## 2. 架構鐵則（不可違反 — 所有 Phase 共同遵守）

> 這是 [HANDOFF 第 3 節](HANDOFF.md) 的權威版本，並補上跨 Phase 的延伸意涵。

1. **題目內容永不進 DB。** 題庫只在 `content/` 的 YAML，啟動載入記憶體。SQLite 只存
   `question_id` + 行為/排程數字。→ CAG、新題型、新科目都不得把題目寫進 DB。
2. **DB 只存「行為衍生狀態」，且分表分責。** `attempts` = 不可變的事實紀錄；
   `schedule` = 衍生的排程狀態。新功能要存狀態 → 開新表、單一職責，**不要往 attempts 加欄位**。
3. **邏輯與 I/O 分離。** 演算法寫成純函式 service（`scheduler_service` 是範本）：吃參數、回值、
   不碰 DB、不碰時鐘（`today` 由呼叫端傳入）。→ 新演算法（SM-2、CAG 的檢索排序）照此寫，才好測。
4. **內容與程式分離；加內容不動程式。** 加題目 = 加 YAML；加科目 = 加資料夾。
   若一個新功能「需要改程式才能加內容」，多半是設計錯了。
5. **題型用 `type` 欄位區分，不用資料夾、不用分支硬寫。** 目前只有 `mcq`。新題型擴充 `type`
   的值與對應的「渲染 / 判分 / 排程映射」三個掛點（見 §5），**引擎主流程不該充滿 if-else**。
6. **前端所有後端呼叫集中在 `api/client.js`。** 頁面不直接 `fetch`。→ 換 API base、加 header、
   之後接 CAG 串流，只改一處。
7. **設定與密鑰走環境變數，不進 git。** 未來 CAG 的 API key 等，從環境讀取；`.env`（前端那種
   無密鑰的 base URL）可進 git，**含密鑰的設定一律 gitignore**。

## 3. 資料模型演進地圖

| 表 | Phase | 職責 | 鍵 |
|---|---|---|---|
| `attempts` | MVP | 每一次作答的事實紀錄（不可變） | autoincrement id |
| `schedule` | 1 | 每題的 Leitner 排程狀態（衍生） | question_id |
| `notes`（規劃中） | 2 | 使用者對某題/某主題的筆記（若改存 DB） | id 或 (scope, ref) |
| *無新表* | 3 (CAG) | CAG 不需新表：它讀題庫+筆記+attempts 組 context | — |
| *無新表* | 4 (新題型) | 新題型沿用 attempts/schedule；`type` 在題庫 YAML，不在 DB | — |

> **原則**：每個 Phase 最多新增「它自己的衍生狀態表」，且不動既有表結構。
> 若真的要改既有表，視為架構變更，須回到本文件更新並經審查。

## 4. API 表面演進

| 端點 | Phase | 說明 |
|---|---|---|
| `GET /subjects` | MVP | 科目/主題樹 |
| `GET /questions` | MVP | 篩選出題（subject/topic/difficulty/only_wrong） |
| `POST /attempts` | MVP→1 | 記錄作答；Phase 1 起順帶重排程 |
| `GET /stats` | MVP→1 | 統計；Phase 1 起多回 `due_today` |
| `GET /tutorials/{s}/{t}` | MVP | 取教學 Markdown |
| `GET /review` | 1 | 今日到期題（已排序） |
| `GET/PUT /notes/...`（規劃） | 2 | 讀寫筆記（若做 DB 版筆記） |
| `POST /tutor/ask`（規劃） | 3 | CAG 問答（可串流）；body 帶 question_id / 主題 / 對話歷史 |
| 既有端點 | 4 | 新題型沿用 `/questions`、`/attempts`、`/review`，回傳多帶 type-specific 欄位 |

> 端點維持「一個端點一個檔、靠 `app.state` 取依賴」的形狀。新端點不要繞過 `app.state` 自己連 DB。

## 5. 關鍵延伸接縫（新功能從這裡接進來）

### 5.1 新科目 / 更多題庫（Phase 2）
- **接縫**：`content/` 加資料夾與 YAML。零程式改動。
- **唯一限制**：通過 `schema.py` 驗證、`id` 全域唯一（loader 會擋重複）。
- 教學文章放同目錄 `<主題>.md`，前端題卡的「看教學」連結自動指過去。

### 5.2 新題型（Phase 4：翻牌卡、開放式自評）
題型擴充必須走「**三個掛點 + 一個欄位**」，不准在引擎主流程塞 if-else：
- **欄位**：題庫 YAML 的 `type`（目前僅 `mcq`）。`schema.py` 用可辨識聯集／分型驗證每種 type 的必填欄位。
- **掛點 A — 判分**：給定「使用者作答」與題目，算出結果。MCQ 是「選項索引 == answer」；
  翻牌卡是「使用者自評會/不會」；開放式是「使用者自評對/錯」。判分結果統一收斂成
  **二元 `is_correct`**（餵給既有 attempts/schedule，排程引擎完全不必懂題型）。
- **掛點 B — 排程映射**：把該題型的作答結果映射成 `is_correct`（見上）。→ Leitner/未來 SM-2 不動。
- **掛點 C — 前端渲染**：前端依 `type` 選對應的題卡元件（`McqCard` / `FlashCard` / …），
  共用「答完 → POST /attempts → 進下一題」的外殼。
- **架構結論**：因為排程吃的是二元 `is_correct`，**新題型不需要碰 scheduler、不需要新表**，
  只需 ①YAML 多一種 type ②後端判分收斂成 is_correct ③前端多一個題卡元件。這是當初把
  judging 設計成二元的回報。

### 5.3 CAG 解答小老師（Phase 3）
- **接縫**：新增一個 `tutor` 後端模組（service + 一個 router），與既有端點平行。
- **它讀什麼**：題庫（`app.state.questions`）+ 教學/筆記（`content/*.md`）+ 該題的 attempts 歷史，
  組成 context 餵給 Claude API（見 [claude-api 參考](#)／實作時查）。**它不寫題目進 DB、不改既有表。**
- **為何叫 CAG 而非 RAG**：題庫規模小，整包（或整科）塞進模型 context 即可，先不需要向量檢索；
  若未來題庫過大，再在 `tutor` 模組內部加檢索層，**對外介面不變**。
- **密鑰**：模型 API key 從環境變數讀取，不進 git（鐵則 7）。
- **前端**：新增對話介面；走 `api/client.js`（鐵則 6），可支援串流回應。

### 5.4 筆記（橫跨 Phase 2/3）
- 現況：筆記是 `content/<科目>/<主題>.md`，與題庫一起 git 管理，但**尚無 UI 可寫**。
- 兩條路（Phase 2 spec 會定）：①維持純檔案、做一個簡單編輯/檢視 UI；②搬進 `notes` 表。
- 架構影響：若做 DB 版，依鐵則 2 開 `notes` 表；CAG 讀筆記時對應改讀來源。**先在 Phase 2 spec 拍板，CAG 才好接。**

## 6. 跨 Phase 的設計一致性檢查（審查時對照）

任何 PR / 任務在審查時，對照這張表：

- [ ] 沒有把題目內容寫進 DB？
- [ ] 新狀態是開新表、還是亂改 attempts？（應開新表）
- [ ] 演算法是否寫成純函式 service、`today`/外部輸入由參數傳入？
- [ ] 加內容有沒有逼著改程式？（不該）
- [ ] 新題型有沒有走「type 欄位 + 三掛點」、而非主流程 if-else？
- [ ] 前端有沒有繞過 `api/client.js` 直接 fetch？
- [ ] 密鑰有沒有不小心進 git？

## 7. 已知技術環境（實作者必讀）

- **Python 3.14**（開發機）。相依需有 cp314 wheel；`requirements.txt` 已凍結可用版本。
- **Windows / PowerShell**：venv 啟用、`python -m pytest` 等細節見 [HANDOFF 第 1、6 節](HANDOFF.md)。
- 後端測試以真實 `TestClient` + 暫存 DB（不 mock 行為）；前端以 `npm run build` + 手動驗證。

## 8. 演進總覽（一張表看完）

| Phase | 主題 | 新表 | 新端點 | 動到既有 | 架構接縫 |
|---|---|---|---|---|---|
| 0 MVP | 選擇題引擎 | attempts | 5 個 | — | 三層基底 |
| 1 | 間隔重複 | schedule | /review | attempts(重排程)、stats(due_today) | §5 排程吃二元 is_correct |
| 2 | 題庫擴充 + 筆記 | (可能) notes | (可能) /notes | 內容為主 | §5.1 加內容、§5.4 筆記 |
| 3 | CAG 解答小老師 | 無 | /tutor/ask | 無（平行新模組） | §5.3 tutor 讀題庫+筆記+attempts |
| 4 | 新題型 | 無 | 無 | schema/前端題卡 | §5.2 type 欄位 + 三掛點 |

> 注意 Phase 3、4 **不動既有表、幾乎不改既有端點**——這是 §2 鐵則與 §5 接縫設計刻意換來的：
> 讓最複雜的兩塊（AI 家教、新題型）能以「平行新增」而非「侵入式修改」的方式落地。
