# Phase 3 — CAG 解答小老師 — 設計文件

- **日期**：2026-06-24
- **狀態**：設計已確認，待動工前產實作計畫
- **Phase**：Roadmap Phase 3
- **架構接縫**：[ARCHITECTURE §5.3（CAG tutor 平行模組）](../../ARCHITECTURE.md)
- **前置**：Phase 2 筆記功能（CAG 讀筆記當知識源）

> 實作由他人進行。動工前讀 [AGENTS.md](../../../AGENTS.md)、[ARCHITECTURE.md](../../ARCHITECTURE.md)。

---

## 1. 目的

一個 AI 家教：就某一題、某主題，或英文情境，與使用者對話、解釋、追問。
知識源是**使用者自己的題庫 + 教學 + 筆記 + 作答歷史**（Cache-Augmented Generation：把相關內容整包塞進
模型 context，而非向量檢索）。

## 2. 核心決策（已確認）

- **CAG 而非 RAG**：題庫規模小，把「相關主題的題目+教學+筆記」整包塞進 context 即可，先不做向量檢索。
  若未來題庫過大，於 `tutor` 模組內部加檢索層、**對外介面不變**（[ARCHITECTURE §5.3](../../ARCHITECTURE.md)）。
- **模型 provider 待定 → 介面設計成可換**：定義 `TutorProvider` 抽象，先提供一個實作（預設指向 Claude API），
  但呼叫端只依賴抽象。實際選哪個 provider 在動工時決定、由設定切換。
- **英文口說教練：先做文字對話**（語音 STT/TTS 不在本 Phase）。
- **不新增 DB 表**：CAG 只讀既有資料；對話歷史先存在前端（ephemeral），不落 DB（[ARCHITECTURE §2、§3](../../ARCHITECTURE.md)）。
- **密鑰走環境變數、不進 git**（鐵則 7）。

## 3. 範圍

### 本 Phase 做
- `tutor` 後端模組：context 組裝（純函式）+ `TutorProvider` 抽象 + 一個 provider 實作 + `POST /tutor/ask`。
- 兩種模式：①**解題家教**（針對某題/主題問答）②**英文對話教練**（情境角色扮演，文字）。
- 前端對話介面：可從題卡「🧑‍🏫 問小老師」進入，也有獨立頁。
- 設定：provider 與 API key 由環境變數讀取。

### 本 Phase 不做（YAGNI）
- 向量檢索 / 嵌入（題庫夠小）。
- 語音輸入輸出（STT/TTS）。
- 對話歷史持久化（先存前端）。
- 多 provider 同時並存的 UI 切換（先一個生效的 provider）。

## 4. 架構與資料流

```
前端對話 UI ──POST /tutor/ask──▶ tutor router
                                   │ 1. build_context(scope) 純函式
                                   │    讀 app.state.questions + content/*.md
                                   │    + content/*.notes.md + 該題 attempts 歷史
                                   │ 2. TutorProvider.complete(system, messages)
                                   ▼
                              （回應，可串流）──▶ 前端顯示
```

### 4.1 Context 組裝（純函式，好測）
```python
# tutor/context.py
def build_context(scope, questions_by_id, content_dir, conn) -> str:
    """scope 指定 question_id 或 (subject, topic)。
    組出：題目+選項+正解+解析、該主題教學(.md)、該主題筆記(.notes.md)、
    （若有 question_id）該題的作答歷史摘要。回傳要放進 system prompt 的字串。"""
```
- 不呼叫模型、不碰網路 → 單元測試只驗「context 內容正確、缺檔時優雅略過」。

### 4.2 Provider 抽象（可換）
```python
# tutor/provider.py
class TutorProvider(Protocol):
    def complete(self, system: str, messages: list[dict]) -> Iterator[str]:
        """回傳文字串流（chunk 疊代）。messages 為 [{role, content}]。"""

# 預設實作（動工時決定是否啟用）：ClaudeProvider 讀 ANTHROPIC_API_KEY
# 載入哪個 provider 由設定/環境變數決定；router 只依賴 TutorProvider。
```
> 實作 ClaudeProvider 時查 [claude-api 技能](../../HANDOFF.md) 取得正確的 model id、SDK 用法、串流與
> tool use 細節——**不要憑記憶寫 API 呼叫**。

### 4.3 端點
| 方法 | 路徑 | body | 回應 |
|---|---|---|---|
| `POST` | `/tutor/ask` | `{mode, scope?, messages}` | 文字（建議串流；MVP 可先非串流） |

- `mode`：`"solve"`（解題家教，需 `scope`）或 `"english"`（英文教練，`scope` 可省，改帶情境設定）。
- `scope`：`{question_id}` 或 `{subject, topic}`。
- `messages`：對話歷史（前端維護）。
- 後端依 `mode` 組 system prompt（solve 用 build_context；english 用情境模板），呼叫 provider。

## 5. 前端

- **對話面板**：可從題卡「🧑‍🏫 問小老師」開啟（自動帶入該題 scope），也有獨立「小老師」頁做英文對話。
- 對話歷史存在前端 state（重整即清空，本 Phase 不持久化）。
- 走 `api/client.js` 新增 `askTutor(payload)`；若做串流，於 client 統一處理 SSE/stream（鐵則 6）。
- 導覽列可加「小老師」入口。

## 6. 設定與密鑰

- `ANTHROPIC_API_KEY`（或所選 provider 的 key）從環境變數讀取。
- 後端啟動時若未設 key：`/tutor/ask` 回明確錯誤（例如 503 + 「未設定 tutor provider」），其餘功能不受影響。
- **任何含密鑰的設定檔一律 gitignore。**

## 7. 測試

- `build_context` 純函式單元測試：含題目/教學/筆記/歷史時內容正確；缺教學或缺筆記時優雅略過、不報錯；
  question_id 不存在時的處理。
- `TutorProvider` 用**假 provider**（回固定字串）做 router 整合測試：`/tutor/ask` 正確組 context 並回傳；
  未設 key/未啟用 provider 時回明確錯誤。**不要在測試打真實 API。**
- 前端：build + 手動驗證（能就某題問答、英文對話模式可用）。

## 8. 檔案異動總覽
```
backend/app/
  tutor/__init__.py
  tutor/context.py      ← build_context 純函式
  tutor/provider.py     ← TutorProvider 抽象 + 一個實作（讀環境變數）
  tutor/prompts.py      ← solve / english 兩種 system prompt 模板
  api/tutor.py          ← POST /tutor/ask
  main.py               ← 掛 tutor router（provider 由設定注入 app.state）
backend/tests/
  test_tutor_context.py  test_tutor_api.py（用假 provider）
frontend/src/
  components/TutorPanel.jsx   pages/Tutor.jsx
  api/client.js              ← askTutor（含串流處理）
```

## 9. 設計鐵則一致性
- 不新增 DB 表、不寫題目進 DB；CAG 只讀既有內容與 attempts。
- context 組裝為純函式、與模型呼叫分離；provider 抽象讓模型可換 → 單一職責、可測、可換。
- 密鑰走環境變數、不進 git。
- 前端呼叫集中 `api/client.js`。
