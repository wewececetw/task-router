#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Task Router 一鍵安裝腳本
# 自動完成：註冊 MCP server + 複製 slash commands + 寫入全域 CLAUDE.md
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
COMMANDS_DIR="$CLAUDE_DIR/commands"

echo "🚀 Task Router 安裝腳本"
echo "========================"
echo ""

# ------------------------------------------------------------------
# 1. 檢查前置條件
# ------------------------------------------------------------------

echo "📋 檢查前置條件..."

if ! command -v claude &>/dev/null; then
    echo "❌ 找不到 claude CLI。請先安裝 Claude Code: https://claude.com/claude-code"
    exit 1
fi

if ! command -v uv &>/dev/null; then
    echo "❌ 找不到 uv。請先安裝: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ claude CLI 已安裝"
echo "✅ uv 已安裝"
echo ""

# ------------------------------------------------------------------
# 2. 安裝 Python 依賴
# ------------------------------------------------------------------

echo "📦 安裝 Python 依賴..."
uv sync --quiet
echo "✅ 依賴安裝完成"
echo ""

# ------------------------------------------------------------------
# 3. 取得 oMLX API key
# ------------------------------------------------------------------

if [ -z "${OMLX_API_KEY:-}" ]; then
    echo "🔑 請輸入你的 oMLX API key（在 oMLX app 設定裡可以找到）："
    read -r OMLX_API_KEY
    if [ -z "$OMLX_API_KEY" ]; then
        echo "⚠️  沒有輸入 API key，使用空值（部分 oMLX 設定不需要 key）"
        OMLX_API_KEY=""
    fi
fi

OMLX_BASE_URL="${OMLX_BASE_URL:-http://127.0.0.1:9000/v1}"
echo "✅ oMLX base URL: $OMLX_BASE_URL"
echo ""

# ------------------------------------------------------------------
# 4. 註冊 MCP server（可選 - legacy）
# ------------------------------------------------------------------

echo "🔌 MCP server 註冊（可選）"
echo "   新架構使用 Bash+curl 直接呼叫 oMLX，MCP server 僅作為 legacy/fallback 選項"
read -r -p "   是否要註冊 omlx-local MCP server？[y/N] " REGISTER_MCP

if [[ "$REGISTER_MCP" =~ ^[Yy]$ ]]; then
    claude mcp remove omlx-local -s user 2>/dev/null || true
    claude mcp add omlx-local -s user \
        -e OMLX_API_KEY="$OMLX_API_KEY" \
        -e OMLX_BASE_URL="$OMLX_BASE_URL" \
        -- uv run --directory "$SCRIPT_DIR" python mcp_omlx.py
    echo "   ✅ MCP server 已註冊（legacy mode）"
else
    echo "   ⏭️  跳過 MCP 註冊（使用 Bash+curl 即可）"
fi
echo ""

# ------------------------------------------------------------------
# 5. 複製 slash commands 到全域
# ------------------------------------------------------------------

echo "📝 安裝全域 slash commands..."
mkdir -p "$COMMANDS_DIR"

# 複製所有 commands，保留既有的非衝突檔案
cp "$SCRIPT_DIR/.claude/commands/"*.md "$COMMANDS_DIR/"

echo "✅ 已安裝以下 commands:"
for f in "$SCRIPT_DIR/.claude/commands/"*.md; do
    name=$(basename "$f" .md)
    echo "   /$name"
done
echo ""

# ------------------------------------------------------------------
# 6. 寫入全域 CLAUDE.md（Spec Kit + local_llm 自動路由規則）
# ------------------------------------------------------------------

echo "📄 設定全域 CLAUDE.md 路由規則..."

# 先清除舊版 vibe-lens section（如果有）
if [ -f "$CLAUDE_MD" ] && grep -q "# === Task Router: vibe-lens" "$CLAUDE_MD" 2>/dev/null; then
    echo "   🧹 移除舊版 vibe-lens 區塊..."
    sed -i '' '/# === Task Router: vibe-lens/,/# === End Task Router ===/d' "$CLAUDE_MD"
fi

# 清除舊版 Spec Kit section（重新安裝時覆蓋）
if [ -f "$CLAUDE_MD" ] && grep -q "# === Task Router: Spec Kit" "$CLAUDE_MD" 2>/dev/null; then
    echo "   🔄 覆蓋舊版 Spec Kit 路由規則..."
    sed -i '' '/# === Task Router: Spec Kit/,/# === End Task Router ===/d' "$CLAUDE_MD"
fi

# 確認 scripts/call-omlx.sh 可執行
if [ -f "$SCRIPT_DIR/scripts/call-omlx.sh" ]; then
    chmod +x "$SCRIPT_DIR/scripts/call-omlx.sh"
    echo "   ✅ scripts/call-omlx.sh 已確認可執行"
fi

