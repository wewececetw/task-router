# Task Router Shared Routing Rules

These rules are shared by Codex and Claude Code profiles. Profile files may use
different command formats, but the routing intent must stay the same.

## Local oMLX Helper

Global helper path:

```bash
~/.task-router/scripts/call-omlx.sh
```

Project-local helper path has priority when available:

```bash
./scripts/call-omlx.sh
```

## Lightweight Task Routing

Use oMLX for:

- i18n translation and bilingual text transformation
- docstring, JSDoc, godoc, and type annotation drafts
- database migration drafts
- test skeletons
- boilerplate, CRUD, simple config, and scaffold tasks
- JSON/YAML/CSV/Markdown format conversion
- changelog drafts from git history or diff

Use the active agent directly for high-risk work: auth, security,
authorization, sessions, token handling, core business logic, algorithms,
concurrency, performance, data-loss risk, and any task where oMLX output is
malformed, unsafe, or low quality.

## Helper Selection

```bash
CALL_OMLX="./scripts/call-omlx.sh"
[ -x "$CALL_OMLX" ] || CALL_OMLX="$HOME/.task-router/scripts/call-omlx.sh"
"$CALL_OMLX" "你的 prompt"
```

## Fallback Rules

- Exit code `5`: preset validator failed; active agent must redo the output.
- Exit code `1`: oMLX is offline or connection refused; active agent must handle the task.
- Any other non-zero exit: active agent must handle the task.
- If output is logically wrong, malformed, or incomplete, active agent must handle the task.

Do not put raw API keys in shell commands. Use `OMLX_API_KEY` and
`OMLX_BASE_URL` environment variables.
