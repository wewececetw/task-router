---
description: "用 vibe-lens 分析一致性，再用本地模型加工"
---

你現在執行 **analyze 階段**。

步驟：
1. 先呼叫 vibe-lens MCP tool `sdd_analyze`，傳入 feature_name（從 $ARGUMENTS 取得）
2. 取得 `sdd_analyze` 的結果後，用 `local_llm` MCP tool 做後處理，prompt：

```
你是 SDD 分析助手。以下是 vibe-lens 的一致性分析結果。
請做以下加工：
- 每個問題加上嚴重度標籤 (P0: 阻塞 / P1: 重要 / P2: 建議)
- 翻譯成雙語（中英對照）
- 按嚴重度排序
- 加上建議的修復優先順序

分析結果：
{sdd_analyze 的輸出}
```

3. 將 `local_llm` 加工後的結果呈現給使用者
4. 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果
5. 如果品質不夠好，你自己修正

$ARGUMENTS
