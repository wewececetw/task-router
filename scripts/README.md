# scripts/

task-router 的 shell helper scripts。

## call-omlx.sh

呼叫本地 oMLX 模型的核心 helper。

```bash
./scripts/call-omlx.sh "你的 prompt"
./scripts/call-omlx.sh "prompt" --system "system prompt"
./scripts/call-omlx.sh "prompt" --max-tokens 2048 --temperature 0.3
```

**環境變數:**
- `OMLX_API_KEY` (必要) - oMLX API key
- `OMLX_BASE_URL` (預設 `http://127.0.0.1:9000/v1`)
- `OMLX_MODEL` (預設 `Qwen3.5-9B-MLX-4bit`)

**Exit codes:**
- `0` 成功
- `1` oMLX server 離線（fallback）
- `2` API 回傳錯誤
- `3` 缺少參數

**使用紀錄：** 每次呼叫會 append 到 `~/.task-router/usage.log`

## usage-stats.sh

檢視使用統計。

```bash
./scripts/usage-stats.sh           # 全部紀錄
./scripts/usage-stats.sh --today   # 只看今天
./scripts/usage-stats.sh --week    # 最近 7 天
```

## 依賴

- `curl` (macOS 內建)
- `jq` (`brew install jq`)
