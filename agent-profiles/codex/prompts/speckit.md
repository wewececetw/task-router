# Spec Kit With Codex

Use GitHub Spec Kit as the source of truth for SDD workflow. `.specify/`
scripts/templates drive the workflow; oMLX only accelerates selected simple
outputs.

If `.specify/` is missing, initialize Codex support first:

```bash
specify init --here --ai codex --offline
```

For existing Spec Kit projects, prefer repo-local scripts:

```bash
.specify/scripts/bash/create-new-feature.sh
.specify/scripts/bash/setup-plan.sh
.specify/scripts/bash/check-prerequisites.sh
.specify/scripts/bash/update-agent-context.sh codex
```

Codex must follow the same Task Router routing semantics as the Claude Code
profile:

- `speckit.constitution`, `speckit.specify`, `speckit.clarify`, and
  `speckit.plan`: Codex handles directly.
- `speckit.tasks`: call `call-omlx.sh --preset speckit-tasks`.
- `speckit.checklist`: call `call-omlx.sh --preset speckit-checklist`.
- `speckit.analyze`: call `call-omlx.sh --preset speckit-analyze`.
- Simple implementation drafts may call oMLX.
- Auth, security, core logic, concurrency, and high-risk changes stay with
  Codex.

If oMLX is offline, a validator fails, or output quality is insufficient, Codex
finishes the task directly.
