#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Task Router installer
# Supports selectable agent profiles: Codex, Claude Code, or both.
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GLOBAL_SCRIPTS_DIR="$HOME/.task-router/scripts"
SHARED_RULES="$SCRIPT_DIR/agent-profiles/shared/routing-rules.md"
CODEX_TEMPLATE="$SCRIPT_DIR/agent-profiles/codex/AGENTS.md.template"
CODEX_PROMPTS_DIR="$SCRIPT_DIR/agent-profiles/codex/prompts"
CLAUDE_TEMPLATE="$SCRIPT_DIR/agent-profiles/claude/CLAUDE.md.template"
CLAUDE_COMMANDS_DIR="$SCRIPT_DIR/.claude/commands"

CODEX_DIR="$HOME/.codex"
CODEX_AGENTS="$CODEX_DIR/AGENTS.md"
CODEX_PROMPTS_TARGET="$CODEX_DIR/prompts/task-router"

CLAUDE_DIR="$HOME/.claude"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
CLAUDE_COMMANDS_TARGET="$CLAUDE_DIR/commands"

AGENT="both"
DRY_RUN=false
FORCE=false
REGISTER_MCP="N"

usage() {
    cat << USAGE
Usage: ./install.sh [--agent codex|claude|both] [--dry-run] [--force]

Options:
  --agent      Agent profile to install. Default: both
  --dry-run    Print planned writes without changing files
  --force      Continue past missing optional agent CLIs
  -h, --help   Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent)
            AGENT="${2:-}"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

case "$AGENT" in
    codex|claude|both) ;;
    *)
        echo "Invalid --agent value: $AGENT" >&2
        echo "Supported values: codex, claude, both" >&2
        exit 2
        ;;
esac

includes_agent() {
    local wanted="$1"
    [[ "$AGENT" == "$wanted" || "$AGENT" == "both" ]]
}

say_step() {
    echo ""
    echo "$1"
}

ensure_dir() {
    local dir="$1"
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: mkdir -p $dir"
    else
        mkdir -p "$dir"
    fi
}

render_template() {
    local template="$1"
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" == "{{SHARED_ROUTING_RULES}}" ]]; then
            cat "$SHARED_RULES"
        else
            printf '%s\n' "$line"
        fi
    done < "$template"
}

write_managed_section() {
    local target="$1"
    local title="$2"
    local rendered="$3"
    local start="# === Task Router: ${title} ==="
    local end="# === End Task Router ==="

    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: update managed section in $target"
        echo "         start: $start"
        echo "         source: rendered profile template + shared routing rules"
        return
    fi

    ensure_dir "$(dirname "$target")"

    local start_count=0
    local end_count=0
    if [[ -f "$target" ]]; then
        start_count=$(grep -c '^# === Task Router:' "$target" 2>/dev/null || true)
        end_count=$(grep -c '^# === End Task Router ===$' "$target" 2>/dev/null || true)
    fi
    if [[ "$start_count" != "$end_count" ]]; then
        echo "Malformed Task Router managed section in $target; leaving file unchanged." >&2
        exit 1
    fi

    local tmp
    tmp="$(mktemp)"
    if [[ -f "$target" ]]; then
        awk '
            /^# === Task Router:/ { skip = 1; next }
            /^# === End Task Router ===$/ { skip = 0; next }
            !skip { print }
        ' "$target" > "$tmp"
    fi

    {
        if [[ -s "$tmp" ]]; then
            cat "$tmp"
            printf '\n'
        fi
        printf '%s\n\n' "$start"
        cat "$rendered"
        printf '\n%s\n' "$end"
    } > "$target"

    rm -f "$tmp"
}

