# Barron Memory

## Working Style

- Barron usually writes in Traditional Chinese and prefers direct, practical
  engineering updates.
- Keep responses concise, but do not skip important technical constraints.
- When the request implies code changes, inspect the repo first, then implement.
- If Barron mentions urgent real-world context, acknowledge briefly and keep the
  technical work moving unless he asks to pause.

## Engineering Preferences

- Favor Codex-native repo guidance: `AGENTS.md`, `.codex/config.toml`, and files
  under `.codex/prompts/`.
- Preserve existing user changes in the working tree. Do not revert dirty files
  unless Barron explicitly asks.
- Prefer local tools and deterministic scripts before network-dependent steps.
- For local model delegation, use `./scripts/call-omlx.sh` first; if it returns
  fallback or low-quality output, Codex should finish the task directly.

## Project Notes

- This repo is `task-router`, a Python 3.11+ project using `uv`, Typer, Rich,
  FastAPI, LiteLLM, MCP, and oMLX integration.
- The historical `.claude/commands/` files are legacy Claude slash-command
  prompts. Codex should use `.codex/prompts/` as the adapted guidance layer.
- Spec Kit lives in `.specify/`. Its agent-context updater should target
  `AGENTS.md` for Codex.
