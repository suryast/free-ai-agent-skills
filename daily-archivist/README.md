# Daily Archivist

**A scheduled agent that audits your knowledge quality and coordinates fixes across your agent team.**

Inspired by the pattern: instead of letting knowledge files drift and decay, run a daily archivist that fact-checks claims, fills gaps, cleans up quality issues, and leaves notes for other agents via an inbox system.

## What It Does

- 🔍 **Fact-checks** memory files against actual state (file counts, project status, configs)
- 📝 **Fills gaps** in documentation (orphan references, missing rationale)
- 🧹 **Cleans up** formatting, duplicates, stale entries
- 📬 **Routes findings** to the right agent via `memory/inbox/<agent>.md`
- 🐛 **Bug hunts** for broken references, missing files, config drift

## Quick Start

1. Copy `SKILL.md` and `scripts/` to your skills directory
2. Create `memory/inbox/` with a `.md` file per agent
3. Customize `scripts/verify-facts.sh` with checks for your project
4. Schedule as a daily cron job

See `SKILL.md` for detailed setup instructions.

## Inter-Agent Mailbox

The killer feature: agents can leave notes for each other.

```
memory/inbox/
├── coder.md       — "Found 3 duplicate slugs in entities.json"
├── reviewer.md    — "Article count is stale — 97 not 90"
├── security.md    — "Hardcoded date in PII scan config"
└── researcher.md  — "Missing market data for Q1 2026"
```

Each agent reads their inbox at session start, acts on items, and deletes them.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/verify-facts.sh` | Mechanical fact-checking (counts, existence, dates) |
| `scripts/scan-changes.sh` | List recently changed files + inbox status |

## Requirements

- Bash, Python 3 (for JSON output)
- Git (optional, for change detection)
- Any SKILL.md-compatible agent platform

## License

MIT — See [LICENSE](../LICENSE)
