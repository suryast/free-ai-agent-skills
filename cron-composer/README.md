# Cron Composer

> Composable block system for OpenClaw cron job prompts.

When you have many OpenClaw cron jobs, you end up copy-pasting the same instructions everywhere: git identity, error handling, backup patterns. When something needs updating (a path changes, a command syntax shifts), you have to edit every cron.

**Cron Composer** solves this by letting you define reusable **blocks** and assemble cron prompts from them via a simple YAML **manifest**.

## Features

- 📦 **Block composition** — combine env, ops, and pattern blocks per cron
- 🔧 **Variable substitution** — `{{VAR}}` placeholders resolved per-cron
- 🧪 **Dry-run mode** — preview assembled prompts before applying
- 🔍 **Drift detection** — `sync` and `diff` commands to spot stale crons
- ✅ **Lint validation** — catch missing blocks, undefined vars, bad UUIDs
- 📊 **Stats dashboard** — block usage frequency and composition metrics

## Installation

Copy this skill directory into your OpenClaw skills folder:

```bash
cp -r cron-composer ~/.openclaw/workspace/skills/
```

Or clone the repo:

```bash
git clone https://github.com/suryast/openclaw-cron-composer
cp -r openclaw-cron-composer ~/.openclaw/workspace/skills/cron-composer
```

## Quick Start

```bash
SKILL="$HOME/.openclaw/workspace/skills/cron-composer"

# See example crons
python3 "$SKILL/scripts/cron-compose.py" "$SKILL/example-manifest.yaml" list

# Preview assembled prompt (safe — doesn't apply)
python3 "$SKILL/scripts/cron-compose.py" "$SKILL/example-manifest.yaml" apply daily-health-check --dry-run

# Validate example manifest
python3 "$SKILL/scripts/cron-compose.py" "$SKILL/example-manifest.yaml" lint
```

## Usage

### 1. Create your manifest

Copy `example-manifest.yaml` and adapt it:

```yaml
# my-manifest.yaml

crons:
  my-daily-task:
    id: "uuid-from-openclaw-cron-list"   # openclaw cron list
    blocks:
      - env/error-handling
      - ops/git-commit
    vars:
      REPO: /home/user/myproject
      GIT_NAME: My Bot
      GIT_EMAIL: bot@example.com
      BRANCH: main
    task: |
      Check for new items in {{REPO}}/inbox/ and process them.
```

### 2. Run commands

```bash
MANIFEST="$HOME/my-manifest.yaml"
SCRIPT="$HOME/.openclaw/workspace/skills/cron-composer/scripts/cron-compose.py"

python3 $SCRIPT $MANIFEST list                          # list crons
python3 $SCRIPT $MANIFEST apply my-daily-task --dry-run # preview
python3 $SCRIPT $MANIFEST apply my-daily-task           # apply
python3 $SCRIPT $MANIFEST apply --all                   # apply all
python3 $SCRIPT $MANIFEST lint                          # validate
python3 $SCRIPT $MANIFEST sync                          # check drift
python3 $SCRIPT $MANIFEST diff                          # diff vs live
python3 $SCRIPT $MANIFEST stats                         # usage dashboard
```

### 3. Write your own blocks

Create `blocks/<category>/<name>.md`:

```markdown
## My Shared Block

Instructions that apply to every cron that includes this block.
Use {{MY_VAR}} for anything that varies per cron.
```

Reference it in your manifest as `<category>/<name>` (no `.md`).

## Block Categories

| Category | Purpose |
|----------|---------|
| `env/` | Environment constraints prepended to every job (error handling, workspace paths) |
| `ops/` | Reusable operations (git commit, file backup, deploy) |
| `patterns/` | Multi-step task shape templates (check-and-fix, content pipeline) |

## Manifest Reference

```yaml
blocks_dir: /optional/custom/blocks/path   # defaults to blocks/ next to manifest

crons:
  cron-name:
    id: "uuid"          # from `openclaw cron list`
    blocks:             # applied in order, then task appended
      - env/error-handling
      - ops/git-commit
    vars:               # substituted as {{KEY}} in blocks + task
      KEY: value
    task: |             # cron-specific instructions (not repeated in blocks)
      What this cron does specifically.
```

## Included Blocks

| Block | What it does |
|-------|-------------|
| `env/error-handling` | Stop on failure, capture stderr, report summary |
| `env/workspace-context` | Working directory, path verification conventions |
| `ops/git-commit` | Stage, commit (with configurable identity), pull-rebase, push |
| `ops/file-backup` | Timestamped backup before modification |
| `patterns/check-and-fix` | Check → evaluate → fix → verify → report pattern |

## Requirements

- Python 3.10+
- `pyyaml` (optional; falls back to subprocess if missing)
- `openclaw` CLI in PATH (for `apply`, `sync`, `diff`)

## License

MIT — see [LICENSE](LICENSE).
