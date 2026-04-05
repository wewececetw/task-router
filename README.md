# Task Router

智慧任務分流系統 — 簡單任務交給本地模型 (oMLX)，複雜任務留給 Claude。
支援 Spec Kit 或任何自訂工作流。

## 為什麼需要這個？

用 SDD（Spec-Driven Development）做開發時，不是每個階段都需要 Claude 的推理能力：

| 工作流階段 | 需要什麼 | 適合的模型 |
|------------|---------|-----------|
| constitution / specify / plan / gate | 深度推理、架構設計 | ☁️ Claude |
| tasks / checklist / analyze / digest / export | 結構化轉換 | 🖥️ 本地模型 |
| implement（簡單） | boilerplate, CRUD, config | 🖥️ 本地模型 |
| implement（複雜） | auth, security, 核心邏輯 | ☁️ Claude |

**結果：約 50% 的任務可以在本地執行，省下 Claude API 額度。**

## 系統架構

```
Claude Code（Pro/Max 會員）
    │
    ├── 複雜任務 → Claude 自己處理（會員額度）
    │
    └── /local, /i18n, /docstring ...
         │
         └── Bash: ./scripts/call-omlx.sh
              │
              └── curl → oMLX (本地 Qwen3.5-9B)
```

**為什麼用 Bash+curl 而不是 MCP？**
- Claude Code UI 會顯示 `Bash(./scripts/call-omlx.sh ...)` — 與原生工具（Read/Write/Edit）視覺一致
- 不會有 MCP tool call 的折疊 JSON 割裂感
- 使用者全程看得到「在做什麼」

不需要 proxy，不需要額外 API key，不違反 Anthropic 條款。

> **Legacy**: 舊版 MCP server (`mcp_omlx.py`) 保留為 optional，安裝時可選擇是否註冊。

## 環境需求

- macOS + Apple Silicon（M1 以上）
- [oMLX](https://omlx.ai/) — 本地 LLM 推理伺服器
- [Claude Code](https://claude.com/claude-code) — Pro 或 Max 會員
- `curl` + `jq` — macOS 內建（`brew install jq` 若沒裝）
- Python 3.11+（僅 legacy MCP 需要）
- [uv](https://github.com/astral-sh/uv) — Python 套件管理（僅 legacy MCP 需要）

## 快速開始

### 1. 安裝 oMLX

從 [omlx.ai](https://omlx.ai/) 下載安裝，在 menu bar 啟動，載入一個模型（例如 Qwen3.5-9B-MLX-4bit）。

記下你的 oMLX API key（在 oMLX 設定裡可以找到）。

### 2. Clone 並一鍵安裝

```bash
git clone https://github.com/wewececetw/task-router.git
cd task-router
./install.sh
```

安裝腳本會自動完成：
- 安裝 Python 依賴（`uv sync`）
- 註冊 omlx-local MCP server（全域）
- 複製 slash commands 到 `~/.claude/commands/`（7 個本地模型工具：`/local`、`/i18n`、`/docstring`、`/migration`、`/test-stub`、`/changelog`、`/implement-simple`）
- 複製 `scripts/call-omlx.sh` helper 到全域位置
- 寫入全域 `~/.claude/CLAUDE.md` 自動路由規則（Spec Kit + local_llm）

**自動路由規則是核心：** 寫入後 Claude 在任何專案遇到 `/speckit.tasks`、`/speckit.analyze`、`/speckit.checklist`、翻譯 i18n、產 docstring 等輕量任務時，會自動委派給本地模型 — 不用你手動選。

### 3. 設定 Claude Desktop App（可選）

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

在任何專案裡開 Claude Code，**安裝後所有專案都自動生效**：

```bash
# 手動指定本地模型
/local 翻譯這段英文成中文

# Spec Kit 官方指令 — Claude 會依規則自動路由
/speckit.specify   # ☁️ Claude 處理（需推理）
/speckit.plan      # ☁️ Claude 處理（架構決策）
/speckit.tasks     # 🖥️ 自動委派給本地模型（省 token）
/speckit.analyze   # 🖥️ 自動委派給本地模型
/speckit.checklist # 🖥️ 自動委派給本地模型

# 輕量工具（一律走本地）
/i18n /docstring /migration /test-stub /changelog /implement-simple
```

**怎麼知道有沒有自動路由？** 看 Claude Code 的 tool call 列表 — 出現 `Bash(./scripts/call-omlx.sh ...)` 就代表有省到 token。

## 支援的工作流

### Spec Kit（預設）

[GitHub Spec Kit](https://github.com/github/spec-kit) 的 Spec-Driven Development 工作流：
constitution → specify → clarify → plan → tasks → implement → analyze → checklist

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
3. **不符規範 → exit code 5**，Claude 接手重做

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
| Fallback | 真的太大就回報，Claude 自己接手 |
| Thinking 過濾 | 自動關閉 Qwen3.5 思考模式 + 過濾 `<think>` 標籤 |
| macOS 通知 | 任務完成/失敗時彈系統通知，不用盯著等 |
| Progress feedback | 即時中英混合進度回饋（類似 Claude Code 體驗） |

## 可用的 MCP Tools

| Tool | 說明 |
|------|------|
| `local_llm` | 送 prompt 給本地模型，支援 system prompt |
| `local_llm_batch` | 批量送多個 prompt，適合一次處理多個小任務 |
| `local_llm_status` | 檢查 oMLX 伺服器狀態和可用模型 |

## 可用的 Slash Commands

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

這會啟動一個 proxy，自動根據工作流階段分流到 oMLX 或 Claude API。

## 授權

MIT

## 作者

Barron
