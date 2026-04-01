---
description: "用 vibe-lens 審閱 SDD 產出物，再用本地模型展開建議"
---

你現在執行 **review artifact 階段**。

步驟：
1. 先呼叫 vibe-lens MCP tool `sdd_review_artifact`，傳入 feature_name 和 artifact_type（從 $ARGUMENTS 取得，artifact_type 可以是 spec / plan / tasks / all）
2. 取得 `sdd_review_artifact` 的結果後，用 `local_llm` MCP tool 做後處理，prompt：

```
你是 SDD 品質審查助手。以下是 vibe-lens 對產出物的審閱結果。
請做以下加工：
- 每個建議展開成具體的改善步驟（1-2-3 步驟）
- 加上優先度標籤 (P0/P1/P2)
- 標記哪些可以自動修正、哪些需要人工判斷
- 加上預估修復時間

審閱結果：
{sdd_review_artifact 的輸出}
```

3. 將 `local_llm` 加工後的結果呈現給使用者
4. 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果

$ARGUMENTS
