# Tasks: Agent Profile Selection

**Input**: Design documents from `/specs/003-agent-profile-selection/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/install-profile.md

**Tests**: Include shell dry-run validation and focused Python tests only where implementation introduces Python install-planning logic.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare profile locations and shared guidance without changing behavior.

- [ ] T001 Create `agent-profiles/shared/routing-rules.md` from current Claude routing block using neutral "active agent" wording
- [ ] T002 [P] Create `agent-profiles/codex/` template structure for AGENTS/memory/prompts guidance
- [ ] T003 [P] Create `agent-profiles/claude/` template structure from existing `.claude/commands/`
- [ ] T004 Document profile source layout in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add profile planning rules before any global writes are changed.

- [ ] T005 Define supported profile values `codex`, `claude`, and `both` in `install.sh`
- [ ] T006 Add `--dry-run` parsing to `install.sh`
- [ ] T007 Implement install-plan output listing directories, file writes, copies, registrations, and warnings
- [ ] T008 Add managed-section replacement helper for global guidance files in `install.sh`
- [ ] T009 Verify `install.sh` syntax with `bash -n install.sh`

**Checkpoint**: Installer can parse choices and print plans without writing profile files.

---

## Phase 3: User Story 1 - Choose Agent During Install (Priority: P1) MVP

**Goal**: Users can choose Codex, Claude Code, or both during installation.

**Independent Test**: Run `./install.sh --agent codex --dry-run`, `./install.sh --agent claude --dry-run`, and `./install.sh --agent both --dry-run`; compare planned destinations.

### Implementation for User Story 1

- [ ] T010 [US1] Implement Codex-only install branch writing Codex guidance from `agent-profiles/codex/`
- [ ] T011 [US1] Implement Claude-only install branch writing Claude guidance and command templates from `agent-profiles/claude/`
- [ ] T012 [US1] Implement both-profile branch that installs shared scripts once and both guidance layers
- [ ] T013 [US1] Update install completion output to show selected profile and next steps
- [ ] T014 [US1] Run dry-run commands for all three profile values and capture expected output in `specs/003-agent-profile-selection/quickstart.md`

**Checkpoint**: Profile selection works independently from core router changes.

---

## Phase 4: User Story 2 - Keep Core Router Agent-Neutral (Priority: P2)

**Goal**: Router/classifier/workflow code stays free of Codex/Claude install concerns.

**Independent Test**: Search core modules for global agent paths and tool-specific installer text.

### Implementation for User Story 2

- [ ] T015 [US2] Rename user-facing route labels in `src/task_router/cli.py` from `Cloud (Claude)` to neutral `Cloud`
- [ ] T016 [US2] Update `src/task_router/workflow.py` comments/reasons to refer to active agent or cloud backend instead of Claude
- [ ] T017 [US2] Keep `src/task_router/claude_client.py` as cloud-provider implementation but prevent installer/profile references from entering router modules
- [ ] T018 [US2] Run `rg -n "~/.codex|~/.claude|CLAUDE.md|AGENTS.md" src/task_router` and verify no install-path leakage

**Checkpoint**: Core code remains focused on routing, not agent setup.

---

## Phase 5: User Story 3 - Codex Spec Kit Delegates Simple Work To oMLX (Priority: P2)

**Goal**: Codex users get oMLX delegation for simple Spec Kit phases and simple implementation tasks, matching the original Claude Code rules.

**Independent Test**: Compare Codex profile guidance to Claude Code routing guidance and verify shared task categories route to the same oMLX presets and fallback behavior.

### Implementation for User Story 3

- [ ] T019 [US3] Add Codex guidance for `speckit.tasks` to call `call-omlx.sh --preset speckit-tasks`
- [ ] T020 [US3] Add Codex guidance for `speckit.checklist` to call `call-omlx.sh --preset speckit-checklist`
- [ ] T021 [US3] Add Codex guidance for `speckit.analyze` to call `call-omlx.sh --preset speckit-analyze`
- [ ] T022 [US3] Add Codex guidance for simple implementation tasks to call oMLX and complex tasks to stay with Codex
- [ ] T023 [US3] Add fallback wording telling Codex to finish directly when oMLX fails or validator exits non-zero
- [ ] T024 [US3] Add a side-by-side parity checklist mapping Claude Code routing categories to Codex routing categories

**Checkpoint**: Codex profile preserves Task Router's local-model savings during Spec Kit workflows.

---

## Phase 6: User Story 4 - Preview Before Writing (Priority: P3)

**Goal**: Users can inspect global writes before installation.

**Independent Test**: Record file mtimes before dry-run and verify they do not change after dry-run.

### Implementation for User Story 4

- [ ] T025 [US4] Ensure every write-capable installer operation has a dry-run branch
- [ ] T026 [US4] Add invalid profile handling before any directory creation or file copy
- [ ] T027 [US4] Add warnings for missing `codex` or `claude` CLI without writing partial profile output
- [ ] T028 [US4] Verify repeated dry-runs produce stable output

**Checkpoint**: Preview mode is safe and useful.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, consistency, and final validation.

- [ ] T029 Update `README.md` quickstart to show `--agent codex`, `--agent claude`, and `--agent both`
- [ ] T030 [P] Update `.codex/prompts/README.md` to reference shared profile rules
- [ ] T031 [P] Update `scripts/call-omlx.sh` fallback wording from "Claude 接手" to "active agent 接手"
- [ ] T032 Decide and document one default `OMLX_BASE_URL` port across `.codex/config.toml`, scripts, README, and Python defaults
- [ ] T033 Run `bash -n install.sh scripts/call-omlx.sh .specify/scripts/bash/update-agent-context.sh`
- [ ] T034 Run `git diff --stat` and review changes for unrelated churn

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on setup and blocks profile installation work.
- **User Story 1 (P1)**: Depends on foundational install planning.
- **User Story 2 (P2)**: Can start after setup, but final verification should happen after US1.
- **User Story 3 (P2)**: Depends on Codex profile templates and shared routing rules.
- **User Story 4 (P3)**: Depends on foundational dry-run support.
- **Polish**: Depends on selected user stories.

### Parallel Opportunities

- T002 and T003 can run in parallel.
- US2 label cleanup can run while installer profile branches are implemented.
- README and prompt documentation updates can run in parallel during polish.

## Implementation Strategy

### MVP First

1. Complete T001-T009.
2. Complete T010-T014.
3. Stop and validate all three `--agent` dry-runs.

### Incremental Delivery

1. Deliver profile selection with dry-run.
2. Neutralize core labels.
3. Harden idempotent global writes.
4. Update docs and port consistency.
