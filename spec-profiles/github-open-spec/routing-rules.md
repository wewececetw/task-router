# GitHub OpenSpec Workflow

Use Fission-AI/OpenSpec as the source of truth for lightweight SDD workflow.
OpenSpec owns `openspec/` artifacts and `/opsx:*` workflow commands.

OpenSpec requires Node.js 20.19.0 or higher and the CLI package:

```bash
npm install -g @fission-ai/openspec@latest
```

Initialize an OpenSpec project from the project root:

```bash
openspec init
```

The default quick path is:

| Trigger | Purpose |
|---------|---------|
| `/opsx:propose <idea>` | Create `openspec/changes/<change>/` and planning artifacts |
| `/opsx:apply` | Implement tasks from the active change |
| `/opsx:archive` | Archive completed change and update specs |

OpenSpec creates change artifacts under:

```text
openspec/changes/<change>/
├── proposal.md
├── specs/
├── design.md
└── tasks.md
```

Useful CLI commands:

```bash
openspec list
openspec status --change <change>
openspec instructions --change <change>
openspec instructions tasks --change <change>
openspec instructions apply --change <change>
openspec validate --all
openspec archive <change> --yes
openspec update
```

## oMLX Routing Inside GitHub OpenSpec

Do not replace OpenSpec artifact workflow with oMLX. Use OpenSpec commands and
instructions for `proposal`, `specs`, `design`, `tasks`, `apply`, and archive
flows.

oMLX may still be used for lightweight supporting work outside OpenSpec's core
artifact lifecycle:

- i18n translation
- docstring drafts
- changelog drafts
- simple boilerplate snippets
- JSON/YAML/Markdown conversion

Until dedicated OpenSpec presets and validators exist, do not route OpenSpec
`tasks.md`, `proposal.md`, `design.md`, or delta specs to oMLX automatically.
