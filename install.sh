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
GLOBAL_SCRIPTS_DIR="$HOME/.task-router/scripts"

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

# 複製 scripts/ 整包（含 presets + validators）到全域
echo "📂 複製 scripts/ (call-omlx.sh + presets + validators) 到 $GLOBAL_SCRIPTS_DIR..."
mkdir -p "$GLOBAL_SCRIPTS_DIR/presets" "$GLOBAL_SCRIPTS_DIR/validators"
cp "$SCRIPT_DIR/scripts/call-omlx.sh" "$GLOBAL_SCRIPTS_DIR/"
cp "$SCRIPT_DIR/scripts/usage-stats.sh" "$GLOBAL_SCRIPTS_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/presets/"*.md "$GLOBAL_SCRIPTS_DIR/presets/" 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/validators/"*.sh "$GLOBAL_SCRIPTS_DIR/validators/" 2>/dev/null || true
chmod +x "$GLOBAL_SCRIPTS_DIR/call-omlx.sh" "$GLOBAL_SCRIPTS_DIR/validators/"*.sh 2>/dev/null || true
echo "   ✅ 全域 scripts 已安裝（$(ls "$GLOBAL_SCRIPTS_DIR/presets/" 2>/dev/null | wc -l | tr -d ' ') presets, $(ls "$GLOBAL_SCRIPTS_DIR/validators/" 2>/dev/null | wc -l | tr -d ' ') validators）"

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

全域 helper 位於 `~/.task-router/scripts/call-omlx.sh`（由 install.sh 部署）。
專案若自帶 `./scripts/call-omlx.sh` 優先用專案版本。

## 強制路由規則 — 使用 preset（有 validator 守門）

以下任務**必須**用 `call-omlx.sh --preset <name>` 執行，Spec Kit 格式由 validator 保證合規：

| 觸發條件 | 指令 |
|---------|------|
| `/speckit.tasks` 或「從 plan 產生 tasks」 | `call-omlx.sh "$(cat plan.md)" --preset speckit-tasks` |
| `/speckit.checklist` 或「品質檢查清單」 | `call-omlx.sh "$(cat spec.md plan.md)" --preset speckit-checklist` |
| `/speckit.analyze` 或「一致性檢查」 | `call-omlx.sh "$(cat spec.md plan.md tasks.md)" --preset speckit-analyze` |

**Fallback**：若 exit code = 5（preset 驗證失敗）→ 產出不符 Spec Kit 規範，你接手重做。

## 強制路由規則 — 輕量任務（無 preset）

```bash
# 專案若有 ./scripts/call-omlx.sh 用專案版，否則用全域
CALL_OMLX="./scripts/call-omlx.sh"
[ -x "$CALL_OMLX" ] || CALL_OMLX="$HOME/.task-router/scripts/call-omlx.sh"
"$CALL_OMLX" "你的 prompt"
```

適用場景：
- 翻譯 i18n 字串 / 雙語對照
- 生成 docstring / JSDoc / 型別註解
- 生成 DB migration / 測試骨架 / boilerplate
- 格式轉換（JSON ↔ YAML、CSV → Markdown table）
- 從 git diff 生成 changelog

**Fallback**：若 `~/.task-router/scripts/call-omlx.sh` 也不存在，改用直接 curl：

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
| `/speckit.implement` | 依複雜度：boilerplate/CRUD/config → call-omlx.sh；auth/security/核心邏輯 → Claude |

## 通用 Fallback 規則

- exit code = 5 → preset validator 失敗，你接手重做
- exit code = 1 → oMLX 離線或 connection refused，你接手
- exit code != 0（其他）→ 你接手處理
- 本地模型產出品質明顯不夠（邏輯錯誤、格式破損）→ 你重做

## 執行注意事項

- `OMLX_API_KEY` 環境變數必須已設定（install.sh 會寫入 shell profile）
- 呼叫時 API key 用 `$OMLX_API_KEY` 變數展開，**不要把實際 key 寫進 Bash 指令**
- call-omlx.sh 會自動記錄使用情況到 `~/.task-router/usage.log`

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
echo "  • /speckit.tasks                  — Spec Kit 拆任務（含 preset+validator 守門）"
echo "  • /speckit.analyze                — Spec Kit 一致性檢查"
echo "  • /speckit.checklist              — Spec Kit 品質清單"
echo ""
echo "全域工具路徑："
echo "  ~/.task-router/scripts/call-omlx.sh              — 主 helper"
echo "  ~/.task-router/scripts/presets/*.md              — few-shot system prompts"
echo "  ~/.task-router/scripts/validators/*.sh           — Spec Kit 規範驗證器"
echo ""
echo "⚠️  記得先啟動 oMLX app 並載入模型！"
echo ""
