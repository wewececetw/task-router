# GitHub OpenSpec With Codex

Use Fission-AI/OpenSpec as the source of truth for lightweight SDD workflow.
OpenSpec owns the `openspec/` directory and `/opsx:*` commands.

## Setup

OpenSpec requires Node.js 20.19.0 or higher.

```bash
npm install -g @fission-ai/openspec@latest
openspec init
```

Refresh agent instructions after upgrades or profile changes:

```bash
openspec update
```

## Core Workflow

- `/opsx:propose <idea>` creates `openspec/changes/<change>/` with planning
  artifacts.
- `/opsx:apply` implements tasks from the active change.
- `/opsx:archive` archives the completed change and updates specs.

OpenSpec change artifacts normally include:

```text
openspec/changes/<change>/
├── proposal.md
├── specs/
├── design.md
└── tasks.md
```

## Codex Responsibility

- Use `openspec status`, `openspec instructions`, and `openspec validate` to
  inspect and validate workflow state.
- Do not replace OpenSpec artifact creation with oMLX.
- Use oMLX only for lightweight supporting work outside OpenSpec's core
  artifact lifecycle.
