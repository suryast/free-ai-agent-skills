#!/usr/bin/env bash
# scan-changes.sh — List recently changed memory files for archivist review
# Works with both git-tracked and non-git workspaces
set -euo pipefail

WORKSPACE="${WORKSPACE_ROOT:-$(pwd)}"

echo "=== Changed memory files (last 24h) ==="
if git -C "$WORKSPACE" rev-parse --git-dir > /dev/null 2>&1; then
    # Git-tracked workspace
    git -C "$WORKSPACE" log --since="24 hours ago" --name-only --pretty=format: -- memory/ MEMORY.md 2>/dev/null \
        | grep -v "^$" \
        | sort -u
else
    # Non-git workspace — use file modification time
    find "$WORKSPACE/memory" -name "*.md" -mtime -1 2>/dev/null | sort
fi

echo ""
echo "=== Inbox status ==="
if [[ -d "$WORKSPACE/memory/inbox" ]]; then
    for f in "$WORKSPACE/memory/inbox"/*.md; do
        if [[ -f "$f" ]]; then
            ITEMS=$(grep -c "^## \[" "$f" 2>/dev/null || echo 0)
            echo "  $(basename "$f"): $ITEMS pending items"
        fi
    done
else
    echo "  No inbox directory found. Create with: mkdir -p memory/inbox"
fi

echo ""
echo "=== Memory file stats ==="
echo "  Facts: $(find "$WORKSPACE/memory/facts/" -name "*.md" 2>/dev/null | wc -l) files"
if [[ -f "$WORKSPACE/memory/feedback/feedback.md" ]]; then
    echo "  Feedback rules: $(grep -c '^##' "$WORKSPACE/memory/feedback/feedback.md" 2>/dev/null || echo 0)"
fi
echo "  Daily logs: $(find "$WORKSPACE/memory" -maxdepth 1 -name "????-??-??.md" 2>/dev/null | wc -l) files"
if [[ -f "$WORKSPACE/memory/holds.md" ]]; then
    echo "  Holds: $(wc -l < "$WORKSPACE/memory/holds.md") lines"
fi
