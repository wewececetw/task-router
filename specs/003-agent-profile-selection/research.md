# Research: Agent Profile Selection

## Decision 1: Agent choice belongs to installation/profile layer

**Decision**: Implement Codex/Claude selection as an install-time agent profile, not as core router behavior.

**Rationale**: Codex and Claude Code differ mainly in guidance file conventions and slash-command support. The classifier and router only need to decide local versus cloud/active-agent work.

**Alternatives Considered**:

- Hard-code Codex and Claude branches in router modules: rejected because it pollutes core logic with global config paths.
- Maintain two separate repos: rejected because routing rules, presets, and validators would drift.

## Decision 2: Shared rules should be neutral markdown

**Decision**: Store shared routing rules once, using terms like "active agent", "local oMLX", and "fallback".

**Rationale**: Both Codex and Claude profiles can consume the same semantics while rendering into different files.

**Alternatives Considered**:

- Generate shared rules from Python constants: rejected for now because markdown is easier to audit and edit.
- Keep current Claude-only global block and translate manually for Codex: rejected because manual translation creates drift.

## Decision 3: Installer should support dry-run first

**Decision**: Add `--dry-run` before expanding writes.

**Rationale**: Global agent files are sensitive. Users need to see exactly what will change.

**Alternatives Considered**:

- Ask interactively before each write: rejected because it is noisy and harder to test.
- Always overwrite managed blocks silently: rejected because users need confidence in global config changes.

## Decision 4: Keep legacy Claude commands available

**Decision**: Preserve `.claude/commands/` and move/copy profile-ready equivalents later, rather than deleting legacy files.

**Rationale**: Existing Claude Code users should not lose behavior while Codex support is added.

**Alternatives Considered**:

- Delete `.claude/` after adding Codex prompts: rejected because it breaks backward compatibility.
