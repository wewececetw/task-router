# App UI/UX Factory

Use this factory for app, game, mobile, web-app, interactive product, UI, or UX
work.

## When To Load

- The task changes user-facing screens, flows, interaction behavior, visual
  layout, preview surfaces, game scenes, mobile views, or web-app UI.
- The user asks for design, mockups, UI/UX, frontend implementation, app
  testing, rendered-surface verification, or screenshot evidence.

## Intent First

- Produce a UI/UX intent screen or mockup before implementation unless Barron
  explicitly asks to skip it.
- Implementation must follow the accepted UI/UX intent screen.
- If layout, transparency, clipping, responsiveness, or technical constraints
  start drifting from the accepted visual structure, stop and realign before
  continuing.

## Rendered-Surface Done Rule

- Visual implementation is not done until verified on the real rendered surface
  with screenshots, not only by code changes.
- For UI/UX-facing changes, preview mode or an equivalent rendered-surface check
  is required in addition to code-level tests.
- If preview verification is unavailable, state that gap explicitly in the final
  handoff.

## App Testing Gate

- Run the project's available unit tests, integration tests, and
  preview/rendered-surface verification before calling implementation work done.
- If one of those test layers does not exist or cannot be run, state that gap in
  the final handoff instead of silently skipping it.
