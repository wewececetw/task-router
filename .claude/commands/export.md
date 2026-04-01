---
description: "用 vibe-lens 匯出報告，再用本地模型調整格式"
---

你現在執行 **export 階段**。

步驟：
1. 先呼叫 vibe-lens MCP tool `sdd_export`，傳入 feature_name（從 $ARGUMENTS 取得）
2. 取得 `sdd_export` 的結果後，用 `local_llm` MCP tool 做後處理，prompt：

```
你是報告格式化助手。以下是 vibe-lens 產出的 stakeholder 報告。
請做以下加工：
- 調整為更適合非技術人員閱讀的格式
- 加上執行摘要（Executive Summary）
- 重點用粗體標記
- 移除過於技術性的細節

報告內容：
{sdd_export 的輸出}
```

3. 將 `local_llm` 加工後的結果呈現給使用者
4. 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果

$ARGUMENTS
