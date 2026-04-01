---
description: "用本地模型實作簡單任務（boilerplate, model, config, CRUD）"
---

你現在執行 **implement 階段（簡單任務）**。

以下類型的任務，**請使用 local_llm MCP tool** 來生成程式碼：
- 建立 model / schema / entity
- Boilerplate / scaffold / 專案結構
- 簡單 CRUD endpoint
- 設定檔（config, .env, docker-compose）
- 簡單 unit test
- Database migration
- 文件、註解

流程：
1. 讀取 `tasks.md` 找到要實作的任務
2. 用 `local_llm` tool 生成程式碼
3. 審查結果（你自己檢查一下品質）
4. 寫入對應的檔案
5. 如果品質不夠好，你自己修正

$ARGUMENTS
