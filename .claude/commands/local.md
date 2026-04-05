---
description: "把任何任務丟給本地 oMLX 模型處理"
---

把使用者的任務送給本地 oMLX 模型處理。

步驟：
1. 用 Bash 執行 `./scripts/call-omlx.sh` 並傳入使用者任務
2. 將本地模型的輸出直接呈現給使用者
3. 如果 helper script 回傳 `❌ oMLX FALLBACK`，你接手自己處理

範例指令：
```bash
./scripts/call-omlx.sh "使用者任務內容"
```

若需要 system prompt、調整參數：
```bash
./scripts/call-omlx.sh "任務" --system "系統提示" --max-tokens 2048 --temperature 0.3
```

使用者任務：
$ARGUMENTS
