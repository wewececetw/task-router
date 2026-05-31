# Implementation Plan: Agent Profile Selection

**Branch**: `003-agent-profile-selection` | **Date**: 2026-05-31 | **Spec**: `spec.md`
**Input**: Feature specification from `/specs/003-agent-profile-selection/spec.md`

## Summary

Add an agent profile layer so users can choose Codex, Claude Code, or both during installation. The core router remains agent-neutral; agent-specific behavior lives in profile metadata, templates, and installer code. Shared oMLX routing rules are written once and rendered into each selected agent's expected guidance format. In the Codex profile, Spec Kit structured/simple phases call oMLX through the same presets and fallback rules as the original Claude Code integration, while complex reasoning stays with Codex.

## Technical Context

**Language/Version**: Python 3.11+, Bash
**Primary Dependencies**: Typer, Rich, Pydantic, FastAPI, MCP, Anthropic SDK, OpenAI SDK, LiteLLM
**Storage**: Filesystem-managed config/guidance files
**Testing**: Shell syntax checks, pytest if existing tests are added, dry-run verification
**Target Platform**: macOS developer machines with Codex and/or Claude Code
**Project Type**: Python CLI plus shell installer
**Performance Goals**: Install plan generation completes under 1 second for local files
**Constraints**: Must preserve existing dirty user files; must not overwrite unmanaged global config content; must keep router/classifier agent-neutral
**Scale/Scope**: 2 initial agent profiles, extensible to additional profiles later

## Constitution Check

- **Codex-First Agent Context**: Pass. Codex stays first-class through `AGENTS.md`, `BARRON_MEMORY.md`, and `.codex/`.
- **Local Model Delegation**: Pass. Shared routing rules continue to route lightweight work through `call-omlx.sh`.
- **Complex Work Stays With Codex**: Pass with nuance. In Codex profile, complex work stays with Codex. In Claude profile, complex work stays with Claude Code. The shared model should call this the "active agent" instead of hard-coding one vendor.
- **Spec Kit Discipline**: Pass. This feature defines spec, plan, data model, contract, quickstart, and tasks.
- **Scoped, Verifiable Changes**: Pass. Implementation can be delivered in slices: profile metadata, dry-run planning, profile-specific writes, docs.

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-profile-selection/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── install-profile.md
└── tasks.md
```

### Source Code (repository root)

```text
agent-profiles/
├── shared/
│   └── routing-rules.md
├── codex/
│   ├── AGENTS.md.template
│   └── prompts/
└── claude/
    ├── CLAUDE.md.template
    └── commands/

scripts/
├── call-omlx.sh
├── presets/
└── validators/

src/task_router/
├── cli.py
├── config.py
├── router.py
└── workflow.py

install.sh
```

**Structure Decision**: Add profile data/templates outside `src/task_router/` so core routing remains neutral. Keep `install.sh` as the compatibility entrypoint, but move profile-specific decisions into clearly named profile sections or a small install planner script.

## Proposed Design

Use three layers:

1. **Core router**: Classifies and routes to `local` or `cloud`. It should avoid agent install paths and agent-specific global config writes.
2. **Shared routing guidance**: One neutral markdown source describes oMLX delegation and fallback rules using terms like "active agent" and "cloud backend".
3. **Agent profiles**: Codex and Claude templates adapt shared guidance to each tool's file conventions.

This avoids code pollution because selecting Codex or Claude becomes installer/profile data, not branching behavior inside classifier, workflow, or router modules.

## Codex Spec Kit Routing Contract

Codex profile guidance must match the original Claude Code routing semantics for shared categories. It must include these default routes:

| Spec Kit phase or task | Codex behavior |
|------------------------|----------------|
| `speckit.constitution` | Codex handles directly |
| `speckit.specify` | Codex handles directly |
| `speckit.clarify` | Codex handles directly |
| `speckit.plan` | Codex handles directly |
| `speckit.tasks` | Call `call-omlx.sh --preset speckit-tasks` |
| `speckit.checklist` | Call `call-omlx.sh --preset speckit-checklist` |
| `speckit.analyze` | Call `call-omlx.sh --preset speckit-analyze` |
| Simple implement tasks | Call oMLX when output is boilerplate/config/CRUD/docs/test skeletons |
| Complex implement tasks | Codex handles directly |

If oMLX is offline, a validator fails, or output quality is insufficient, Codex finishes the task directly.

Claude Code and Codex profiles may differ in file format and command mechanics, but not in routing intent. For example, Claude Code can install slash commands under `~/.claude/commands/`, while Codex may express the same behavior through `AGENTS.md` and `.codex/prompts/`; both must point simple Spec Kit work at the same oMLX presets.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Profile template layer | Two agent ecosystems use different command/guidance formats | Hard-coding both in `install.sh` would duplicate rules and keep expanding vendor-specific shell branches |
