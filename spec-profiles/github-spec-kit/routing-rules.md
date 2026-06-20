# GitHub Spec Kit Workflow

Use GitHub Spec Kit as the source of truth for SDD workflow. `.specify/`
scripts/templates drive the workflow; oMLX only accelerates selected simple
outputs.

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

## oMLX Routing Inside GitHub Spec Kit

The active agent should call oMLX for these structured Spec Kit phases:

| Trigger | Command |
|---------|---------|
| `speckit.tasks` or "從 plan 產生 tasks" | `call-omlx.sh "$(cat plan.md)" --preset speckit-tasks` |
| `speckit.checklist` or "品質檢查清單" | `call-omlx.sh "$(cat spec.md plan.md)" --preset speckit-checklist` |
| `speckit.analyze` or "一致性檢查" | `call-omlx.sh "$(cat spec.md plan.md tasks.md)" --preset speckit-analyze` |

Use the active agent directly for:

- `speckit.constitution`
- `speckit.specify`
- `speckit.clarify`
- `speckit.plan`
- auth, security, authorization, sessions, and token handling
- core business logic, algorithms, concurrency, performance, and data-loss risk
- any task where oMLX output is malformed, unsafe, or low quality
