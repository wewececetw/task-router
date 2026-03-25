---
description: "Spec Kit analyze 階段：用本地模型檢查 spec 一致性"
---

你現在執行 Spec Kit 的 **analyze 階段**。

這是模式匹配和比對任務，**請使用 local_llm MCP tool** 來完成。

步驟：
1. 讀取 `specs/` 目錄下的 `spec.md`、`plan.md`、`tasks.md`
2. 用 `local_llm` tool 檢查一致性，prompt：

```
檢查以下三份文件的一致性，找出不一致或遺漏：
1. spec 裡提到但 plan 沒有涵蓋的需求
2. plan 裡的步驟但 tasks 沒有對應任務
3. tasks 裡的任務但 spec/plan 沒有提到

Spec: {spec.md}
Plan: {plan.md}
Tasks: {tasks.md}

輸出格式：
## 不一致
- [ ] 問題描述

## 遺漏
- [ ] 遺漏描述

## 建議
- 建議描述
```

3. 將結果寫入 `specs/{feature}/analysis.md`

$ARGUMENTS
