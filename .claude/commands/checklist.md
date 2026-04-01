---
description: "用本地模型生成品質檢查清單"
---

你現在執行 **checklist 階段**。

這是結構化輸出任務，**請使用 local_llm MCP tool** 來完成。

步驟：
1. 讀取 `specs/` 目錄下的 `spec.md` 和 `plan.md`
2. 用 `local_llm` tool 生成品質檢查清單，prompt 範例：

```
根據以下 spec 和 plan，生成品質檢查清單（markdown checkbox 格式）。
涵蓋：功能完整性、邊界條件、錯誤處理、效能、安全性。

Spec: {spec.md 內容}
Plan: {plan.md 內容}
```

3. 將結果寫入 `specs/{feature}/checklist.md`

$ARGUMENTS
