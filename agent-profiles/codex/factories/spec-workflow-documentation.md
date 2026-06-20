# Spec Workflow Documentation Factory

Use this factory when a project needs GitHub Spec Kit, Fission-AI/OpenSpec, or
project knowledge documents to stay consistent across agent runs.

## When To Load

- The user asks for Spec Kit, OpenSpec, specs, plans, tasks, checklists, ADRs,
  domain knowledge, or engineering knowledge-base documents.
- The repo has `.specify/` or `openspec/`.
- The project `AGENTS.md` declares spec document placement rules.

## Document Placement

- Store feature specs in `docs/specs/{feature-name}/`.
- Each feature spec should contain `spec.md`, `plan.md`, and `tasks.md`.
- Store domain knowledge in `docs/domains/`.
- Store architecture decisions in `docs/adr/`.
- Keep customer-facing documents separate from internal engineering, risk,
  threshold, API, test, and deploy details unless the user explicitly asks to
  publish those details.

## Spec Workflow

1. Use the selected project spec workflow as the primary workflow when requested
   or present.
2. For new features, define the spec and boundaries before implementation.
3. Create or update plan/tasks before code changes when the change is
   non-trivial.
4. Do not mark `tasks.md` items complete until implementation, relevant tests,
   integration checks, and required preview/rendered evidence are available.
5. If a required gate cannot run, leave the task unchecked and state the gap in
   the final handoff.

## Workflow Selection

- For GitHub Spec Kit projects, use `.specify/` scripts and `specify` commands.
- For Fission-AI/OpenSpec projects, use `openspec/`, `/opsx:*` commands, and
  `openspec validate` / `openspec instructions`.
- Do not mix Spec Kit and OpenSpec artifacts in the same feature unless the user
  explicitly asks for a migration or bridge.

## Knowledge-Base Documents

- Prefer durable engineering guidance: responsibilities, contracts, modification
  questions, guardrails, failure modes, verification steps, and file pointers.
- For code examples, prefer contracts, payload shapes, pseudocode, and file
  references when the project guidance forbids direct implementation snippets.
- Keep documents scoped to the project. Do not move secrets, `.env` values,
  tokens, production credentials, or private keys into docs.
