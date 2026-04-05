---
description: "用本地模型為程式碼加 docstring / JSDoc / 型別註解"
---

為程式碼加上文件註解。

步驟：
1. 用 Read 讀取指定的檔案
2. 用 Bash 執行 `./scripts/call-omlx.sh` 產生註解：

```bash
./scripts/call-omlx.sh "為以下程式碼的每個 public function/class/method 加上文件註解。
- Python: 用 Google style docstring
- TypeScript/JavaScript: 用 JSDoc
- Go: 用 godoc 格式
保留原始程式碼，只加上註解。

程式碼：
{檔案內容}" --max-tokens 4096 --temperature 0.3
```

3. 審查輸出品質，確認準確性後用 Write 寫回檔案
4. 如果 FALLBACK，你自己寫註解

$ARGUMENTS
