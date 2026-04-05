---
description: "用本地模型生成 DB migration 檔案"
---

生成 database migration 檔案。

步驟：
1. 用 Read 讀取 model/schema 定義檔
2. 用 Bash 執行 `./scripts/call-omlx.sh` 生成 migration：

```bash
./scripts/call-omlx.sh "根據以下 model 定義，生成 database migration。
- 偵測使用的框架（Prisma / Alembic / Knex / TypeORM）
- 生成 up 和 down migration
- 包含 index 和 constraint

Model 定義：
{schema 內容}" --max-tokens 4096 --temperature 0.3
```

3. 用 Write 寫入對應的 migration 檔案
4. 檢查 SQL 的正確性（這是你的責任，本地模型可能出錯）
5. 如果 FALLBACK，你自己生成 migration

$ARGUMENTS
