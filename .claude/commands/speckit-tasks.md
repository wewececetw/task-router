---
description: "Spec Kit tasks 階段：用本地模型把 plan 拆解成任務列表"
---

你現在執行 Spec Kit 的 **tasks 階段**。

這是一個結構化轉換任務，**請使用 local_llm MCP tool** 來完成，節省 Claude API 額度。

步驟：
1. 讀取 `specs/` 目錄下的 `plan.md`（和 `spec.md` 如果有的話）
2. 用 `local_llm` tool 把 plan 拆解成任務列表，prompt 範例：

```
根據以下 implementation plan，生成結構化的 tasks.md 任務列表。
格式要求：
- 按 Phase 分組（Setup → Foundational → User Stories → Polish）
- 每個任務格式：- [ ] T001 [P] [US1] 描述 in 檔案路徑
- [P] 表示可平行執行
- [US1] 表示所屬 user story

Plan 內容：
{plan.md 的內容}
```

3. 將結果寫入 `specs/{feature}/tasks.md`

$ARGUMENTS
