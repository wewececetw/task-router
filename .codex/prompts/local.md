# Local Model Delegation

Use this when Barron asks to send a task to the local model, or when the task is
small enough for oMLX: translation, boilerplate, JSON/YAML conversion, short
documentation, simple schema/model generation, or repetitive formatting.

## Flow

1. Run `./scripts/call-omlx.sh "使用者任務內容"`.
2. Return the useful output directly, or apply it if the user asked for file
   changes.
3. If the helper returns `oMLX FALLBACK`, malformed output, or an unsafe patch,
   Codex finishes the task directly.

## Optional Parameters

```bash
./scripts/call-omlx.sh "任務" --system "系統提示" --max-tokens 2048 --temperature 0.3
```

Codex remains responsible for correctness. Treat local-model output as a draft,
not as trusted final code.
