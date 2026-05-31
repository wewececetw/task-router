# Task Router Shared Routing Rules

These rules are shared by Codex and Claude Code profiles. Profile files may use
different command formats, but the routing intent must stay the same.

## GitHub Spec Kit Is The Primary Workflow

When the user asks for Spec Kit, use GitHub Spec Kit project files and scripts
first. oMLX is only an execution optimization for selected simple outputs.

If the current repository does not have `.specify/`, initialize Spec Kit with
the selected agent profile:

```bash
specify init --here --ai <codex|claude> --offline
```

For existing Spec Kit projects, use the repo-local scripts:

```bash
.specify/scripts/bash/create-new-feature.sh
.specify/scripts/bash/setup-plan.sh
.specify/scripts/bash/check-prerequisites.sh
.specify/scripts/bash/update-agent-context.sh <codex|claude>
```

The active agent should own requirements, planning, clarification, architecture,
implementation judgment, and final review. oMLX should not replace the Spec Kit
workflow.

## Local oMLX Helper

Global helper path:

```bash
~/.task-router/scripts/call-omlx.sh
```

Project-local helper path has priority when available:

```bash
./scripts/call-omlx.sh
```

## oMLX Routing Inside Spec Kit

The active agent should call oMLX for these structured Spec Kit phases:

| Trigger | Command |
|---------|---------|
| `speckit.tasks` or "從 plan 產生 tasks" | `call-omlx.sh "$(cat plan.md)" --preset speckit-tasks` |
| `speckit.checklist` or "品質檢查清單" | `call-omlx.sh "$(cat spec.md plan.md)" --preset speckit-checklist` |
| `speckit.analyze` or "一致性檢查" | `call-omlx.sh "$(cat spec.md plan.md tasks.md)" --preset speckit-analyze` |

## Lightweight Task Routing

Use oMLX for:

- i18n translation and bilingual text transformation
- docstring, JSDoc, godoc, and type annotation drafts
- database migration drafts
- test skeletons
- boilerplate, CRUD, simple config, and scaffold tasks
- JSON/YAML/CSV/Markdown format conversion
- changelog drafts from git history or diff

Use the active agent directly for:

- `speckit.constitution`
- `speckit.specify`
- `speckit.clarify`
- `speckit.plan`
- auth, security, authorization, sessions, and token handling
- core business logic, algorithms, concurrency, performance, and data-loss risk
- any task where oMLX output is malformed, unsafe, or low quality

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
