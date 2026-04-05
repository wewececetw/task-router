#!/usr/bin/env bash
# Validator for speckit-tasks preset output.
# Reads content from stdin, prints violations to stderr.
# Exit 0 = passes; exit != 0 = violates Spec Kit rules.

set -u
CONTENT=$(cat)
VIOLATIONS=()

# Rule 1: must contain T-prefixed sequential IDs (T001, T002, ...)
if ! echo "$CONTENT" | grep -qE '^\s*-\s*\[\s*\]\s*T[0-9]{3}'; then
  VIOLATIONS+=("R1: 缺少 T001-style task IDs（global sequential）")
fi

# Rule 2: MUST NOT use phase-prefixed IDs
if echo "$CONTENT" | grep -qE '\b(SETUP|FOUND|POLISH|US1|US2|US3|US4)-[0-9]+'; then
  VIOLATIONS+=("R2: 發現 phase-prefixed IDs（應該是 T001 全域編號）")
fi

# Rule 3: MUST NOT tag Setup/Foundational/Polish with story labels
if echo "$CONTENT" | grep -qE '\[\s*(Setup|SETUP|Foundational|FOUND|FOUNDATIONAL|Polish|POLISH)\s*\]'; then
  VIOLATIONS+=("R3: Setup/Foundational/Polish phase 不該加標籤")
fi

# Rule 4: must have Dependencies section
if ! echo "$CONTENT" | grep -qiE '^#+\s*Dependencies'; then
  VIOLATIONS+=("R4: 缺少 Dependencies 區塊")
fi

# Rule 5: must have at least one [P] parallel marker (most features have parallelizable work)
if ! echo "$CONTENT" | grep -qE '\[\s*P\s*\]'; then
  VIOLATIONS+=("R5: 完全沒有 [P] 平行標記（檢查是否真無可平行任務）")
fi

# Rule 6: task count sanity (5-40 tasks)
TASK_COUNT=$(echo "$CONTENT" | grep -cE '^\s*-\s*\[\s*\]\s*T[0-9]{3}')
if [[ $TASK_COUNT -lt 5 ]]; then
  VIOLATIONS+=("R6: 任務過少 ($TASK_COUNT)，可能拆解不完整")
elif [[ $TASK_COUNT -gt 40 ]]; then
  VIOLATIONS+=("R6: 任務過多 ($TASK_COUNT)，可能過度拆解")
fi

if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
  echo "❌ speckit-tasks 驗證失敗 (${#VIOLATIONS[@]} 項):" >&2
  for v in "${VIOLATIONS[@]}"; do
    echo "  - $v" >&2
  done
  exit 1
fi

echo "✅ speckit-tasks 驗證通過 ($TASK_COUNT 個任務)" >&2
exit 0
