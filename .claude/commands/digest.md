---
description: "用 vibe-lens 產出商業邏輯摘要，再用本地模型翻譯成雙語"
---

你現在執行 **digest 階段**。

步驟：
1. 先呼叫 vibe-lens MCP tool `sdd_digest`，傳入 feature_name（從 $ARGUMENTS 取得）
2. 取得 `sdd_digest` 的結果後，用 `local_llm` MCP tool 做後處理，prompt：

```
你是技術文件翻譯助手。以下是 vibe-lens 產出的商業邏輯摘要。
請做以下加工：
- 翻譯成英文版本（保留中文原文，雙語對照）
- 確保技術術語翻譯準確
- 保持 markdown 格式

商業邏輯摘要：
{sdd_digest 的輸出}
```

3. 將 `local_llm` 加工後的結果呈現給使用者
4. 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果

$ARGUMENTS
