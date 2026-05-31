# Codex / Claude Code Routing Parity Checklist

The profiles may write different files, but these shared categories must route
the same way.

| Category | Claude Code Profile | Codex Profile | Expected Route |
|----------|---------------------|---------------|----------------|
| `speckit.constitution` | `CLAUDE.md` managed rules | `AGENTS.md` managed rules | Active agent |
| `speckit.specify` | `CLAUDE.md` managed rules | `AGENTS.md` managed rules | Active agent |
| `speckit.clarify` | `CLAUDE.md` managed rules | `AGENTS.md` managed rules | Active agent |
| `speckit.plan` | `CLAUDE.md` managed rules | `AGENTS.md` managed rules | Active agent |
| `speckit.tasks` | `speckit-tasks` preset | `speckit-tasks` preset | oMLX |
| `speckit.checklist` | `speckit-checklist` preset | `speckit-checklist` preset | oMLX |
| `speckit.analyze` | `speckit-analyze` preset | `speckit-analyze` preset | oMLX |
| i18n/docstring/migration/test stub/changelog | local helper | local helper | oMLX |
| Boilerplate/config/CRUD/simple docs | local helper | local helper | oMLX |
| Auth/security/core logic/concurrency/data-loss risk | active agent | active agent | Active agent |

Any future difference must be justified by a tool capability difference, not by
duplicated routing logic.
