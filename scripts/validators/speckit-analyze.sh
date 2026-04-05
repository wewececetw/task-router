#!/usr/bin/env bash
# Validator for speckit-analyze preset output.

set -u
CONTENT=$(cat)
VIOLATIONS=()

# Rule 1: must have 3 required section headers
REQUIRED_HEADERS=("Consistency Issues" "Coverage Gaps" "Quality Concerns")
for header in "${REQUIRED_HEADERS[@]}"; do
  if ! echo "$CONTENT" | grep -qF "$header"; then
    VIOLATIONS+=("R1: 缺少分類「$header」")
  fi
done

# Rule 2: must have severity markers
if ! echo "$CONTENT" | grep -qE '🔴|🟡|🟢'; then
  VIOLATIONS+=("R2: 缺少嚴重度標記（🔴/🟡/🟢）")
fi

# Rule 3: must cite artifact locations
if ! echo "$CONTENT" | grep -qE '(spec\.md|plan\.md|tasks\.md)'; then
  VIOLATIONS+=("R3: 未引用具體 artifact 位置")
fi

if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
  echo "❌ speckit-analyze 驗證失敗 (${#VIOLATIONS[@]} 項):" >&2
  for v in "${VIOLATIONS[@]}"; do
    echo "  - $v" >&2
  done
  exit 1
fi

echo "✅ speckit-analyze 驗證通過" >&2
exit 0
