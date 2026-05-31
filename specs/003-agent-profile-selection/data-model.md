# Data Model: Agent Profile Selection

## AgentProfile

Represents one selectable integration target.

Fields:

- `name`: Stable profile id, such as `codex` or `claude`.
- `display_name`: Human-readable name.
- `required_tools`: Commands that should be checked before profile installation.
- `optional_tools`: Commands that improve the profile but are not required.
- `managed_files`: Files the profile can create or update.
- `template_root`: Repo path containing profile-specific templates.
- `supports_slash_commands`: Whether the profile installs slash commands.
- `global_guidance_path`: Destination for the managed guidance block.

Validation:

- `name` must be unique.
- `managed_files` must be explicit; no glob writes in dry-run output.
- Missing required tools must stop writes unless `--force` is provided.

## ManagedSection

Represents a replaceable block inside a target guidance file.

Fields:

- `section_id`: Stable marker, for example `Task Router`.
- `start_marker`: Exact start marker string.
- `end_marker`: Exact end marker string.
- `content`: Rendered markdown body.
- `target_path`: File to update.

Validation:

- Existing content outside markers must remain unchanged.
- Re-running install must produce one managed section, not duplicates.

## SharedRoutingRule

Represents agent-neutral routing guidance.

Fields:

- `trigger`: User intent or command category.
- `route`: `local`, `active-agent`, or `cloud-backend`.
- `helper_command`: Optional helper invocation.
- `fallback`: What the active agent should do if local routing fails.

Validation:

- Rules must not mention `~/.codex`, `~/.claude`, or profile-specific paths.
- Profile templates may add path-specific instructions around the shared rule body.

## InstallPlan

Represents the computed operations for selected profiles.

Fields:

- `selected_profiles`: Ordered list of `AgentProfile` ids.
- `directories`: Directories to create.
- `file_writes`: Managed files to create or update.
- `copies`: Shared scripts/templates to copy.
- `registrations`: CLI registrations, if any.
- `warnings`: Non-fatal issues.

Validation:

- Invalid profiles fail before any operation.
- Dry-run prints the plan and performs no operation.
