---
name: cron-composer
description: >
  Composable block system for OpenClaw cron job prompts. Assembles cron prompts from reusable
  markdown blocks so cross-cutting changes (e.g. git identity, error handling) only need updating
  in one place. Use when managing multiple cron jobs, authoring a cron manifest, composing blocks
  into prompts, running cron-compose.py, or asking about cron prompt assembly, block composition,
  manifest format, or `apply`/`lint`/`diff`/`sync`/`stats` commands.
---

# Cron Composer

🧩 STARTER_CHARACTER = 🧩

Composable block system for OpenClaw cron job prompts. Define reusable blocks once; assemble prompts from them via a YAML manifest.

**Why:** When you have many cron jobs sharing common behaviours (git identity, error handling, backup patterns), editing each prompt individually is error-prone. Cron Composer centralises shared logic in block files and assembles final prompts on demand.

## Quick Start

```bash
# Install: copy skill to your skills directory (already done if you're reading this)
SKILL_DIR="$HOME/.openclaw/workspace/skills/cron-composer"

# List all crons in manifest
python3 "$SKILL_DIR/scripts/cron-compose.py" "$SKILL_DIR/example-manifest.yaml" list

# Preview assembled prompt (dry-run)
python3 "$SKILL_DIR/scripts/cron-compose.py" /path/to/my-manifest.yaml apply my-cron --dry-run

# Apply one cron
python3 "$SKILL_DIR/scripts/cron-compose.py" /path/to/my-manifest.yaml apply my-cron

# Apply all crons
python3 "$SKILL_DIR/scripts/cron-compose.py" /path/to/my-manifest.yaml apply --all

# Validate manifest
python3 "$SKILL_DIR/scripts/cron-compose.py" /path/to/my-manifest.yaml lint
```

## Key Concepts

- **Blocks** — Markdown files in `blocks/<category>/`. Prepended to every cron that references them.
- **Manifest** — YAML file mapping cron names → block lists + task prompt + variables.
- **Variables** — `{{VAR}}` placeholders in blocks/tasks, resolved from the `vars:` section per cron.

## Manifest Format

```yaml
blocks_dir: /path/to/your/blocks   # absolute or relative to manifest file

crons:
  my-cron-name:
    id: "uuid-from-openclaw-cron-list"
    blocks:
      - env/error-handling        # prepended first
      - env/workspace-context
      - ops/git-commit
      - ops/file-backup
    vars:
      PROJECT: /home/user/myproject   # replaces {{PROJECT}} in blocks + task
      SITE: my-site
    task: |
      Task-specific instructions only. Don't repeat what blocks already cover.
      Check {{PROJECT}}/status.txt and report findings.
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | Tabular view: name, ID, blocks |
| `apply <name>` | Assemble + push prompt to openclaw cron |
| `apply --all` | Apply every cron in manifest |
| `apply <name> --dry-run` | Print assembled prompt without applying |
| `apply <name> --diff` | Show line diff vs live before applying |
| `lint` | Validate UUIDs, block files, var coverage |
| `sync` | Detect drift between manifest and live crons |
| `diff [name]` | Summarise line changes vs live prompt |
| `stats` | Block usage dashboard |

## Block Categories (convention)

| Category | Purpose | Example blocks |
|----------|---------|---------------|
| `env/` | Environment constraints, always-prepended | `error-handling`, `workspace-context` |
| `ops/` | Reusable operations | `git-commit`, `file-backup` |
| `patterns/` | Multi-step task shape templates | `check-and-fix` |

## Writing Blocks

1. Create `blocks/<category>/<name>.md`
2. Write reusable instructions. Use `{{VAR}}` for anything job-specific.
3. Reference as `<category>/<name>` in manifests (no `.md` extension).

**Good blocks** cover one concern (commit, backup, error handling). Keep them short and composable.

## blocks_dir Resolution

The assembler resolves blocks relative to `blocks_dir` in the manifest. You can:
- Set `blocks_dir:` to an absolute path
- Set `blocks_dir:` relative to the manifest file location
- Omit `blocks_dir:` — defaults to a `blocks/` directory next to the manifest

## Example

See `example-manifest.yaml` and `blocks/` in this skill directory for working examples.
