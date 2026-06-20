# Task Router

智慧任務分流系統 — 簡單任務交給本地模型 (oMLX)，複雜任務留給使用中的 agent。
支援 Spec Kit 或任何自訂工作流。

## 為什麼需要這個？

用 SDD（Spec-Driven Development）做開發時，不是每個階段都需要主 agent 的推理能力：

| 工作流階段 | 需要什麼 | 適合的模型 |
|------------|---------|-----------|
| constitution / specify / plan / gate | 深度推理、架構設計 | ☁️ Codex / Claude Code |
| tasks / checklist / analyze / digest / export | 結構化轉換 | 🖥️ 本地模型 |
| implement（簡單） | boilerplate, CRUD, config | 🖥️ 本地模型 |
| implement（複雜） | auth, security, 核心邏輯 | ☁️ Codex / Claude Code |

**結果：約 50% 的任務可以在本地執行，主 agent 專注在高風險或高推理工作。**

## 系統架構

```
Codex 或 Claude Code
    │
    ├── 複雜任務 → active agent 自己處理
    │
    └── Spec Kit tasks/checklist/analyze、i18n、docstring ...
         │
         └── Bash: ./scripts/call-omlx.sh
              │
              └── curl → oMLX (本地 Qwen3.5-9B)
```

**為什麼用 Bash+curl 作為共通層？**
- Codex 和 Claude Code 都能呼叫同一個 `call-omlx.sh` helper
- Spec Kit 的簡單階段可以維持同一套路由規則
- 使用者全程看得到「在做什麼」

不需要 proxy，不需要額外雲端 API key。

> **Legacy**: 舊版 MCP server (`mcp_omlx.py`) 保留為 optional，安裝時可選擇是否註冊。

## 環境需求

