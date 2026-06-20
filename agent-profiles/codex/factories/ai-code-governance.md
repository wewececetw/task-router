# AI Code Governance Factory

Use this factory for non-trivial software work, AI-generated code governance,
review workflow, deterministic verification, and scope-control decisions.

## When To Load

- The task asks to codify workflow rules, create or update generated code, use an
  AI helper, review AI output, update specs/tasks, or perform substantial
  implementation.
- The change touches security, auth, authorization, sessions, tokens, production
  deploy behavior, data-loss risk, core business logic, concurrency,
  performance, migrations, or public contracts.

## Required Workflow

1. Define spec, intent, and boundaries before non-trivial implementation.
2. Create or update plan/tasks when the project uses a spec workflow or the work
   has multiple implementation steps.
3. Implement with the active coding agent owning architecture judgment,
   implementation quality, security judgment, and final review.
4. Add or update relevant tests.
5. Run deterministic checks that fit the repo: tests, typecheck, lint, build,
   migration checks, contract checks, smoke tests, and preview/rendered-surface
   validation when applicable.
6. Perform a second-pass review of the diff against spec, tasks, tests, security
   risks, contract drift, scope creep, and missing evidence.
7. Complete the human-facing handoff with evidence and any explicit gaps.

## AI Output Boundaries

- AI-generated code is acceptable only inside an explicit specification,
  implementation, review, and verification workflow.
- Do not treat generated code as done just because it compiles or looks
  plausible.
- Use oMLX only for selected drafts such as tasks, checklist, analyze,
  translations, boilerplate, and test skeletons; review all oMLX output before
  applying it.
- Do not delegate auth, authorization, sessions, token handling, core business
  logic, concurrency, performance, data-loss risk, or production deploy
  decisions to unchecked generated output.
- AI review is not a replacement for deterministic tooling or human judgment.
  Security-sensitive changes still require explicit tests, negative cases, and
  manual review of the threat boundary.

## Scope And Secrets

- Keep AI work scoped. Do not change unrelated files, rewrite architecture, add
  dependencies, alter public contracts, or modify deploy/runtime behavior unless
  the spec or direct user instruction requires it.
- Never put API keys, tokens, `.env` contents, private credentials, or
  production secrets into prompts, shell commands, generated docs, commits, or
  review artifacts.
- Do not mark spec workflow `tasks.md` items complete until implementation,
  relevant automated checks, integration checks, and required preview evidence
  are all available. If a gate cannot be run, leave the risk explicit in the
  final handoff.
