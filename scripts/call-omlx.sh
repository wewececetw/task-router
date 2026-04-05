#!/usr/bin/env bash
# call-omlx.sh — 呼叫本地 oMLX 模型的 helper script
#
# Usage:
#   ./call-omlx.sh "你的 prompt"
#   ./call-omlx.sh "prompt" --system "system prompt"
#   ./call-omlx.sh "prompt" --max-tokens 2048 --temperature 0.3
#   ./call-omlx.sh "prompt" --preset speckit-tasks
#
# Presets (from scripts/presets/*.md):
#   speckit-tasks      從 plan.md 產 tasks.md（含 few-shot 範例）
#   speckit-checklist  從 spec + plan 產品質檢查清單
#   speckit-analyze    跨檔案一致性分析
#
# Env vars:
#   OMLX_API_KEY    (required) oMLX API key
#   OMLX_BASE_URL   (default: http://127.0.0.1:9000/v1)
#   OMLX_MODEL      (default: Qwen3.5-9B-MLX-4bit)
#
# Exit codes:
#   0  成功（且 preset 輸出通過 validator）
#   1  oMLX server 離線
#   2  API 回傳錯誤
#   3  缺少 prompt 參數
#   4  preset 檔案不存在
#   5  preset 輸出不符規範（Claude 應接手）

set -euo pipefail

# ---------- Config ----------
OMLX_BASE_URL="${OMLX_BASE_URL:-http://127.0.0.1:9000/v1}"
OMLX_MODEL="${OMLX_MODEL:-Qwen3.5-9B-MLX-4bit}"
OMLX_API_KEY="${OMLX_API_KEY:-}"
USAGE_LOG="${HOME}/.task-router/usage.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRESETS_DIR="${SCRIPT_DIR}/presets"

# ---------- Parse args ----------
PROMPT=""
SYSTEM=""
PRESET=""
MAX_TOKENS=4096
TEMPERATURE=0.7

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system)
      SYSTEM="$2"; shift 2 ;;
    --preset)
      PRESET="$2"; shift 2 ;;
    --max-tokens)
      MAX_TOKENS="$2"; shift 2 ;;
    --temperature)
      TEMPERATURE="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,25p' "${BASH_SOURCE[0]}"; exit 0 ;;
    --*)
      # 認得的 flag 已 match；未知 --flag 且長度 < 20 視為真 flag（拒絕）
      # 長度 >= 20 或含換行 → 視為 prompt 內容（例如 "--- spec.md ---\n..."）
      if [[ ${#1} -ge 20 ]] || [[ "$1" == *$'\n'* ]]; then
        if [[ -z "$PROMPT" ]]; then PROMPT="$1"; else PROMPT="$PROMPT $1"; fi
        shift
      else
        echo "❌ 未知參數: $1" >&2; exit 3
      fi
      ;;
    *)
      if [[ -z "$PROMPT" ]]; then PROMPT="$1"; else PROMPT="$PROMPT $1"; fi
      shift ;;
  esac
done

# ---------- Load preset ----------
if [[ -n "$PRESET" ]]; then
  PRESET_FILE="${PRESETS_DIR}/${PRESET}.md"
  if [[ ! -f "$PRESET_FILE" ]]; then
    echo "❌ preset 不存在: $PRESET_FILE" >&2
    echo "可用 presets: $(ls "$PRESETS_DIR" 2>/dev/null | sed 's/\.md$//' | tr '\n' ' ')" >&2
    exit 4
  fi
  # preset 覆蓋 --system（presets 本就是 system prompt）
  SYSTEM="$(cat "$PRESET_FILE")"
  # preset 任務通常需要結構化輸出，降低溫度
  TEMPERATURE=0.2
fi

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

# ---------- Validate preset output ----------
VALIDATOR_FILE="${SCRIPT_DIR}/validators/${PRESET}.sh"
if [[ -n "$PRESET" ]] && [[ -x "$VALIDATOR_FILE" ]]; then
  if ! echo "$CONTENT" | "$VALIDATOR_FILE"; then
    echo "" >&2
    echo "❌ oMLX FALLBACK: preset '$PRESET' 產出不符 Spec Kit 規範" >&2
    echo "建議 Claude 接手處理此任務" >&2
    exit 5
  fi
fi

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
