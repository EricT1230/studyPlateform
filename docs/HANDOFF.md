# HANDOFF — 動工交接文件

> AI agent 接手請先讀 [AGENTS.md](../AGENTS.md)（定向導言），再讀本檔。
> 給接手實作的人（人類開發者或 AI coding agent）。讀完這份就能動工。
> 高層次的「為什麼/做什麼」見 [企畫書](企畫書.md)。
>
> 最後更新：2026-06-24

---

## 0. 工作模式（先讀這段）

- **Claude（規劃 + 審視）**：寫 spec、寫實作計畫（plan）、做 code review。**不主導動工。**
- **你（實作者）**：照 plan 一個任務一個任務做，每個任務 TDD + 獨立 commit。
- **節奏**：每個新功能都走一輪 **spec → plan → 實作 → review**。
  - 要開新功能？先回去找 Claude 走 brainstorming 出 spec、再出 plan。**不要在沒有 plan 的情況下硬幹大功能。**
  - 拿到 plan 後，照任務逐項實作；每完成一個任務交給 Claude review，過了再下一個。
- **你該回來找 Claude 的時機**：①要開新 Phase / 新功能（要 spec+plan）②一個任務做完要 review ③遇到計畫沒預期的架構抉擇。

## 1. 環境與啟動

需要 **Python 3.11+**（目前開發機是 3.14）與 **Node 18+**。

```powershell
# 後端（埠 8000）
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # 被擋的話先 Set-ExecutionPolicy -Scope Process Bypass
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端（埠 5173）— 另一個終端機
cd frontend
npm install
npm run dev
```

開 http://localhost:5173 。

**測試**（每次動完都要跑）：
```powershell
cd backend; .\.venv\Scripts\Activate.ps1; python -m pytest    # 應 30 passed
cd frontend; npm run build                                    # 前端以 build 通過為 smoke test
```

## 2. 程式碼地圖（每個檔案的職責）

```
content/                      ← 題庫與教學（資料，不是程式）
  <科目>/<主題>.yaml          ← 題目陣列
  <科目>/<主題>.md            ← (選用) 該主題教學文章

backend/
  requirements.txt            ← 已凍結為有 Python 3.14 wheel 的版本
  pyproject.toml              ← requires-python + pytest 設定（filterwarnings）
  app/
    config.py                 ← CONTENT_DIR / DB_PATH 路徑
    main.py                   ← create_app()：載入題庫、建 questions_by_id、init DB、掛 router
    content/
      schema.py               ← Pydantic Question / LoadedQuestion + 驗證
      loader.py               ← load_questions(dir)：掃 YAML、組 subject/topic、擋重複 id
    db/
      database.py             ← get_connection() / init_db()（attempts 表）
      attempts.py             ← record_attempt() / wrong_question_ids()（最近一次錯的題）
    stats_service.py          ← compute_stats()：各科/難度正確率 + 最常錯題
    api/                      ← 一個端點一個檔
      subjects.py  questions.py  attempts.py  stats.py  tutorials.py
  tests/                      ← 每個模組對應一個 test_*.py；conftest.py 提供 client fixture

frontend/src/
  api/client.js               ← 所有後端呼叫集中在此（getSubjects/getQuestions/postAttempt/getStats/getTutorial）
  App.jsx                     ← router + 導覽列
  pages/  Dashboard / Practice / Tutorial / Browse
  components/ Filters.jsx  QuestionCard.jsx
  styles.css
```

## 3. 關鍵設計決策與理由（不要違反這些）

1. **SQLite 只存作答歷史，題目永遠不進 DB。** 題庫是 `content/` 的 YAML，後端啟動載入記憶體。
   → 為了讓題庫可讀、可 diff、可換工具。**新功能不要把題目寫進 DB。**
2. **每一次作答都記一列**（不是只記對錯次數）。→ 未來間隔重複需要完整歷史，現在就要累積。
3. **`only_wrong` = 最近一次作答是錯的**（答對後就離開錯題本）。SQL 用 `MAX(id)` 取最近一次。
4. **題目 `id` 穩定且唯一**，進度靠它對應。改題目文字不能改 id；loader 會擋重複 id。
5. **`type` / `difficulty` 是欄位不是資料夾**。→ 未來加題型、加難度不需改架構。
6. **內容與程式分離**是最高原則。加科目 = 加資料夾，**不該動程式碼**。

## 4. 內容撰寫規範（題庫格式）

一個主題一個 YAML 檔，內容是題目陣列：

```yaml
- id: ds-arrays-004          # 穩定唯一；建議 <科縮寫>-<主題>-<序號>，別重複、別事後改
  type: mcq                  # 目前只支援 mcq（可省略，預設 mcq）
  difficulty: basic          # basic / intermediate / advanced / master（只有這四個）
  tags: [arrays, complexity] # 自由標籤
  question: |
    題目敘述（可多行）
  options: ["A", "B", "C", "D"]   # 至少 2 個
  answer: 1                  # 正確選項索引，0 起算，必須在 options 範圍內
  explanation: |
    解析（答完會顯示）
```

