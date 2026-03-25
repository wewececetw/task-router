---
description: "用本地模型生成 DB migration 檔案"
---

**請使用 local_llm MCP tool** 生成 database migration。

步驟：
1. 讀取 model/schema 定義檔
2. 用 `local_llm` tool 生成 migration，prompt：

```
根據以下 model 定義，生成 database migration。
- 偵測使用的框架（Prisma / Alembic / Knex / TypeORM）
- 生成 up 和 down migration
- 包含 index 和 constraint

Model 定義：
{schema 內容}
```

3. 寫入對應的 migration 檔案
4. 你自己檢查 SQL 的正確性

$ARGUMENTS
