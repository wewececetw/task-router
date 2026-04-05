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
# 4. 註冊 MCP server（全域）
# ------------------------------------------------------------------

echo "🔌 註冊 omlx-local MCP server..."

# 先移除舊的（如果有）
claude mcp remove omlx-local -s user 2>/dev/null || true

claude mcp add omlx-local -s user \
    -e OMLX_API_KEY="$OMLX_API_KEY" \
    -e OMLX_BASE_URL="$OMLX_BASE_URL" \
    -- uv run --directory "$SCRIPT_DIR" python mcp_omlx.py

echo "✅ MCP server 已註冊"
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
# 6. 清除舊版 vibe-lens section（如果有）
# ------------------------------------------------------------------

if [ -f "$CLAUDE_MD" ] && grep -q "# === Task Router: vibe-lens" "$CLAUDE_MD" 2>/dev/null; then
    echo "🧹 偵測到舊版 vibe-lens 區塊，自動清除..."
    sed -i '' '/# === Task Router: vibe-lens/,/# === End Task Router ===/d' "$CLAUDE_MD"
    echo "✅ 已清除"
    echo ""
fi

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
echo "  • /speckit-tasks feature-name     — Spec Kit 拆任務"
echo "  • /speckit-analyze feature-name   — Spec Kit 一致性檢查"
echo "  • /speckit-checklist feature-name — Spec Kit 品質清單"
echo ""
echo "⚠️  記得先啟動 oMLX app 並載入模型！"
echo ""
