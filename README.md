# Study Drill Platform

個人用的刷題打底工具：用選擇題邊做邊學，系統記錄你的作答歷史、標出「哪裡不會」，並把教學掛在題目旁。

- **後端**：FastAPI + SQLite（Python）。從 `content/` 載入 YAML 題庫到記憶體；SQLite 只存作答歷史。
- **前端**：React + Vite。儀表板 / 練習 / 教學 / 瀏覽四個頁面。
- **內容**：`content/<科目>/<主題>.yaml`（題目）+ `<主題>.md`（選用教學），純文字、git 管理。

題庫與程式碼徹底分開——題目永遠是可讀的 YAML，能 `git diff`、能換工具。

## 用 Docker 跑（推薦）

只需要安裝 **Docker Desktop**，不用自己裝 Python / Node。

**開發模式（熱重載）** — 改 code 即時生效：

```bash
docker compose -f docker-compose.dev.yml up --build
```

- 後端 `uvicorn --reload`，改 `backend/app/**.py` 自動重啟
- 前端 Vite dev server，HMR + React Fast Refresh，改前端即時熱替換
- 開瀏覽器到 http://localhost:5173

**正式模式** — 前端 build 成靜態檔由 nginx 提供：

```bash
docker compose up --build
```

- 前端走 nginx 同源 + `/api` 反向代理到後端，**沒有 CORS 問題**
- 一樣開 http://localhost:5173

收掉容器：

```bash
docker compose down                              # 正式
docker compose -f docker-compose.dev.yml down    # 開發
```

> 作答進度存在具名 volume `studyplateform_study-data`（`down` 不會清掉，資料保留）。
> 題庫 `content/` 以讀寫掛載進容器：改 YAML 重啟後端即生效（不用重 build），筆記功能也會把 `<主題>.notes.md` 寫回這裡（git 管理）。
> 後端 API 文件在 http://localhost:8000/docs 。

## 本機手動跑

需要 **Python 3.11+** 和 **Node 18+**。開兩個終端機：

**1) 後端**（埠 8000）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> 若 PowerShell 擋住啟用 venv，先執行 `Set-ExecutionPolicy -Scope Process Bypass`。

**2) 前端**（埠 5173）

```powershell
cd frontend
npm install
npm run dev
```

開瀏覽器到 http://localhost:5173 。

## 測試

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

## 新增題目

在 `content/<科目>/<主題>.yaml` 加一筆（一個主題一個檔，裡面是題目陣列）：

```yaml
- id: ds-arrays-004        # 穩定唯一 ID，進度靠它對應，別重複
  difficulty: basic        # basic / intermediate / advanced / master
  tags: [arrays]
  question: |
    你的題目敘述
  options: ["選項 A", "選項 B", "選項 C", "選項 D"]
  answer: 1                # 正確選項索引（0 起算）
  explanation: |
    解析說明
```

重啟後端即生效。要加新科目就新增一個資料夾即可，程式碼不用改。

## 進度資料

作答歷史存在 `backend/progress.db`（git 忽略）。每一次作答都記錄下來，未來要升級成「間隔重複（Anki 式）」複習時，所需的歷史現在就在累積。

## 文件

- [AGENTS.md](AGENTS.md) — 接手 Agent 的定向導言（動工前先讀）
- [系統架構 ARCHITECTURE](docs/ARCHITECTURE.md) — 鐵則、資料模型演進、各 Phase 的接縫
- [企畫書](docs/企畫書.md) — 願景、學科地基策略、開發里程碑
- [HANDOFF](docs/HANDOFF.md) — 交接與動工指南（給接手實作的人）
- [設計 spec](docs/superpowers/specs/2026-06-23-study-drill-platform-design.md)
- [MVP 實作計畫](docs/superpowers/plans/2026-06-23-study-drill-platform.md)

## 路線圖（之後）

- 間隔重複排程（用已累積的作答歷史）
- CAG 解答小老師（吃題庫+筆記當知識源，也當英文口說對話教練）
- 翻牌卡 / 開放式自評題
- 更多科目題庫（OS → 網路 → DB/分散式；ML/AI/PyTorch/統計）
