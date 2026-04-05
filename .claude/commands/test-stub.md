---
description: "用本地模型生成測試骨架（test stubs）"
---

生成測試骨架。

步驟：
1. 用 Read 讀取指定的原始碼檔案
2. 用 Bash 執行 `./scripts/call-omlx.sh` 生成測試：

```bash
./scripts/call-omlx.sh "為以下程式碼生成測試骨架。
- 每個 public function 至少 2 個 test case（正常 + 邊界）
- 使用對應的測試框架（pytest / jest / go test）
- 只生成骨架，assertion 用 TODO 標記
- 包含必要的 import 和 setup

程式碼：
{檔案內容}" --max-tokens 4096
```

3. 用 Write 寫入對應的測試檔案（`_test.py` / `.test.ts` / `_test.go`）
4. 審查並修正明顯錯誤
5. 如果 FALLBACK，你自己寫測試骨架

$ARGUMENTS
