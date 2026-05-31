# Contract: Install Agent Profile

## Command

```bash
./install.sh --agent <codex|claude|both> [--dry-run] [--force]
```

## Behavior

- `--agent codex`: installs Codex guidance only.
- `--agent claude`: installs Claude Code guidance and commands only.
- `--agent both`: installs shared scripts once, then installs both guidance layers.
- `--dry-run`: prints the install plan and exits without writing.
- `--force`: allows installation to continue when optional validation fails. It must not bypass invalid agent names.

## Required Output

Dry-run output must include:

- Selected profiles.
- Directories that would be created.
- Files that would be created or updated.
- Commands that would be registered.
- Warnings for missing tools or skipped optional steps.

## Failure Rules

- Invalid `--agent` value exits non-zero before writes.
- Missing required profile tool exits non-zero before writes unless the profile can be installed by files alone.
- Existing target files with malformed managed markers exit non-zero and leave the file unchanged.

## Idempotency

Running the same install command twice must not duplicate managed sections, command files, or helper script copies.
