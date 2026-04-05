---
description: "用本地模型實作簡單任務（boilerplate, model, config, CRUD）"
---

執行 **implement 階段（簡單任務）** — 把 boilerplate 類型的工作交給本地模型。

適用任務：
- 建立 model / schema / entity
- Boilerplate / scaffold / 專案結構
- 簡單 CRUD endpoint
- 設定檔（config, .env, docker-compose）
- 簡單 unit test
- Database migration
- 文件、註解

流程：
1. 用 Read 讀取 `specs/{feature}/tasks.md` 找到要實作的任務
2. 用 Bash 執行 `./scripts/call-omlx.sh` 生成程式碼：

```bash
./scripts/call-omlx.sh "實作以下任務，輸出完整程式碼（含 import）：

任務描述：{task description}
技術棧：{從 plan.md 讀取}
目標檔案：{file path}

要求：
- 遵循專案既有的程式碼風格
- 加上必要的型別註解和 docstring
- 只輸出程式碼，不要說明文字" --max-tokens 4096 --temperature 0.3
```

3. 審查品質（你負責確認程式碼正確性）
4. 用 Write 寫入對應的檔案
5. 如果 FALLBACK 或品質不夠，你自己實作

$ARGUMENTS
