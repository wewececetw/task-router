# Local Model Delegation

Use this when the task is lightweight enough for oMLX: translation, boilerplate,
JSON/YAML conversion, short documentation, simple schema/model generation, or
repetitive formatting.

## Flow

1. Prefer `./scripts/call-omlx.sh "任務內容"` when available.
2. Fall back to `~/.task-router/scripts/call-omlx.sh "任務內容"`.
3. Review the output before applying file changes.
4. If oMLX fails, returns fallback, or produces low-quality output, Codex
   finishes the task directly.

## Optional Parameters

```bash
./scripts/call-omlx.sh "任務" --system "系統提示" --max-tokens 2048 --temperature 0.3
```
