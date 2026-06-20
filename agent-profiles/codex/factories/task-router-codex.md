# Task Router Codex Factory

Use this factory for Task Router, Codex/Claude profile routing, selected spec
workflow routing, and oMLX helper usage.

## Codex Responsibilities

- Use the selected spec workflow as the source of truth.
- Keep Codex responsible for requirements, clarification, architecture,
  implementation judgment, and final review.
- Use oMLX only for selected lightweight drafts and validated structured phases.
- Review all oMLX output before applying code changes.
- If oMLX fails, validator output fails, or quality is insufficient, finish the
  task directly in Codex.

## GitHub Spec Kit Workflow

Use GitHub Spec Kit as the source of truth for SDD workflow when the user asks
for Spec Kit or the repo has `.specify/`. `.specify/` scripts/templates drive
the workflow; oMLX only accelerates selected simple outputs.

If the current repository does not have `.specify/`, initialize Spec Kit with
the selected agent profile:

```bash
specify init --here --ai <codex|claude> --offline
```

For existing Spec Kit projects, use repo-local scripts:

```bash
.specify/scripts/bash/create-new-feature.sh
.specify/scripts/bash/setup-plan.sh
.specify/scripts/bash/check-prerequisites.sh
.specify/scripts/bash/update-agent-context.sh <codex|claude>
```

The active agent owns requirements, planning, clarification, architecture,
implementation judgment, and final review.

## GitHub OpenSpec Workflow

Use Fission-AI/OpenSpec as the source of truth for lightweight SDD workflow when
the user asks for OpenSpec or the repo has `openspec/`. OpenSpec owns
`openspec/` artifacts and `/opsx:*` workflow commands.

Initialize an OpenSpec project from the project root:

```bash
openspec init
```

The default quick path is:

| Trigger | Purpose |
|---------|---------|
| `/opsx:propose <idea>` | Create `openspec/changes/<change>/` and planning artifacts |
| `/opsx:apply` | Implement tasks from the active change |
| `/opsx:archive` | Archive completed change and update specs |

Useful CLI commands:

```bash
openspec list
openspec status --change <change>
openspec instructions --change <change>
openspec instructions tasks --change <change>
openspec instructions apply --change <change>
openspec validate --all
openspec archive <change> --yes
openspec update
```

Do not mix Spec Kit and OpenSpec artifacts in the same feature unless the user
explicitly asks for a migration or bridge.

## Local oMLX Helper

Global helper path:

```bash
~/.task-router/scripts/call-omlx.sh
```

Project-local helper path has priority when available:

```bash
./scripts/call-omlx.sh
```

## oMLX Routing

For GitHub Spec Kit, the active agent should call oMLX for these structured
phases:

| Trigger | Command |
|---------|---------|
| `speckit.tasks` or "從 plan 產生 tasks" | `call-omlx.sh "$(cat plan.md)" --preset speckit-tasks` |
| `speckit.checklist` or "品質檢查清單" | `call-omlx.sh "$(cat spec.md plan.md)" --preset speckit-checklist` |
| `speckit.analyze` or "一致性檢查" | `call-omlx.sh "$(cat spec.md plan.md tasks.md)" --preset speckit-analyze` |

For GitHub OpenSpec, do not replace OpenSpec artifact workflow with oMLX. Until
dedicated OpenSpec presets and validators exist, do not route OpenSpec
`tasks.md`, `proposal.md`, `design.md`, or delta specs to oMLX automatically.

Use oMLX for lightweight supporting work:

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
- Exit code `1`: oMLX is offline or connection refused; active agent must handle
  the task.
- Any other non-zero exit: active agent must handle the task.
- If output is logically wrong, malformed, or incomplete, active agent must
  handle the task.

Do not put raw API keys in shell commands. Use `OMLX_API_KEY` and
`OMLX_BASE_URL` environment variables.
