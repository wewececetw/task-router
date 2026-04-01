---
description: "用 vibe-lens 生成品質檢查清單，再用本地模型加工"
---

你現在執行 **checklist 階段**。

步驟：
1. 先呼叫 vibe-lens MCP tool `sdd_checklist`，傳入 feature_name（從 $ARGUMENTS 取得）
2. 取得 `sdd_checklist` 的結果後，用 `local_llm` MCP tool 做後處理，prompt：

```
你是 QA 助手。以下是 vibe-lens 產出的品質檢查清單。
請做以下加工：
- 每個檢查項擴展成可執行的測試場景（Given/When/Then）
- 加上測試類型標籤（unit / integration / e2e）
- 標記自動化測試可覆蓋的項目
- 補充邊界條件和錯誤處理的檢查項

檢查清單：
{sdd_checklist 的輸出}
```

3. 將 `local_llm` 加工後的結果呈現給使用者
4. 如果 `local_llm` 回傳 FALLBACK 警告，直接呈現 vibe-lens 原始結果
5. 如果品質不夠好，你自己修正

$ARGUMENTS