- 教學文章放同目錄 `<主題>.md`，前端題卡與瀏覽頁會有「📖 看教學」連結指過去。
- 改完重啟後端（或開 `--reload`）即生效。
- **所有檔案用 UTF-8**。

加新科目：在 `content/` 下開一個資料夾、丟 YAML 進去即可，程式零改動。

## 5. 測試與品質門檻

- 後端**每個任務 TDD**：先寫會失敗的測試 → 看它失敗 → 實作 → 看它通過 → commit。
- 後端測試用真實 `TestClient` + 暫存 content dir + 暫存 SQLite（見 `conftest.py`），**不要 mock 掉真行為**。
- 前端 MVP 階段以 `npm run build` 通過 + 手動驗證為主。
- **commit 前**：後端 `pytest` 全綠且輸出乾淨（無雜訊警告）、前端 build 通過。
- 每個任務一個聚焦 commit，訊息用 `feat:` / `fix:` / `refactor:` / `docs:` / `content:` 前綴。

## 6. 慣例與雷區

| 雷區 | 說明 / 因應 |
|---|---|
| **Python 3.14** | 計畫原本釘的舊套件沒有 3.14 wheel（pydantic-core 需 Rust 編譯會失敗）。`requirements.txt` 已凍結為有 cp314 wheel 的版本（pydantic 2.13.4、pyyaml 6.0.3、fastapi 0.138.0…）。升級套件前先確認有 3.14 wheel。 |
| **Windows / PowerShell** | venv 啟用被擋 → `Set-ExecutionPolicy -Scope Process Bypass`。跑 pytest 用 `python -m pytest`（確保 `app/` 可被 import）。 |
| **CRLF 警告** | git 會提示 LF→CRLF，無害。可選擇加 `.gitattributes` 統一，但非必要。 |
| **CORS** | 後端只允許 `http://localhost:5173`（見 `main.py`）。前端換埠要同步改。 |
| **progress.db** | 作答歷史檔，已被 `.gitignore`。別 commit 它。 |
| **SQLite 執行緒** | 連線用 `check_same_thread=False`（uvicorn 多執行緒需要）。 |

## 7. 待辦 Backlog（下一批可動工的任務）

> 開動前先找 Claude 為該 Phase 出 spec + plan。以下是方向與驗收，不是 plan 本身。

**最高優先：題庫擴充（Phase 2，可立即做、無需大改）**
- [ ] 資料結構補到 basic→master 各約 8–10 題（hash table、tree、heap、graph、stack/queue）
- [ ] 演算法補（搜尋、遞迴/DP、greedy、圖論基礎）
- [ ] 英文補（更多職場溝通情境、技術閱讀理解）
- 驗收：`load_questions(CONTENT_DIR)` 無例外、前端能篩到新題、難度分佈合理。

**間隔重複（Phase 1，需 spec+plan）**
- [ ] 設計排程演算法（SM-2 或簡化版），讀 `attempts` 歷史算下次複習時間
- [ ] 新增 `GET /review/today` 出「今日該複習」清單
- [ ] 前端儀表板加「今日複習」入口
- 驗收：答錯題間隔縮短、答對拉長；每日清單正確。

**CAG 解答小老師（Phase 3，需 spec+plan）**
- [ ] 設計把題庫+筆記組成 context 的策略；接 Claude API
- [ ] 問答 API + 前端對話介面；英文口說對話教練模式
- 驗收：能就某題/主題追問並得到貼合題庫的解說。

## 8. 已知缺口（最終 review 列出、尚未處理的 minor）

來自 2026-06 整體分支 review，皆非 bug、不阻擋使用：

- **`marked` 未做 HTML sanitize**（`Tutorial.jsx`）。目前內容皆單人 git 管理，無 XSS 風險；若未來內容來源變廣，需加 sanitize。
- **`Practice` 的洗牌用 `Math.random()-0.5`**，非均勻洗牌。對「變化順序」夠用；若順序變重要再換 Fisher–Yates。
- 前端尚無自動化測試（MVP 以 build + 手動驗證為主）。題庫/邏輯變複雜後可考慮加 Vitest + React Testing Library。

## 9. 參考文件

- [企畫書](企畫書.md) — 願景、學科策略、里程碑
- [設計 spec](superpowers/specs/2026-06-23-study-drill-platform-design.md)
- [MVP 實作計畫](superpowers/plans/2026-06-23-study-drill-platform.md) — 13 任務、含完整程式碼，是動工的範本格式
- [README](../README.md) — 使用者導向的啟動/加題說明