copy_shared_scripts() {
    say_step "📂 Installing shared oMLX helper scripts..."
    ensure_dir "$GLOBAL_SCRIPTS_DIR/presets"
    ensure_dir "$GLOBAL_SCRIPTS_DIR/validators"

    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: copy scripts/call-omlx.sh to $GLOBAL_SCRIPTS_DIR/"
        echo "DRY-RUN: copy scripts/usage-stats.sh to $GLOBAL_SCRIPTS_DIR/ if present"
        echo "DRY-RUN: copy scripts/presets/*.md to $GLOBAL_SCRIPTS_DIR/presets/"
        echo "DRY-RUN: copy scripts/validators/*.sh to $GLOBAL_SCRIPTS_DIR/validators/"
        return
    fi

    cp "$SCRIPT_DIR/scripts/call-omlx.sh" "$GLOBAL_SCRIPTS_DIR/"
    cp "$SCRIPT_DIR/scripts/usage-stats.sh" "$GLOBAL_SCRIPTS_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/scripts/presets/"*.md "$GLOBAL_SCRIPTS_DIR/presets/" 2>/dev/null || true
    cp "$SCRIPT_DIR/scripts/validators/"*.sh "$GLOBAL_SCRIPTS_DIR/validators/" 2>/dev/null || true
    chmod +x "$GLOBAL_SCRIPTS_DIR/call-omlx.sh" "$GLOBAL_SCRIPTS_DIR/validators/"*.sh 2>/dev/null || true
    echo "✅ Shared scripts installed"
}

write_shell_profile_env() {
    local shell_profile=""
    if [[ -f "$HOME/.zshrc" ]]; then
        shell_profile="$HOME/.zshrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
        shell_profile="$HOME/.bash_profile"
    fi

    if [[ -z "$shell_profile" || -z "${OMLX_API_KEY:-}" ]]; then
        return
    fi

    if grep -q "OMLX_API_KEY" "$shell_profile" 2>/dev/null; then
        return
    fi

    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: append OMLX_API_KEY and OMLX_BASE_URL to $shell_profile"
        return
    fi

    {
        echo ""
        echo "# Task Router: oMLX API key"
        echo "export OMLX_API_KEY=\"$OMLX_API_KEY\""
        echo "export OMLX_BASE_URL=\"$OMLX_BASE_URL\""
    } >> "$shell_profile"
    echo "✅ Wrote OMLX environment to $shell_profile"
}

