# Agent Instructions

Read and follow `BARRON_MEMORY.md` before making changes in this repository.

This project is now configured for Codex. Treat Claude-specific files under `.claude/`
as legacy source material only; prefer the Codex guidance in `.codex/` and this
file when instructions conflict.

## Project Defaults

- Use `uv` for Python dependency and command execution.
- Prefer `rg` for searching and `apply_patch` for manual edits.
- Keep changes scoped; do not rewrite unrelated Claude legacy files unless asked.
- Route lightweight local-model tasks through `./scripts/call-omlx.sh` or the
  configured `omlx-local` MCP tools.
- Let Codex handle complex reasoning, architecture, security, and final review.

## Useful Commands

- `uv run task-router --help`
- `uv run task-router phases --workflow speckit`
- `./scripts/call-omlx.sh "任務內容"`
- `.specify/scripts/bash/update-agent-context.sh codex`
