# Implement Simple

Use this for boilerplate-style implementation tasks:

- model, schema, entity, or DTO creation
- simple CRUD endpoints
- config files, `.env` examples, or Docker Compose snippets
- simple unit-test skeletons
- straightforward database migrations
- documentation and docstrings

## Flow

1. Read the relevant spec, task, and target files.
2. Ask oMLX for a focused draft only when that saves time:

```bash
./scripts/call-omlx.sh "實作以下任務，輸出完整程式碼（含 import）：

任務描述：{task description}
技術棧：{from plan.md or repo context}
目標檔案：{file path}

要求：
- 遵循專案既有的程式碼風格
- 加上必要的型別註解和 docstring
- 只輸出程式碼，不要說明文字" --max-tokens 4096 --temperature 0.3
```

3. Review the draft for correctness, project style, imports, and edge cases.
4. Apply changes with `apply_patch`.
5. Run the narrowest useful validation command when practical.

If the task involves security, auth, core routing logic, concurrency, data loss,
or ambiguous architecture, Codex should implement it directly instead of
delegating.
