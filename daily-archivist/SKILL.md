---
name: daily-archivist
version: 1.0.0
author: Polycat
tags: [knowledge-management, quality, coordination, memory]
license: MIT
platform: universal
description: >
  Daily knowledge quality audit and inter-agent coordination. Fact-checks memory files,
  fills knowledge gaps, cleans up quality issues, and routes findings to other agents via
  an inbox system. Triggers on: knowledge audit, fact check memory, clean up memory,
  archivist run, inbox check, memory quality.
---

> **Compatible with Claude Code, Codex CLI, Cursor, Windsurf, and any SKILL.md-compatible agent.**

# Daily Archivist

Audit knowledge quality. Fix what's safe. Flag what's not. Route findings to the right agent.

Inspired by the "daily-archivist" pattern: a scheduled agent that vets all knowledge files, fact-checks claims, fills gaps, cleans up quality — and leaves notes for other agents when it finds issues they should handle.

## What It Does

1. **Fact-check** — Verify claims in memory files against actual state (file counts, project status, config values)
2. **Gap-fill** — Find undocumented decisions, orphan references, missing rationale
3. **Clean up** — Fix formatting, remove duplicates, merge overlapping entries, archive stale content
4. **Route findings** — Leave notes in `memory/inbox/<agent>.md` for the appropriate agent
5. **Bug hunt** — Spot broken references, missing files, config drift, stale data

## Setup

### 1. Create the inbox directory

```bash
mkdir -p memory/inbox
# Create inbox files for each agent in your team
for agent in main coder reviewer researcher; do
  cat > memory/inbox/${agent}.md << 'EOF'
# Agent Inbox
<!-- Archivist leaves notes here. Read at session start, delete after acting. -->
EOF
done
```

### 2. Add inbox reading to your agent startup

Add this to your `AGENTS.md` or equivalent configuration:

```markdown
## Every Session
1. Read memory files and feedback
2. **Check inbox:** Read `memory/inbox/<your-agent>.md` — act on pending items, delete after handling
```

### 3. Configure the verification script

Copy `scripts/verify-facts.sh` and customize the checks for your project. See comments in the script for examples.

### 4. Schedule the cron

```bash
# Example for OpenClaw
openclaw cron add \
  --name daily-archivist \
  --cron "0 3 * * *" \
  --agent janitor \
  --model claude-haiku-4-5 \
  --timeout-seconds 300 \
  --announce \
  --message 'Daily knowledge audit. Run verify-facts.sh, scan changes, fix what is safe, route findings to agent inboxes.'
```

## Scope Control

To keep token cost low, only scan files changed recently:

```bash
# Files changed in last 24h (git-tracked workspaces)
git log --since="24 hours ago" --name-only --pretty=format: -- memory/ | sort -u

# Or by modification time (non-git workspaces)
find memory/ -name "*.md" -mtime -1
```

For large knowledge bases, rotate sections across days of the week (Monday = facts A-G, Tuesday = H-N, etc.).

## Inter-Agent Mailbox

```
memory/inbox/
├── main.md        — coordination / process issues
├── coder.md       — code bugs, broken references
├── reviewer.md    — content corrections, stale claims
├── researcher.md  — knowledge gaps, outdated intel
└── janitor.md     — cleanup tasks, infra issues
```

Adapt agent names to your team structure.

### Mailbox Entry Format

```markdown
## [2026-03-22] Subject line
Priority: LOW|MEDIUM|HIGH
Found: <what was found>
Action: <what the agent should do>
Evidence: <file:line or command output>
---
```

### Mailbox Rules

- Agents read their inbox at session start
- After acting on an item, delete it from the inbox
- Archivist only APPENDS to inboxes, never modifies existing entries
- Items older than 7 days should be auto-archived or deleted by a cleanup agent

## What to Auto-Fix (no approval needed)

- Formatting issues (trailing whitespace, inconsistent headers, broken markdown)
- Duplicate entries (identical content in multiple files)
- Stale dates in boilerplate (e.g., "Updated: 2025-01-01" when file was modified recently)
- Empty/stub files with no meaningful content

## What to Flag Only (route to agent)

- Incorrect facts (counts, status claims, configuration values)
- Missing documentation for active projects
- Broken file references in prompts or configs
- Security-adjacent findings (always route to security agent)
- Content quality issues (route to content/writing agent)
- Code bugs discovered during audit (route to coding agent)

## Verification Script

The included `scripts/verify-facts.sh` provides a template for mechanical fact-checking. Customize it for your workspace:

```bash
# Run the verification
bash scripts/verify-facts.sh
# Output: JSON array of findings
# [{"claim": "...", "file": "...", "actual": "...", "status": "ok|stale|wrong"}]
```

### Common Checks to Add

| Check | How |
|-------|-----|
| File/entity counts | `find <dir> -name "*.md" \| wc -l` vs. claimed count |
| Broken symlinks | `find ~/bin -type l ! -exec test -e {} \; -print` |
| Stale facts | `find memory/facts/ -mtime +30` |
| Duplicate rules | Compare `grep "^##" feedback.md \| wc -l` vs `sort -u \| wc -l` |
| Expired holds | Parse dates in holds file, compare to today |
| Config drift | Diff current config against documented values |

## Scan Changes Script

The included `scripts/scan-changes.sh` lists recently modified memory files and inbox status:

```bash
bash scripts/scan-changes.sh
# Output: changed files, inbox item counts, memory stats
```

## Example Cron Prompt

```
Daily knowledge audit. Be thorough but efficient.

1. Run the scan-changes script to see what changed in the last 24h
2. Run the verify-facts script to check claims against reality
3. For each finding:
   - If auto-fixable (formatting, stale dates): fix it directly
   - If needs another agent: append a note to the appropriate inbox file
4. For memory file fact corrections (counts, status): update directly
5. Report: X files scanned, Y issues found, Z auto-fixed, W routed to agents
6. If nothing found, reply NO_REPLY
```

## Design Principles

- **Scan, don't rewrite** — The archivist verifies and flags, it doesn't rewrite prose
- **Mechanical where possible** — Use scripts for counts/existence checks, not LLM judgment
- **Route, don't fix** — When in doubt, leave a note for the specialist agent
- **Cost-conscious** — Use the cheapest model that can run bash and compare strings
- **Idempotent** — Running twice should produce the same result (don't duplicate inbox entries)
