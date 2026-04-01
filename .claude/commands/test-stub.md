---
description: "用本地模型生成測試骨架（test stubs）"
---

**請使用 local_llm MCP tool** 生成測試骨架。

步驟：
1. 讀取指定的原始碼檔案
2. 用 `local_llm` tool 生成測試，prompt：

```
為以下程式碼生成測試骨架。
- 每個 public function 至少 2 個 test case（正常 + 邊界）
- 使用對應的測試框架（pytest / jest / go test）
- 只生成骨架，assertion 用 TODO 標記
- 包含必要的 import 和 setup

程式碼：
{檔案內容}
```

3. 寫入對應的測試檔案（`_test.py` / `.test.ts` / `_test.go`）
4. 你自己審查結果，修正明顯的錯誤

$ARGUMENTS
