#!/usr/bin/env bash
# Validator for speckit-checklist preset output.
# Reads content from stdin, prints violations to stderr.

set -u
CONTENT=$(cat)
VIOLATIONS=()

# Rule 1: must have all 4 required category headers
REQUIRED_HEADERS=("Requirements Completeness" "Requirements Clarity" "Testability" "Constitutional Compliance")
for header in "${REQUIRED_HEADERS[@]}"; do
  if ! echo "$CONTENT" | grep -qF "$header"; then
    VIOLATIONS+=("R1: 缺少分類「$header」")
  fi
done

# Rule 2: must have checkbox items
CHECKBOX_COUNT=$(echo "$CONTENT" | grep -cE '^\s*-\s*\[\s*\]')
if [[ $CHECKBOX_COUNT -lt 8 ]]; then
  VIOLATIONS+=("R2: checkbox 過少 ($CHECKBOX_COUNT)，每類至少 2 項")
fi

# Rule 3: must NOT look like a re-written plan (reject if has Implementation Phases / ADR reproduction)
if echo "$CONTENT" | grep -qE '^##\s*(Implementation Phases|Phase [0-9]+:)'; then
  VIOLATIONS+=("R3: 輸出像 plan.md 而非 checklist（含 Implementation Phases）")
fi

# Rule 4: must reference spec/plan content (US IDs, NFR IDs, ADR IDs)
if ! echo "$CONTENT" | grep -qE '\b(US[0-9]+|NFR-?[0-9]+|ADR-?[0-9]+)\b'; then
  VIOLATIONS+=("R4: 未引用 spec/plan 具體 IDs（US1/NFR-1/ADR-001）")
fi

if [[ ${#VIOLATIONS[@]} -gt 0 ]]; then
  echo "❌ speckit-checklist 驗證失敗 (${#VIOLATIONS[@]} 項):" >&2
  for v in "${VIOLATIONS[@]}"; do
    echo "  - $v" >&2
  done
  exit 1
fi

echo "✅ speckit-checklist 驗證通過 ($CHECKBOX_COUNT 個檢查項)" >&2
exit 0
