#!/usr/bin/env bash
# verify-facts.sh — Mechanically verify claims in memory files against actual state
# Outputs: JSON array of findings
# Customize the checks below for your workspace
set -euo pipefail

# Configure your workspace root
WORKSPACE="${WORKSPACE_ROOT:-$(pwd)}"
FINDINGS="[]"

add_finding() {
    local claim="$1" file="$2" actual="$3" status="$4"
    FINDINGS=$(echo "$FINDINGS" | python3 -c "
import json, sys
arr = json.load(sys.stdin)
arr.append({
    'claim': '''$claim''',
    'file': '''$file''',
    'actual': '''$actual''',
    'status': '''$status'''
})
print(json.dumps(arr))
")
}

echo "Verifying facts..." >&2

# ===== CUSTOMIZE THESE CHECKS FOR YOUR PROJECT =====

# Example 1: Check if a claimed file count matches reality
# Uncomment and adapt:
#
# ACTUAL_COUNT=$(find "$HOME/projects/my-project/data" -name "*.json" | wc -l)
# CLAIMED=$(grep -oP '\d+ data files' "$WORKSPACE/MEMORY.md" | grep -oP '\d+')
# if [[ -n "$CLAIMED" && "$ACTUAL_COUNT" != "$CLAIMED" ]]; then
#     add_finding "Data file count" "MEMORY.md" "$ACTUAL_COUNT" "stale"
# fi

# Example 2: Check for broken symlinks in a bin directory
BROKEN_LINKS=$(find ~/bin -type l ! -exec test -e {} \; -print 2>/dev/null | head -10)
if [[ -n "$BROKEN_LINKS" ]]; then
    COUNT=$(echo "$BROKEN_LINKS" | wc -l)
    add_finding "Broken symlinks in ~/bin" "~/bin" "${COUNT} broken links" "wrong"
fi

# Example 3: Check for stale fact files (>30 days old)
if [[ -d "$WORKSPACE/memory/facts/" ]]; then
    STALE_FACTS=$(find "$WORKSPACE/memory/facts/" -name "*.md" -mtime +30 2>/dev/null | wc -l)
    if [[ "$STALE_FACTS" -gt 0 ]]; then
        add_finding "Stale fact files (>30 days)" "memory/facts/" "${STALE_FACTS} files" "stale"
    fi
fi

# Example 4: Check for duplicate rules in feedback file
if [[ -f "$WORKSPACE/memory/feedback/feedback.md" ]]; then
    TOTAL=$(grep -c "^##" "$WORKSPACE/memory/feedback/feedback.md" 2>/dev/null || echo 0)
    UNIQUE=$(grep "^##" "$WORKSPACE/memory/feedback/feedback.md" 2>/dev/null | sort -u | wc -l)
    if [[ "$TOTAL" -gt "$UNIQUE" ]]; then
        DIFF=$((TOTAL - UNIQUE))
        add_finding "Duplicate feedback rules" "feedback.md" "${DIFF} duplicates" "stale"
    fi
fi

# Example 5: Check for expired holds
if [[ -f "$WORKSPACE/memory/holds.md" ]]; then
    TODAY=$(date -u +%Y-%m-%d)
    EXPIRED=$(grep -oP '\d{4}-\d{2}-\d{2}' "$WORKSPACE/memory/holds.md" 2>/dev/null | while read -r DATE; do
        if [[ "$DATE" < "$TODAY" ]]; then echo "$DATE"; fi
    done | wc -l)
    if [[ "$EXPIRED" -gt 0 ]]; then
        add_finding "Expired holds" "memory/holds.md" "${EXPIRED} expired" "stale"
    fi
fi

# Example 6: Check a project registry for missing directories
# Uncomment and adapt:
#
# if [[ -f "$WORKSPACE/projects-registry.json" ]]; then
#     python3 -c "
# import json, os
# reg = json.load(open('$WORKSPACE/projects-registry.json'))
# projects = reg if isinstance(reg, list) else reg.get('projects', [])
# for p in projects:
#     path = p.get('path', '')
#     if path and not os.path.isdir(os.path.expanduser(path)):
#         print(f'MISSING:{path}')
# " 2>/dev/null | while read -r line; do
#         add_finding "Missing project directory" "projects-registry.json" "${line#MISSING:}" "wrong"
#     done
# fi

# ===== END CUSTOMIZATION =====

# Output findings as formatted JSON
echo "$FINDINGS" | python3 -m json.tool

# Summary to stderr
COUNT=$(echo "$FINDINGS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
echo "" >&2
echo "Found $COUNT issues" >&2
