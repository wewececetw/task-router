# Maintenance Tasks

## Changelog

Inspect recent history and draft a Keep a Changelog entry. Write it only when
the user asks for a file change.

## Docstrings

Add documentation only for public functions, classes, and methods. Match the
language's native convention and the repo's existing style.

## i18n

Translate values only. Preserve keys, placeholders, ICU blocks, and JSON/YAML
syntax.

## Migration

Infer the migration framework from the repo, generate forward and rollback
behavior where supported, and manually verify indexes, constraints, defaults,
and nullability.

## Test Stub

Match the existing test framework and naming convention. Leave TODO assertions
only when the user explicitly asks for skeletons.
