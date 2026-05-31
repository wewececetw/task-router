# Codex Prompts

These files adapt the legacy `.claude/commands/` guidance for Codex.
Canonical shared routing rules live in `agent-profiles/shared/routing-rules.md`.

Codex does not need Claude slash-command frontmatter to perform the work. Use
these prompt files as operational playbooks when Barron asks for the matching
task by name.

## Prompt Map

- `local.md`: send a lightweight task to the local oMLX model.
- `implement-simple.md`: use the local model for boilerplate-style tasks, then
  review and patch the result.
- `maintenance.md`: changelog, docstring, i18n, migration, and test-stub flows.
- `speckit.md`: Codex handling for Spec Kit workflows.

Legacy Claude files remain in `.claude/commands/` for reference and backward
compatibility.

Generated global Codex installs should come from `agent-profiles/codex/` so the
Codex and Claude Code profiles stay semantically aligned.
