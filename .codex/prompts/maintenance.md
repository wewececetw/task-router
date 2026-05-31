# Maintenance Tasks

## Changelog

1. Inspect recent history with `git log --oneline -20` and a focused diff/stat.
2. Draft a Keep a Changelog entry.
3. Insert or update `CHANGELOG.md` only if the user asked for a file change.

## Docstrings

1. Read the target source file.
2. Add documentation only for public functions, classes, and methods.
3. Use the language's native convention: Google-style Python docstrings, JSDoc,
   godoc, or the repo's existing style.

## i18n

1. Preserve keys and placeholders like `{{name}}`, `{0}`, `%s`, and ICU blocks.
2. Translate values only.
3. Validate JSON/YAML syntax before writing.

## Migration

1. Read the model/schema and infer the migration framework from the repo.
2. Generate both forward and rollback behavior when the framework supports it.
3. Verify indexes, constraints, defaults, and nullability manually.

## Test Stub

1. Match the repo's existing test framework and naming convention.
2. Cover normal and boundary cases.
3. Leave TODO assertions only when Barron explicitly asked for skeletons.
