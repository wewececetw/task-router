# Task Router Constitution

## Core Principles

### I. Codex-First Agent Context
Repository guidance must target Codex through `AGENTS.md`, `BARRON_MEMORY.md`,
and `.codex/`. Claude-specific files may remain for compatibility, but they are
not the primary instruction surface.

### II. Local Model Delegation
Simple, repetitive, and format-heavy tasks may be delegated to oMLX through
`./scripts/call-omlx.sh` or the `omlx-local` MCP tools. Codex remains
responsible for reviewing output quality before applying changes.

### III. Complex Work Stays With Codex
Architecture, security-sensitive code, authentication, routing decisions,
concurrency, data-loss risk, and unclear product behavior must be handled by
Codex directly.

### IV. Spec Kit Discipline
Spec Kit artifacts must stay internally consistent. Specs describe user value,
plans describe technical approach, and tasks describe independently executable
work with clear ordering and validation.

### V. Scoped, Verifiable Changes
Changes should be small, reviewable, and aligned with existing repo style.
Validation starts narrow and expands only when risk or blast radius justifies it.

## Technical Constraints

- Use Python 3.11+ and `uv` for project commands.
- Preserve local oMLX compatibility and the legacy Claude command files unless
  Barron explicitly asks to remove them.
- Prefer deterministic scripts and local validation over network-dependent steps.
- Do not commit, reset, or revert user changes without explicit instruction.

## Development Workflow

1. Inspect relevant files before editing.
2. Use Codex guidance from `AGENTS.md`, `BARRON_MEMORY.md`, and `.codex/`.
3. Delegate only low-risk drafts to the local model.
4. Apply final edits with Codex review and targeted validation.
5. Keep legacy Claude behavior documented but secondary.

## Governance

This constitution overrides placeholder Spec Kit defaults for this repo. Updates
must preserve Codex as the primary agent target and must document any intentional
Claude compatibility behavior.

**Version**: 1.0.0 | **Ratified**: 2026-05-03 | **Last Amended**: 2026-05-03
