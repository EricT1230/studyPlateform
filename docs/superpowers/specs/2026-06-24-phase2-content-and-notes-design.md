# Phase 2 — 題庫擴充與筆記 — 設計文件

- **日期**：2026-06-24
- **狀態**：設計已確認，待動工前產實作計畫
- **Phase**：Roadmap Phase 2
- **架構接縫**：[ARCHITECTURE §5.1（新科目）、§5.4（筆記）](../../ARCHITECTURE.md)

> 實作由他人進行。動工前讀 [AGENTS.md](../../../AGENTS.md)、[ARCHITECTURE.md](../../ARCHITECTURE.md)。
> 本 Phase 分兩塊：**A. 題庫擴充（內容為主、幾乎不動程式）** 與 **B. 筆記功能（要寫程式）**。

---

## A. 題庫擴充（內容策略）

### 目的
把第一、二梯隊學科的題庫補到「足以天天刷」的量與深度。這是**內容工作**，靠加 YAML，
不動架構（[ARCHITECTURE §5.1](../../ARCHITECTURE.md)）。

### 範圍與順序（依企畫書學科策略）
1. **第一梯隊補滿**：資料結構（hash table、tree、heap、graph、stack/queue）、演算法（搜尋、遞迴/DP、greedy、圖論）、英文（更多職場溝通情境、技術閱讀）。
2. **第二梯隊開新科**：OS → 網路與 Web Server 模型 → Database / 分散式系統。各科從 `content/<科目>/` 新資料夾起步。
3. 每科每難度（basic→master）逐步鋪量。

### 產線與品質門檻
- **生成**：由規劃方（Claude）批次生成題目草稿（「給我 OS - 行程排程 - 中級 15 題」）。
- **訂正**：擁有者校對正確性與解析；生成只是草稿。
- **驗收**：`load_questions(CONTENT_DIR)` 無例外（schema 驗證 + id 唯一）；難度分佈合理；每題有 `explanation`。
- **id 慣例**：`<科縮寫>-<主題>-<序號>`，全域唯一、不事後改（進度靠它對應）。

### 為何不需 spec→plan→code 流程
純加 YAML 不改程式。照 [HANDOFF §4 題庫撰寫規範](../../HANDOFF.md) 直接做即可。本段是策略與驗收，不是程式任務。

---

## B. 筆記功能（要寫程式）

### 目的
讓擁有者把「刷題遇到的卡點」就地寫成筆記，與題庫一起 git 管理；未來 CAG 也讀得到（[ARCHITECTURE §5.4](../../ARCHITECTURE.md)）。

### 核心決策（已確認）
- **筆記存純檔案 `.md`**（非 DB），符合「內容與程式分離」鐵則、可 diff、可 git。
- **粒度：以「主題」為單位**的一份筆記檔。一個主題一個 `content/<科目>/<主題>.notes.md`，
  是該主題的個人 scratchpad（可自由分段、可自己用題目 id 當小標）。
  - *為何不是每題一檔*：每題一檔會產生上千個碎檔、難維護。主題級 scratchpad 是檔案模型下最簡潔的選擇。

### 資料與檔案
- 路徑：`content/<subject>/<topic>.notes.md`（與 `<topic>.yaml`、`<topic>.md` 同目錄）。
- 後端可**讀也可寫**這個檔（單人本機工具，無並發疑慮）。寫入用 `encoding="utf-8"`。
- `.notes.md` 一樣進 git（擁有者自行決定何時 commit）。

### API（沿用「一端點一檔、靠 app.state」形狀）
| 方法 | 路徑 | 功能 |
|---|---|---|
| `GET` | `/notes/{subject}/{topic}` | 回該主題筆記 Markdown；無檔回空字串（非 404，方便前端直接編） |
| `PUT` | `/notes/{subject}/{topic}` | 寫入/覆蓋該主題筆記檔（body: `{markdown}`）；目錄不存在則建立 |

> 安全性：`subject`/`topic` 需驗證為單純檔名片段（不含 `/`、`..`），避免路徑跳脫寫到 content 之外。
> 這是本 Phase 唯一的安全注意點，實作計畫要明列驗證。

### 前端
- **筆記面板**：在練習頁／複習頁的題卡旁、以及教學頁，提供「✍️ 筆記」可展開的編輯區
  （`textarea` + 儲存鈕，呼叫 `PUT /notes`）。讀取用 `GET /notes`。
- 題卡已有「📖 看教學」連結；筆記面板與它並列。
- API client 新增 `getNotes(subject, topic)`、`saveNotes(subject, topic, markdown)`。

### 測試
- 後端：`GET /notes`（有檔/無檔）、`PUT /notes`（建立、覆蓋、目錄自動建立）、**路徑跳脫被拒**（`..`、含 `/` 的片段回 400）。
- 前端：build + 手動驗證（寫入後重讀一致、空筆記不報錯）。

### 檔案異動總覽
```
backend/app/
  notes_service.py     ← 新增：安全解析路徑 + 讀寫 .notes.md（純函式 + I/O 分離）
  api/notes.py         ← 新增：GET/PUT /notes
  main.py              ← 修改：掛 notes router
backend/tests/
  test_notes_service.py  test_notes_api.py   ← 新增
frontend/src/
  components/NotesPanel.jsx   ← 新增
  api/client.js              ← 修改：getNotes / saveNotes
  pages/Practice.jsx / Review.jsx / Tutorial.jsx ← 修改：嵌入 NotesPanel
```

### 設計鐵則一致性
- 筆記是 `content/` 下的 Markdown → 未違反「內容與程式分離」「題目/知識不進 DB」。
- `notes_service` 路徑解析為純函式、檔案 I/O 分離 → 好測、可擋路徑跳脫。
