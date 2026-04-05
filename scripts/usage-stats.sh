#!/usr/bin/env bash
# usage-stats.sh — 顯示 call-omlx.sh 的使用統計
#
# Usage:
#   ./scripts/usage-stats.sh           # 顯示所有統計
#   ./scripts/usage-stats.sh --today   # 只顯示今天
#   ./scripts/usage-stats.sh --week    # 最近 7 天

set -euo pipefail

USAGE_LOG="${HOME}/.task-router/usage.log"

if [[ ! -f "$USAGE_LOG" ]]; then
  echo "尚無使用紀錄（$USAGE_LOG 不存在）"
  echo "先跑一次 ./scripts/call-omlx.sh 建立紀錄"
  exit 0
fi

# Filter by time range
FILTER="${1:-all}"
case "$FILTER" in
  --today)
    TODAY=$(date +"%Y-%m-%d")
    LINES=$(grep "^${TODAY}" "$USAGE_LOG" || echo "")
    RANGE="今天 (${TODAY})"
    ;;
  --week)
    WEEK_AGO=$(date -v-7d +"%Y-%m-%d")
    LINES=$(awk -v since="$WEEK_AGO" '$1 >= since' "$USAGE_LOG")
    RANGE="最近 7 天 (since ${WEEK_AGO})"
    ;;
  *)
    LINES=$(cat "$USAGE_LOG")
    RANGE="全部紀錄"
    ;;
esac

if [[ -z "$LINES" ]]; then
  echo "範圍內無使用紀錄: $RANGE"
  exit 0
fi

# 計算統計
COUNT=$(echo "$LINES" | wc -l | tr -d ' ')
TOTAL_ELAPSED=$(echo "$LINES" | awk -F'|' '{gsub(/s/,"",$2); sum+=$2} END {print sum}')
TOTAL_INPUT=$(echo "$LINES" | awk -F'|' '{split($3,a,"→"); gsub(/ tokens/,"",a[1]); sum+=a[1]} END {print sum}')
TOTAL_OUTPUT=$(echo "$LINES" | awk -F'|' '{split($3,a,"→"); gsub(/ tokens/,"",a[2]); sum+=a[2]} END {print sum}')

cat << EOF
📊 task-router 使用統計
├─ 範圍: $RANGE
├─ 呼叫次數: $COUNT
├─ 總耗時: ${TOTAL_ELAPSED}s
├─ 輸入 tokens: ~${TOTAL_INPUT}
├─ 輸出 tokens: ~${TOTAL_OUTPUT}
└─ 估算節省: ~$((TOTAL_INPUT + TOTAL_OUTPUT)) Claude tokens

💡 最近 5 筆：
EOF

echo "$LINES" | tail -5 | while IFS='|' read -r ts elapsed tokens prompt; do
  echo "   ${ts} |${tokens} |${prompt}"
done
