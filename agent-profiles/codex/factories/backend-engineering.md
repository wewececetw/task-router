# Backend Engineering Factory

Use this factory for backend, API, worker, queue, job, webhook, database, or
business-logic work. It is framework-neutral; apply framework adapters only when
they match the current repo.

## When To Load

- The task changes backend behavior, API contracts, jobs, queues, broadcasts,
  webhooks, persistence, auth, authorization, integrations, or domain logic.
- The project `AGENTS.md` declares backend rules.
- The user asks for engineering handoff, backend knowledge base, modification
  guardrails, code review questions, or safe-change guidance.

## Core Workflow

1. Identify the existing architecture and ownership boundary before changing
   files.
2. Identify the contract being changed: endpoint, event payload, command shape,
   database invariant, job side effect, external API behavior, or observable
   user/admin outcome.
3. Keep business rules in the existing domain/service/action/use-case layer,
   not in transport glue such as controllers, route handlers, CLI wrappers, or
   view code.
4. Put request/input validation in the framework's established validation layer
   when one exists.
5. Use transactions for multi-table writes and any write path that must stay
   consistent across related records.
6. Treat external APIs, queues, jobs, webhooks, broadcasts, and workers as
   unreliable boundaries. Add idempotency, retries, timeouts, clear failure
   states, and safe re-run behavior where the product behavior requires them.
7. Add or update tests when behavior changes. Cover the happy path, at least one
   negative/validation path, and relevant boundary behavior for queues,
   broadcasts, transactions, or external calls when touched.
8. Run the repo's deterministic gates before handoff when available: formatter,
   unit tests, integration/feature tests, static analysis/typecheck, migrations,
   contract checks, and smoke tests.

## Default Guardrails

- Follow existing project structure and naming before introducing new folders or
  abstractions.
- Keep dependency, generated, runtime, cache, and build-output directories
  untouched unless the user explicitly asks for maintenance on those paths.
- Do not change public contracts, auth/session/token handling, production
  deploy behavior, or data-loss boundaries without explicit spec/user direction.
- Before implementing, ask whether the change is durable state, derived state,
  or a one-shot command. Do not persist one-shot commands as long-lived state
  unless the spec explicitly requires audit/history.
- Make failure modes explicit: validation error, not found, conflict, retryable
  failure, permanent failure, and partial external-service outage.

## Engineer Handoff Checklist

- What exact behavior or contract changed?
- Which files own the domain logic, validation, transport, persistence, and
  tests?
- What invariants must remain true after failure or retry?
- Which negative cases are covered?
- Which deterministic checks ran, and which could not run?
- Which operational risks remain: queue backlog, duplicate job, stale cache,
  external API outage, migration rollback, or incompatible client payload?

## Framework Adapter: Laravel

Apply these only for Laravel projects unless project instructions override them.

- Do not edit `vendor/`, `storage/`, or `bootstrap/cache/`.
- Put business logic in Service classes when the project already follows that
  pattern.
- Use FormRequest classes for validation when applicable.
- Use Laravel database transactions for multi-table writes.
- Prefer these gates when available: `./vendor/bin/pint`, `php artisan test`,
  and `./vendor/bin/phpstan analyse`.