- macOS + Apple Silicon（M1 以上）
- [oMLX](https://omlx.ai/) — 本地 LLM 推理伺服器
- Codex CLI、Claude Code，或兩者都裝
- `curl` + `jq` — macOS 內建（`brew install jq` 若沒裝）
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — Python 套件管理

## 快速開始

### 1. 安裝 oMLX

從 [omlx.ai](https://omlx.ai/) 下載安裝，在 menu bar 啟動，載入一個模型（例如 Qwen3.5-9B-MLX-4bit）。

記下你的 oMLX API key（在 oMLX 設定裡可以找到）。

### 2. Clone 並一鍵安裝

```bash
git clone https://github.com/wewececetw/task-router.git
cd task-router
# 預覽，不寫入全域設定（預設 spec profile: github-spec-kit）
./install.sh --agent codex --dry-run

# Codex + GitHub Spec Kit
./install.sh --agent codex --spec github-spec-kit

# Codex + Fission-AI/OpenSpec
./install.sh --agent codex --spec github-open-spec

# Claude Code only
./install.sh --agent claude

# 同時安裝 Codex + Claude Code profile
./install.sh --agent both
```

安裝腳本會自動完成：
- 安裝 Python 依賴（`uv sync`）
- 複製 `scripts/call-omlx.sh` helper 到全域位置
- 依 `--spec` 寫入 GitHub Spec Kit 或 Fission-AI/OpenSpec workflow rules
- 寫入 Codex profile 到 `~/.codex/AGENTS.md` 與 `~/.codex/prompts/task-router/`（選 `codex` 或 `both`）
- 複製 Claude slash commands 到 `~/.claude/commands/` 並更新 `~/.claude/CLAUDE.md`（選 `claude` 或 `both`）
- 可選擇註冊 Claude legacy MCP server

**自動路由規則是核心：** Codex 與 Claude Code profile 使用同一套 agent 語意。你可以用 `--spec github-spec-kit` 或 `--spec github-open-spec` 選 spec workflow；翻譯 i18n、產 docstring 等輕量任務可委派給本地模型；複雜推理留給 active agent。

GitHub Spec Kit 本身仍是主要 workflow：`specify` CLI 與 `.specify/`
scripts/templates 負責初始化、spec、plan、tasks 等流程；oMLX 只是其中
`tasks/checklist/analyze` 和其他輕量產物的加速後端。

Fission-AI/OpenSpec 則由 `openspec` CLI、`openspec/changes/<change>/`、
`/opsx:propose`、`/opsx:apply`、`/opsx:archive` 管 workflow。Task Router
不會用 oMLX 取代 OpenSpec artifact lifecycle；oMLX 只支援周邊輕量任務。

### 3. 設定 Claude Desktop App（可選 / legacy MCP）

在 `~/Library/Application Support/Claude/claude_desktop_config.json` 加入：

```json
{
  "mcpServers": {
    "omlx-local": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/task-router", "python", "mcp_omlx.py"],
      "env": {
        "OMLX_API_KEY": "你的-omlx-key",
        "OMLX_BASE_URL": "http://127.0.0.1:9000/v1",
        "OMLX_MODEL": "Qwen3.5-9B-MLX-4bit"
      }
    }
  }
}
```

> **注意：** `command` 必須用 `uv` 的完整路徑（用 `which uv` 查詢），Claude Desktop 的 PATH 很有限。

重啟 Claude Desktop App 即可使用。

### 4. 開始使用

在任何專案裡開 Codex 或 Claude Code，**安裝後對選定 profile 生效**：

```bash
# Claude Code: 手動指定本地模型
/local 翻譯這段英文成中文

# Spec Kit — Codex / Claude Code 依同一規則自動路由
/speckit.specify   # ☁️ active agent 處理（需推理）
/speckit.plan      # ☁️ active agent 處理（架構決策）
/speckit.tasks     # 🖥️ 自動委派給本地模型（省 token）
/speckit.analyze   # 🖥️ 自動委派給本地模型
/speckit.checklist # 🖥️ 自動委派給本地模型

# 輕量工具（一律走本地）
/i18n /docstring /migration /test-stub /changelog /implement-simple
```

**怎麼知道有沒有自動路由？** 看 agent 的 tool call 列表 — 出現 `./scripts/call-omlx.sh` 或 `~/.task-router/scripts/call-omlx.sh` 就代表有走本地模型。

## 支援的 Spec Workflows

### GitHub Spec Kit（預設）

[GitHub Spec Kit](https://github.com/github/spec-kit) 的 Spec-Driven Development 工作流：
constitution → specify → clarify → plan → tasks → implement → analyze → checklist

如果專案還沒初始化 Spec Kit：

```bash
specify init --here --ai codex --offline
```

### Fission-AI/OpenSpec

OpenSpec 的 lightweight SDD workflow：
`/opsx:propose` → `/opsx:apply` → `/opsx:archive`

安裝 OpenSpec CLI：

```bash
npm install -g @fission-ai/openspec@latest
openspec init
```

使用 Task Router 安裝 OpenSpec profile：

```bash
./install.sh --agent codex --spec github-open-spec
```

### CLI 用法

```bash
uv run task-router phases --workflow speckit
uv run task-router ask "generate task list" --workflow speckit
```

## Preset 系統（Spec Kit 品質守門）

本地模型在沒有明確格式範例時容易亂產（例如 `SETUP-001` 而非 `T001`、忘記標 `[P]`）。Preset 系統解決這問題：

```bash
# 用 preset，內建 few-shot 範例 + 自動驗證
./scripts/call-omlx.sh "$(cat plan.md)" --preset speckit-tasks
```

**流程**：
1. `scripts/presets/speckit-tasks.md` 當作 system prompt（含完整格式規則 + 範例輸出）
2. oMLX 產出後，`scripts/validators/speckit-tasks.sh` 檢查規範：
   - Task ID 必須是 `T001`、`T002`... 全域單調（不可 `SETUP-001`）
   - User story phase 才能加 `[US1]/[US2]/[US3]`，Setup/Polish 不能加
   - 必須有 `[P]` 平行標記、Dependencies 區塊
   - 任務數量介於 5-40（太少表示拆不夠，太多表示過度拆解）
3. **不符規範 → exit code 5**，active agent 接手重做

| Preset | 用途 | Validator 規則數 |
|--------|------|-----|
| `speckit-tasks` | 從 plan 生成 tasks.md | 6 |
| `speckit-checklist` | 從 spec+plan 生成品質檢查清單 | 4 |
| `speckit-analyze` | 跨檔案一致性分析 | 3 |

可以自己加新 preset：在 `scripts/presets/` 寫 system prompt（含 few-shot 範例），在 `scripts/validators/` 寫對應驗證腳本。

## 內建保護機制

| 機制 | 說明 |
|------|------|
| Preset validator | Spec Kit 輸出不符規範自動 fallback（exit 5） |
| Auto-compact | 輸入超過 70% context window 時自動壓縮再送 |
| Chunked map-reduce | 超過 90% 時自動分段處理再合併 |
| Fallback | 真的太大就回報，active agent 自己接手 |
| Thinking 過濾 | 自動關閉 Qwen3.5 思考模式 + 過濾 `<think>` 標籤 |
| macOS 通知 | 任務完成/失敗時彈系統通知，不用盯著等 |
| Progress feedback | 即時中英混合進度回饋 |

## 可用的 MCP Tools

| Tool | 說明 |
|------|------|
| `local_llm` | 送 prompt 給本地模型，支援 system prompt |
| `local_llm_batch` | 批量送多個 prompt，適合一次處理多個小任務 |
| `local_llm_status` | 檢查 oMLX 伺服器狀態和可用模型 |

## Claude Code Slash Commands

| 指令 | 說明 | 路由 |
|------|------|------|
| `/local <任務>` | 手動丟給本地模型 | 🖥️ oMLX |
| `/tasks` | 從 plan 生成任務列表 | 🖥️ oMLX |
| `/checklist` | 生成品質檢查清單 | 🖥️ oMLX |
| `/implement-simple` | 實作簡單任務（boilerplate, CRUD, config） | 🖥️ oMLX |
| `/analyze` | 檢查 spec/plan/tasks 一致性 | 🖥️ oMLX |
| `/docstring` | 為程式碼加 docstring/JSDoc | 🖥️ oMLX |
| `/test-stub` | 生成測試骨架 | 🖥️ oMLX |
| `/migration` | 生成 DB migration | 🖥️ oMLX |
| `/i18n` | 翻譯 i18n 字串檔 | 🖥️ oMLX |
| `/changelog` | 從 git diff 生成 changelog | 🖥️ oMLX |

## CLI 工具

```bash
# 查看工作流階段路由表
uv run task-router phases
uv run task-router phases --workflow speckit

# 分析 tasks.md 裡每個任務的路由
uv run task-router phases examples/sample-tasks.md

# 直接路由並執行任務
OMLX_API_KEY=xxx uv run task-router ask "翻譯 hello world" --phase tasks -v
```

## LiteLLM Proxy（替代方案）

如果你有 Anthropic API key，也可以用 LiteLLM proxy 模式：

```bash
OMLX_API_KEY=xxx ANTHROPIC_API_KEY=xxx python proxy_router.py --port 4000
```

這會啟動一個 proxy，自動根據工作流階段分流到 oMLX 或 cloud backend。

## 授權

MIT

## 作者

Barron
