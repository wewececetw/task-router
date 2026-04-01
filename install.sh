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
# 6. 寫入全域 CLAUDE.md（vibe-lens + local_llm 路由規則）
# ------------------------------------------------------------------

echo "📄 設定全域 CLAUDE.md..."

# 定義要加入的 section 標記
MARKER="# === Task Router: vibe-lens + local_llm 路由規則 ==="
MARKER_END="# === End Task Router ==="

# 如果已經有舊的 section，先移除
if [ -f "$CLAUDE_MD" ]; then
    # 用 sed 移除舊的 section
    if grep -q "$MARKER" "$CLAUDE_MD" 2>/dev/null; then
        sed -i '' "/$MARKER/,/$MARKER_END/d" "$CLAUDE_MD"
        echo "   (移除舊的 Task Router section)"
    fi
fi

# Append 新的 section
cat >> "$CLAUDE_MD" << 'RULES'

# === Task Router: vibe-lens + local_llm 路由規則 ===

## vibe-lens + local_llm 整合

當使用 vibe-lens (sdd_*) MCP tools 時，必須遵循以下路由規則：

### Local 階段 — 先呼叫 vibe-lens，再用 local_llm 後處理

| vibe-lens tool | local_llm 後處理 |
|----------------|-----------------|
| `sdd_tasks` | 加時間估算、格式化、標記可平行任務 |
| `sdd_analyze` | 加嚴重度 (P0/P1/P2)、翻譯成雙語 |
| `sdd_checklist` | 擴展成可執行的測試場景 |
| `sdd_digest` | 翻譯成雙語對照 |
| `sdd_export` | 調整為 stakeholder 友好格式 |
| `sdd_review_artifact` | 展開建議成具體改善步驟 |

後處理 prompt 格式：
```
你是 SDD 工作流助手。以下是 vibe-lens 的 {階段名} 產出。
請做以下加工：{對應的後處理內容}

原始產出：
{vibe-lens 的輸出}
```

### Cloud 階段 — 只呼叫 vibe-lens，不用 local_llm

`sdd_constitution`, `sdd_specify`, `sdd_clarify`, `sdd_plan`, `sdd_gate`
這些需要深度推理，由 Claude 直接處理。

### 工具類 — 直接回覆

`sdd_status`, `sdd_guide`, `sdd_task_next`, `sdd_task_done`, `sdd_learn`, `sdd_explain`

### Fallback

- 如果 local_llm 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果
- 簡單實作任務（boilerplate, CRUD, config）用 local_llm
- 複雜任務（auth, security, 核心邏輯）由 Claude 處理

# === End Task Router ===
RULES

echo "✅ 全域 CLAUDE.md 已更新"
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
echo "  • /sdd tasks user-auth    — vibe-lens 拆任務 + local_llm 加工"
echo "  • /sdd plan user-auth     — vibe-lens 規劃（Claude 處理）"
echo "  • /local 翻譯 hello world — 直接丟給本地模型"
echo "  • /tasks feature-name     — 拆解任務列表"
echo ""
echo "⚠️  記得先啟動 oMLX app 並載入模型！"
echo ""
