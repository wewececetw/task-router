# Quickstart: Agent Profile Selection

## Preview Codex Install

```bash
./install.sh --agent codex --dry-run
```

Expected result:

- Lists Codex guidance destinations.
- Lists shared helper script installation.
- Does not list Claude slash-command writes.
- Performs no file writes.

## Install Claude Code Profile

```bash
./install.sh --agent claude
```

Expected result:

- Installs `.claude` command templates to the user's Claude command directory.
- Updates the managed Task Router section in global Claude guidance.
- Does not touch global Codex guidance.

## Install Both Profiles

```bash
./install.sh --agent both
```

Expected result:

- Installs shared scripts once.
- Updates Codex guidance.
- Updates Claude guidance and commands.
- Keeps shared routing rules semantically consistent across both agents.

## Verify Core Neutrality

```bash
rg -n "~/.codex|~/.claude|CLAUDE.md|AGENTS.md" src/task_router
```

Expected result:

- No matches for global agent install paths in router/classifier/workflow modules.
