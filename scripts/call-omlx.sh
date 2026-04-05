#!/usr/bin/env bash
# call-omlx.sh — 呼叫本地 oMLX 模型的 helper script
#
# Usage:
#   ./call-omlx.sh "你的 prompt"
#   ./call-omlx.sh "prompt" --system "system prompt"
#   ./call-omlx.sh "prompt" --max-tokens 2048 --temperature 0.3
#
# Env vars:
#   OMLX_API_KEY    (required) oMLX API key
#   OMLX_BASE_URL   (default: http://127.0.0.1:9000/v1)
#   OMLX_MODEL      (default: Qwen3.5-9B-MLX-4bit)
#
# Exit codes:
#   0  成功
#   1  oMLX server 離線
#   2  API 回傳錯誤
#   3  缺少 prompt 參數

set -euo pipefail

# ---------- Config ----------
OMLX_BASE_URL="${OMLX_BASE_URL:-http://127.0.0.1:9000/v1}"
OMLX_MODEL="${OMLX_MODEL:-Qwen3.5-9B-MLX-4bit}"
OMLX_API_KEY="${OMLX_API_KEY:-}"
USAGE_LOG="${HOME}/.task-router/usage.log"

# ---------- Parse args ----------
PROMPT=""
SYSTEM=""
MAX_TOKENS=4096
TEMPERATURE=0.7

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system)
      SYSTEM="$2"; shift 2 ;;
    --max-tokens)
      MAX_TOKENS="$2"; shift 2 ;;
    --temperature)
      TEMPERATURE="$2"; shift 2 ;;
    --*)
      echo "❌ 未知參數: $1" >&2; exit 3 ;;
    *)
      if [[ -z "$PROMPT" ]]; then PROMPT="$1"; else PROMPT="$PROMPT $1"; fi
      shift ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "❌ 缺少 prompt 參數" >&2
  echo "Usage: $0 \"your prompt\" [--system \"sys\"] [--max-tokens N] [--temperature F]" >&2
  exit 3
fi

# ---------- Build JSON payload ----------
# 用 jq 組 JSON，避免 shell quoting 問題
MESSAGES_JSON=$(
  if [[ -n "$SYSTEM" ]]; then
    jq -n --arg sys "$SYSTEM" --arg usr "$PROMPT" \
      '[{role: "system", content: $sys}, {role: "user", content: $usr}]'
  else
    jq -n --arg usr "$PROMPT" \
      '[{role: "user", content: $usr}]'
  fi
)

PAYLOAD=$(jq -n \
  --arg model "$OMLX_MODEL" \
  --argjson messages "$MESSAGES_JSON" \
  --argjson max_tokens "$MAX_TOKENS" \
  --argjson temperature "$TEMPERATURE" \
  '{model: $model, messages: $messages, max_tokens: $max_tokens, temperature: $temperature, chat_template_kwargs: {enable_thinking: false}}')

# ---------- Call oMLX ----------
START_TIME=$(date +%s)

set +e  # 允許 curl 失敗，自己處理
RESPONSE=$(curl -s --max-time 120 -w "\n%{http_code}" \
  "${OMLX_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OMLX_API_KEY}" \
  -d "$PAYLOAD" 2>&1)
CURL_EXIT=$?
set -e

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

# curl 失敗（連不上、timeout）
if [[ $CURL_EXIT -ne 0 ]]; then
  echo "❌ oMLX FALLBACK: 無法連線到 ${OMLX_BASE_URL} (curl exit $CURL_EXIT)" >&2
  echo "建議 Claude 接手處理此任務" >&2
  exit 1
fi

# 最後一行是 HTTP status code
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

# HTTP status 000 = connection refused
if [[ "$HTTP_CODE" == "000" ]]; then
  echo "❌ oMLX FALLBACK: 無法連線到 ${OMLX_BASE_URL}" >&2
  echo "建議 Claude 接手處理此任務" >&2
  exit 1
fi

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "❌ oMLX API 錯誤 (HTTP $HTTP_CODE)" >&2
  echo "$BODY" >&2
  exit 2
fi

# ---------- Extract content + filter <think> tags ----------
CONTENT=$(echo "$BODY" | jq -r '.choices[0].message.content' | \
  sed -E 's/<think>.*<\/think>//g' | \
  sed -E '/^<think>/,/^<\/think>/d')

# ---------- Token estimation ----------
PROMPT_CHARS=${#PROMPT}
OUTPUT_CHARS=${#CONTENT}
# 粗估：中文 ~1.5 char/token，英文 ~4 char/token，取平均 2.5
INPUT_TOKENS=$((PROMPT_CHARS / 3))
OUTPUT_TOKENS=$((OUTPUT_CHARS / 3))

# ---------- Log usage ----------
mkdir -p "$(dirname "$USAGE_LOG")"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
PROMPT_PREVIEW=$(echo "$PROMPT" | head -c 60 | tr '\n' ' ')
echo "${TIMESTAMP} | ${ELAPSED}s | ${INPUT_TOKENS}→${OUTPUT_TOKENS} tokens | ${PROMPT_PREVIEW}" >> "$USAGE_LOG"

# ---------- Output ----------
cat << EOF
✅ oMLX | ${OMLX_MODEL}
├─ 任務: ${PROMPT:0:80}$([ ${#PROMPT} -gt 80 ] && echo "...")
├─ 輸入: ~${INPUT_TOKENS} tokens → 輸出: ~${OUTPUT_TOKENS} tokens
└─ 耗時: ${ELAPSED}s
──────────────────────────────────────────────────
${CONTENT}
EOF
