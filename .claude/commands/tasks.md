---
description: "用 vibe-lens 拆解任務，再用本地模型加工"
---

你現在執行 **tasks 階段**。

步驟：
1. 先呼叫 vibe-lens MCP tool `sdd_tasks`，傳入 feature_name（從 $ARGUMENTS 取得）
2. 取得 `sdd_tasks` 的結果後，用 `local_llm` MCP tool 做後處理，prompt：

```
你是任務拆解助手。以下是 vibe-lens 產出的任務列表。
請做以下加工：
- 確保每個任務格式一致：- [ ] [T###] [P?] [US#?] 描述
- 加上預估時間（分鐘）
- 如果有中文，加上英文摘要
- 標記可平行執行的任務
- 檢查是否有遺漏

任務列表：
{sdd_tasks 的輸出}
```

3. 將 `local_llm` 加工後的結果呈現給使用者
4. 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果
5. 如果品質不夠好，你自己修正

$ARGUMENTS