install_codex_profile() {
    say_step "🧭 Installing Codex profile..."
    local rendered
    rendered="$(mktemp)"
    render_template "$CODEX_TEMPLATE" > "$rendered"
    write_managed_section "$CODEX_AGENTS" "Codex Profile" "$rendered"
    rm -f "$rendered"

    ensure_dir "$CODEX_PROMPTS_TARGET"
    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: copy $CODEX_PROMPTS_DIR/*.md to $CODEX_PROMPTS_TARGET/"
    else
        cp "$CODEX_PROMPTS_DIR/"*.md "$CODEX_PROMPTS_TARGET/"
        echo "✅ Codex profile installed"
    fi
}

install_claude_profile() {
    say_step "📝 Installing Claude Code profile..."
    ensure_dir "$CLAUDE_COMMANDS_TARGET"

    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: copy $CLAUDE_COMMANDS_DIR/*.md to $CLAUDE_COMMANDS_TARGET/"
    else
        cp "$CLAUDE_COMMANDS_DIR/"*.md "$CLAUDE_COMMANDS_TARGET/"
        echo "✅ Claude slash commands installed"
    fi

    local rendered
    rendered="$(mktemp)"
    render_template "$CLAUDE_TEMPLATE" > "$rendered"
    write_managed_section "$CLAUDE_MD" "Claude Code Profile" "$rendered"
    rm -f "$rendered"
}

maybe_register_claude_mcp() {
    if ! includes_agent claude; then
        return
    fi

    if ! command -v claude >/dev/null 2>&1; then
        echo "⚠️  claude CLI not found; skipping optional MCP registration"
        return
    fi

    if [[ "$DRY_RUN" == true ]]; then
        echo "DRY-RUN: optional Claude MCP registration would be offered"
        return
    fi

    echo ""
    echo "🔌 Claude MCP server registration is optional."
    echo "   Bash/curl helper is the default path; MCP is legacy/fallback."
    read -r -p "   Register omlx-local MCP server for Claude Code? [y/N] " REGISTER_MCP

    if [[ "$REGISTER_MCP" =~ ^[Yy]$ ]]; then
        claude mcp remove omlx-local -s user 2>/dev/null || true
        claude mcp add omlx-local -s user \
            -e OMLX_API_KEY="$OMLX_API_KEY" \
            -e OMLX_BASE_URL="$OMLX_BASE_URL" \
            -- uv run --directory "$SCRIPT_DIR" python mcp_omlx.py
        echo "✅ Claude MCP server registered"
    else
        echo "⏭️  Skipped Claude MCP registration"
    fi
}

print_plan() {
    echo "Selected agent profile: $AGENT"
    echo "Dry run: $DRY_RUN"
    echo ""
    echo "Shared writes:"
    echo "  - $GLOBAL_SCRIPTS_DIR/call-omlx.sh"
    echo "  - $GLOBAL_SCRIPTS_DIR/presets/*.md"
    echo "  - $GLOBAL_SCRIPTS_DIR/validators/*.sh"

    if includes_agent codex; then
        echo ""
        echo "Codex writes:"
        echo "  - $CODEX_AGENTS managed section"
        echo "  - $CODEX_PROMPTS_TARGET/*.md"
    fi

    if includes_agent claude; then
        echo ""
        echo "Claude Code writes:"
        echo "  - $CLAUDE_MD managed section"
        echo "  - $CLAUDE_COMMANDS_TARGET/*.md"
        echo "  - optional claude mcp registration"
    fi
}

echo "🚀 Task Router installer"
echo "========================"
print_plan

say_step "📋 Checking prerequisites..."

if ! command -v uv >/dev/null 2>&1; then
    echo "❌ uv is required. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
fi
echo "✅ uv found"

if includes_agent codex && ! command -v codex >/dev/null 2>&1; then
    echo "⚠️  codex CLI not found; file-based Codex guidance can still be installed"
fi

if includes_agent claude && ! command -v claude >/dev/null 2>&1; then
    echo "⚠️  claude CLI not found; slash-command files can still be installed, MCP registration will be skipped"
fi

if [[ "$DRY_RUN" == false ]]; then
    say_step "📦 Installing Python dependencies..."
    uv sync --quiet
    echo "✅ Dependencies installed"
fi

if [[ -z "${OMLX_API_KEY:-}" && "$DRY_RUN" == false ]]; then
    say_step "🔑 oMLX API key"
    read -r -p "Enter oMLX API key (leave blank if your oMLX setup does not require one): " OMLX_API_KEY
fi

OMLX_API_KEY="${OMLX_API_KEY:-}"
OMLX_BASE_URL="${OMLX_BASE_URL:-http://127.0.0.1:9000/v1}"
echo "✅ oMLX base URL: $OMLX_BASE_URL"

copy_shared_scripts
write_shell_profile_env

if includes_agent codex; then
    install_codex_profile
fi

if includes_agent claude; then
    install_claude_profile
fi

maybe_register_claude_mcp

echo ""
echo "==============================="
if [[ "$DRY_RUN" == true ]]; then
    echo "✅ Dry run complete. No files were changed."
else
    echo "🎉 Installation complete."
fi
echo "==============================="
echo ""
echo "Next steps:"
if includes_agent codex; then
    echo "  - Codex: restart/open Codex in a project and follow Task Router guidance."
fi
if includes_agent claude; then
    echo "  - Claude Code: open claude and use /local, /speckit.tasks, /speckit.analyze, /speckit.checklist."
fi
echo "  - Start oMLX and load your local model before routing local tasks."
