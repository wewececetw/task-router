# Feature Specification: Agent Profile Selection

**Feature Branch**: `003-agent-profile-selection`
**Created**: 2026-05-31
**Status**: Draft
**Input**: User description: "可以把它改成 Codex 跟 Claude Code 可以讓使用者自行選擇嗎，但又不污染程式碼，用 Spec Kit 做"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choose Agent During Install (Priority: P1)

A user installing Task Router chooses whether to install Codex integration, Claude Code integration, or both, without editing scripts manually.

**Why this priority**: This is the main product decision. The package should not assume Claude Code or Codex globally.

**Independent Test**: Run the installer with each supported agent option in dry-run mode and verify the planned file writes only target the selected agent locations.

**Acceptance Scenarios**:

1. **Given** a clean machine with Codex installed, **When** the user runs install with `--agent codex`, **Then** the installer prepares Codex guidance and does not write Claude Code commands.
2. **Given** a machine with Claude Code installed, **When** the user runs install with `--agent claude`, **Then** the installer prepares Claude commands and does not write Codex guidance.
3. **Given** a user wants both tools, **When** the user runs install with `--agent both`, **Then** the installer prepares both integrations from the same shared routing rules.

---

### User Story 2 - Keep Core Router Agent-Neutral (Priority: P2)

A maintainer can update routing behavior without touching Codex-specific or Claude-specific files.

**Why this priority**: Agent-specific text should not leak into core router code, CLI output, or classifier behavior.

**Independent Test**: Inspect and run core router tests after adding the feature; core modules should use neutral concepts like `local`, `cloud`, and `agent profile`, not hard-coded Codex or Claude Code install behavior.

**Acceptance Scenarios**:

1. **Given** a routing rule changes, **When** a maintainer updates the shared rules, **Then** Codex and Claude profile outputs both receive the same semantic change.
2. **Given** a core Python module is inspected, **When** searching for agent-install paths, **Then** no references to `~/.codex`, `~/.claude`, `CLAUDE.md`, or Codex prompt directories appear outside profile/install code.

---

### User Story 3 - Codex Spec Kit Delegates Simple Work To oMLX (Priority: P2)

A Codex user running a Spec Kit workflow gets the same local-model savings as the original Claude Code rules: structured/simple phases call oMLX, while complex reasoning remains with Codex.

**Why this priority**: Codex support is only useful if it preserves the original Task Router value: simple Spec Kit work should not consume the main agent unnecessarily.

**Independent Test**: Compare Codex profile guidance against the original Claude Code routing rules and verify the same phases/tasks call `call-omlx.sh` with the same presets and fallback behavior.

**Acceptance Scenarios**:

1. **Given** Codex profile guidance is installed, **When** the user asks Codex to generate Spec Kit tasks from a plan, **Then** Codex should invoke `./scripts/call-omlx.sh` or the global helper with `--preset speckit-tasks`.
2. **Given** Codex profile guidance is installed, **When** the user asks for Spec Kit checklist or analyze output, **Then** Codex should invoke the matching oMLX preset and fall back to Codex if validation fails.
3. **Given** Codex profile guidance is installed, **When** the user asks for implementation, **Then** boilerplate/config/CRUD/docstring/test-stub work may call oMLX, but auth/security/core logic stays with Codex.
4. **Given** Claude Code legacy rules route a task category to oMLX, **When** the same category appears in Codex guidance, **Then** Codex guidance should route it to oMLX unless Codex lacks the required local helper.

---

### User Story 4 - Preview Before Writing (Priority: P3)

A cautious user can preview which files will be created or modified before applying an agent profile.

**Why this priority**: Global agent config writes are sensitive and should be transparent.

**Independent Test**: Run install with `--dry-run` and verify no files change while the output lists exact destinations.

**Acceptance Scenarios**:

1. **Given** existing global Codex and Claude configs, **When** the user runs `--agent both --dry-run`, **Then** the command prints every target path and exits without changes.
2. **Given** an unsupported agent value, **When** the user runs install, **Then** the command fails before any write and lists supported values.

### Edge Cases

- Selected agent CLI is not installed: installer should warn and skip CLI registration that depends on that binary, unless the selected profile only requires file templates.
- Existing global config already contains a Task Router section: installer should replace only the managed section and preserve user content.
- oMLX is not running during installation: installer should still install files but mark runtime verification as skipped or failed.
- User selects both profiles: shared scripts should be installed once, then both agent-specific guidance layers should reference the same helper path.
- Repo-local Codex guidance exists: install should not overwrite repo-local files unless explicitly requested.
- Codex profile is selected but local oMLX is offline: guidance should still install, and runtime fallback should tell Codex to complete the task directly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an explicit agent selection option with supported values `codex`, `claude`, and `both`.
- **FR-002**: System MUST keep shared routing rules in an agent-neutral source that can render or feed both Codex and Claude Code guidance.
- **FR-003**: System MUST isolate agent-specific templates, commands, and destination paths from core router logic.
- **FR-004**: System MUST support a dry-run mode that prints planned writes and command registrations without modifying files.
- **FR-005**: System MUST preserve user-authored content outside Task Router managed sections when updating global agent files.
- **FR-006**: System MUST install shared helper scripts and presets once, regardless of how many agent profiles are selected.
- **FR-007**: System MUST document which profile writes to Codex files, Claude files, or both.
- **FR-008**: System MUST use neutral CLI labels for routing output, such as `Local (oMLX)` and `Cloud`, unless an agent profile explicitly needs tool-specific wording.
- **FR-009**: System MUST let maintainers add future agent profiles without changing classifier or router modules.
- **FR-010**: System MUST fail before writing if the selected agent value is invalid.
- **FR-011**: Codex profile guidance MUST route Spec Kit `tasks`, `checklist`, and `analyze` phases to oMLX presets by default.
- **FR-012**: Codex profile guidance MUST route simple implementation tasks to oMLX and keep complex/security-sensitive implementation tasks with Codex.
- **FR-013**: Codex profile routing rules MUST remain semantically consistent with the original Claude Code routing rules for all shared task categories.
- **FR-014**: Any intentional difference between Codex and Claude Code routing MUST be documented in the profile template and justified by tool capability differences.

### Key Entities *(include if feature involves data)*

- **Agent Profile**: A selectable integration target. Attributes include name, description, required tools, managed files, command template directory, global guidance destination, and install capabilities.
- **Managed Section**: A named block inside a global guidance file that Task Router owns and can replace safely.
- **Shared Routing Rule**: Agent-neutral guidance describing which tasks go to local oMLX and which stay with the active agent/cloud path.
- **Install Plan**: A computed list of file writes, directory creations, executable registrations, and warnings for a selected profile.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can install Codex-only, Claude-only, and both-profile setups using one documented command each.
- **SC-002**: Dry-run output lists all planned global file writes and performs zero writes.
- **SC-003**: Search results show no global agent config paths in `src/task_router/classifier.py`, `src/task_router/router.py`, or `src/task_router/workflow.py`.
- **SC-004**: Adding a new agent profile requires adding profile data/templates and does not require editing routing/classifier code.
- **SC-005**: Existing Task Router managed sections are replaced idempotently; running install twice does not duplicate guidance blocks.
- **SC-006**: Codex profile documentation contains explicit oMLX preset commands for Spec Kit `tasks`, `checklist`, and `analyze`.
- **SC-007**: A side-by-side rule comparison shows Codex and Claude Code profiles route the same shared task categories to oMLX.
