# Spec Kit Task Router

Spec Kit 工作流的智慧任務分流系統 — 簡單任務交給本地模型 (oMLX)，複雜任務留給 Claude。

## 為什麼需要這個？

用 Spec Kit 做開發時，不是每個階段都需要 Claude 的推理能力：

| Spec Kit 階段 | 需要什麼 | 適合的模型 |
|---------------|---------|-----------|
| constitution / specify / plan | 深度推理、架構設計 | ☁️ Claude |
| tasks / checklist / analyze | 結構化轉換 | 🖥️ 本地模型 |
| implement（簡單） | boilerplate, CRUD, config | 🖥️ 本地模型 |
| implement（複雜） | auth, security, 核心邏輯 | ☁️ Claude |

**結果：約 50% 的任務可以在本地執行，省下 Claude API 額度。**

## 系統架構

```
Claude Code（Pro/Max 會員）
    │
    ├── 複雜任務 → Claude 自己處理（會員額度）
    │
    └── /local, /speckit-tasks, /speckit-checklist ...
         │
         └── MCP tool: local_llm
              │
              └── oMLX (本地 Qwen3.5-9B)
```

不需要 proxy，不需要額外 API key，不違反 Anthropic 條款。

## 環境需求

- macOS + Apple Silicon（M1 以上）
- [oMLX](https://omlx.ai/) — 本地 LLM 推理伺服器
- [Claude Code](https://claude.com/claude-code) — Pro 或 Max 會員
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) — Python 套件管理

## 快速開始

### 1. 安裝 oMLX

從 [omlx.ai](https://omlx.ai/) 下載安裝，在 menu bar 啟動，載入一個模型（例如 Qwen3.5-9B-MLX-4bit）。

記下你的 oMLX port 和 API key（在 oMLX 設定裡可以找到）。

### 2. Clone 並安裝

```bash
git clone https://github.com/wewececetw/task-router.git
cd task-router
uv sync
```

### 3. 註冊 MCP server（全域）

```bash
claude mcp add omlx-local -s user \
  -e OMLX_API_KEY="你的-omlx-key" \
  -e OMLX_BASE_URL="http://127.0.0.1:9000/v1" \
  -- uv run --directory $(pwd) python mcp_omlx.py
```

### 4. 設定 Claude Desktop App（可選）

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

### 5. 安裝全域 commands

```bash
mkdir -p ~/.claude/commands
cp .claude/commands/*.md ~/.claude/commands/
```

### 6. 開始使用

在任何專案裡開 Claude Code：

```bash
# 把任務丟給本地模型
/local 翻譯這段英文成中文

# Spec Kit 工作流
/speckit-tasks        # 用本地模型拆解任務列表
/speckit-checklist    # 用本地模型生成品質檢查清單
/speckit-implement-simple  # 用本地模型寫簡單程式碼
```

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
| `/speckit-tasks` | 從 plan.md 生成任務列表 | 🖥️ oMLX |
| `/speckit-checklist` | 生成品質檢查清單 | 🖥️ oMLX |
| `/speckit-implement-simple` | 實作簡單任務（boilerplate, CRUD, config） | 🖥️ oMLX |
| `/speckit-analyze` | 檢查 spec/plan/tasks 一致性 | 🖥️ oMLX |
| `/speckit-docstring` | 為程式碼加 docstring/JSDoc | 🖥️ oMLX |
| `/speckit-test-stub` | 生成測試骨架 | 🖥️ oMLX |
| `/speckit-migration` | 生成 DB migration | 🖥️ oMLX |
| `/speckit-i18n` | 翻譯 i18n 字串檔 | 🖥️ oMLX |
| `/speckit-changelog` | 從 git diff 生成 changelog | 🖥️ oMLX |

## CLI 工具（額外功能）

除了 MCP，專案也包含獨立的 CLI 路由器：

```bash
# 查看 Spec Kit 階段路由表
uv run task-router speckit-route

# 分析 tasks.md 裡每個任務的路由
uv run task-router speckit-route examples/sample-tasks.md

# 直接路由並執行任務
OMLX_API_KEY=xxx uv run task-router ask "翻譯 hello world" --phase tasks -v
```

### 路由表範例

```
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Phase        ┃ Backend ┃ Reason                                    ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ constitution │ cloud   │ 定義專案原則 — 需要深度推理                │
│ specify      │ cloud   │ 需求分析需要理解使用者故事                │
│ plan         │ cloud   │ 架構決策需要強推理能力                    │
│ tasks        │ local   │ 結構化轉換，從 plan 拆解任務              │
│ implement    │ auto    │ 依個別任務複雜度決定                      │
│ analyze      │ local   │ 一致性檢查是模式匹配工作                  │
│ checklist    │ local   │ 結構化輸出                                │
└──────────────┴─────────┴───────────────────────────────────────────┘
```

### 任務分析範例

```
Summary: 12 local (oMLX) | 11 cloud (Claude) | 23 total
52% of tasks can run locally — saving API cost 💰
```

## LiteLLM Proxy（替代方案）

如果你有 Anthropic API key，也可以用 LiteLLM proxy 模式：

```bash
OMLX_API_KEY=xxx ANTHROPIC_API_KEY=xxx python speckit_router.py --port 4000
```

這會啟動一個 proxy，自動根據 Spec Kit 階段分流到 oMLX 或 Claude API。

## 開發經過

### 問題

用 Spec Kit + Claude Code 做開發時，所有任務都送 Claude API — 但很多簡單任務（拆任務、寫 boilerplate、生成 checklist）其實不需要 Claude 等級的推理能力。

### 探索過的方案

1. **自建 task-router CLI** — 可以分類任務，但無法攔截 Claude Code 的請求
2. **LiteLLM proxy** — 可以做路由，但 Pro/Max OAuth token 不能用在第三方工具（違反條款）
3. **現有 LLM router 套件**（RouteLLM, LLMRouter, ClawRouter）— 都不理解 Spec Kit 工作流
4. **MCP server + Claude Code commands** ✅ — 最終方案

### 為什麼選 MCP

- MCP 在 Claude Code 內部執行，不算第三方工具
- 不需要 API key，不違反 Anthropic 條款
- Claude Code 的 slash commands 可以指示 Claude 什麼時候用 local_llm
- 完全透明 — Claude 看到本地模型的回覆後可以自行修正品質

## 授權

MIT

## 作者

Barron
