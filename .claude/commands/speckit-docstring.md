---
description: "用本地模型為程式碼加 docstring / JSDoc / 型別註解"
---

**請使用 local_llm MCP tool** 為以下程式碼加上文件註解。

步驟：
1. 讀取指定的檔案
2. 用 `local_llm` tool 生成 docstring，prompt：

```
為以下程式碼的每個 public function/class/method 加上文件註解。
- Python: 用 Google style docstring
- TypeScript/JavaScript: 用 JSDoc
- Go: 用 godoc 格式
保留原始程式碼，只加上註解。

程式碼：
{檔案內容}
```

3. 你自己審查結果，確認準確性後寫回檔案

$ARGUMENTS