# 寫入 OMLX_API_KEY 到 shell profile（如果尚未設定）
SHELL_PROFILE=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
fi

if [ -n "$SHELL_PROFILE" ] && [ -n "$OMLX_API_KEY" ]; then
    if ! grep -q "OMLX_API_KEY" "$SHELL_PROFILE" 2>/dev/null; then
        echo "" >> "$SHELL_PROFILE"
        echo "# Task Router: oMLX API key" >> "$SHELL_PROFILE"
        echo "export OMLX_API_KEY=\"$OMLX_API_KEY\"" >> "$SHELL_PROFILE"
        echo "export OMLX_BASE_URL=\"$OMLX_BASE_URL\"" >> "$SHELL_PROFILE"
        echo "   ✅ 已寫入 OMLX_API_KEY 到 $SHELL_PROFILE"
    fi
fi

# Append 新的路由規則
cat >> "$CLAUDE_MD" << 'RULES'

# === Task Router: Spec Kit + Bash+curl 自動路由 ===

## 強制路由規則

當使用者執行以下 Spec Kit slash commands 或等效自然語言請求時，你**必須**用 **Bash 執行 `./scripts/call-omlx.sh`**（或直接 curl 呼叫 oMLX），不可自己處理：

| 觸發條件 | 執行方式 |
|---------|---------|
| `/speckit.tasks` 或「拆解任務列表」「從 plan 產生 tasks」 | Bash `./scripts/call-omlx.sh "..."` 產生 tasks.md 內容 |
| `/speckit.analyze` 或「一致性檢查」「比對 spec/plan/tasks」 | Bash `./scripts/call-omlx.sh "..."` 做跨檔案比對 |
| `/speckit.checklist` 或「品質檢查清單」「requirements checklist」 | Bash `./scripts/call-omlx.sh "..."` 生成 checklist |
| `/speckit.taskstoissues` 或「任務轉 GitHub issues」 | Bash `./scripts/call-omlx.sh "..."` 轉換格式 |

**如果專案根目錄沒有 `./scripts/call-omlx.sh`**，改用直接 curl：

```bash
curl -s http://127.0.0.1:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OMLX_API_KEY" \
  -d '{"model":"Qwen3.5-9B-MLX-4bit","messages":[{"role":"user","content":"..."}],"max_tokens":4096,"chat_template_kwargs":{"enable_thinking":false}}' \
  | jq -r '.choices[0].message.content'
```

## 不委派的情況（由 Claude 直接處理）

| 觸發條件 | 原因 |
|---------|------|
| `/speckit.constitution` | 定義專案原則，需深度推理 |
| `/speckit.specify` | 理解使用者需求與 user stories |
| `/speckit.clarify` | 找出 spec 缺口需上下文理解 |
| `/speckit.plan` | 架構與設計決策 |
| `/speckit.implement` | 依任務複雜度：boilerplate/CRUD/config → call-omlx.sh；auth/security/核心邏輯 → Claude |

## 同樣委派給 call-omlx.sh 的輕量任務

（不限於 Spec Kit，任何時候遇到都該路由）

- 翻譯 i18n 字串 / 雙語對照
- 生成 docstring / JSDoc / 型別註解
- 生成 DB migration
- 生成測試骨架（test stubs）
- 格式轉換（JSON ↔ YAML、CSV → Markdown table）
- 從 git diff 生成 changelog
- 簡單問答、boilerplate、scaffold

## Fallback 規則

- 若 `call-omlx.sh` 回傳 `❌ oMLX FALLBACK` 或 exit code != 0 → 你接手自己處理
- 若 curl 顯示 connection refused（oMLX 離線）→ 你接手自己處理
- 若本地模型產出品質明顯不夠（邏輯錯誤、格式破損）→ 你重做

## 執行注意事項

- `OMLX_API_KEY` 環境變數必須已設定（install.sh 會處理或寫入 shell profile）
- 呼叫時 API key 用 `$OMLX_API_KEY` 變數展開，**不要把實際 key 寫進 Bash 指令**
- `./scripts/call-omlx.sh` 會自動記錄使用情況到 `~/.task-router/usage.log`

# === End Task Router ===
RULES

echo "✅ 全域 CLAUDE.md 路由規則已寫入"
echo ""

# ------------------------------------------------------------------
# 完成
# ------------------------------------------------------------------

echo "==============================="
echo "🎉 安裝完成！"
echo "==============================="
echo ""
echo "使用方式："
echo "  在任何專案開 claude，即可使用："
echo "  • /local 翻譯 hello world         — 直接丟給本地模型"
echo "  • /speckit.tasks                  — Spec Kit 拆任務（自動路由本地模型）"
echo "  • /speckit.analyze                — Spec Kit 一致性檢查"
echo "  • /speckit.checklist              — Spec Kit 品質清單"
echo ""
echo "⚠️  記得先啟動 oMLX app 並載入模型！"
echo ""
