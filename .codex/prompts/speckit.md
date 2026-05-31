# Spec Kit With Codex

Use GitHub Spec Kit as the source of truth for SDD workflow. `.specify/`
scripts/templates drive the workflow; oMLX only accelerates selected simple
outputs. Codex should match the legacy Claude Code routing rules for shared Task
Router categories; only the guidance format differs.

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

## Responsibility Split

- Codex handles `constitution`, `specify`, `clarify`, `plan`, review,
  security-sensitive logic, and ambiguous product decisions.
- The local model handles `tasks`, `checklist`, `analyze`, summaries, and
  repetitive transformations through `./scripts/call-omlx.sh`.
- Simple implementation tasks such as boilerplate, CRUD, config, docstrings,
  migration drafts, and test stubs may call oMLX.
- Complex implementation tasks such as auth, security, core logic, concurrency,
  and data-loss risk stay with Codex.
- If a preset validator fails, Codex fixes the output directly.

## Commands

- Create or update Codex agent context:
  `.specify/scripts/bash/update-agent-context.sh codex`
- Generate with local preset:
  `./scripts/call-omlx.sh "$(cat plan.md)" --preset speckit-tasks`
- Checklist with local preset:
  `./scripts/call-omlx.sh "$(cat spec.md plan.md)" --preset speckit-checklist`
- Analyze with local preset:
  `./scripts/call-omlx.sh "$(cat spec.md plan.md tasks.md)" --preset speckit-analyze`

## Quality Gates

- Specs must be testable, technology-agnostic, and limited to at most three
  explicit clarification markers.
- Plans must identify language, dependencies, storage, project type, and
  constitution checks.
- Tasks must use `T001`, `T002`, and so on; mark parallel work with `[P]` only
  when files and dependencies are independent.
- Implementation must preserve existing user changes and keep patches scoped.
