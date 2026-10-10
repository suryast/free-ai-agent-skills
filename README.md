# 🐱 Free AI Agent Skills

[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-blue)](https://docs.anthropic.com/en/docs/claude-code)
[![Codex CLI](https://img.shields.io/badge/Codex_CLI-compatible-green)](https://github.com/openai/codex)
[![SKILL.md](https://img.shields.io/badge/SKILL.md-standard-orange)](https://docs.anthropic.com/en/docs/claude-code/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**12 complete skill packages** for AI coding agents: nine original operational skills and three portable, fixture-tested additions. The original collection grew from running **8 specialist agents 24/7 in production**; the new examples are synthetic rehearsals, not claims of live deployment or agent integration.

Designed for agents that support the open Agent Skills format. Package discovery and runtime tools vary by agent; see Installation and each skill's compatibility requirements.

🔗 **[skillpacks.dev](https://skillpacks.dev)** · **[GitHub](https://github.com/suryast/free-ai-agent-skills)** · ☕ **[Ko-fi](https://ko-fi.com/srvzt)**

---

## Skills

| Skill | What It Does | Triggers |
|-------|-------------|----------|
| 🔧 [**Cron Doctor**](#-cron-doctor) | Diagnose cron failures — pattern detection, severity triage, health reports | cron failure, backup failed, job not running |
| 💚 [**Self Monitor**](#-self-monitor) | Infrastructure monitoring — disk, memory, CPU, services, auto-remediation | health check, heartbeat, service status |
| 🔒 [**Skill Security**](#-skill-security-scanner) | Audit skills for credential harvesting, code injection, exfiltration | new skill install, security scan |
| 💰 [**Cost Tracker**](#-cost-tracker) | Track token usage and spend across providers, set session budgets | how much did this cost, token usage |
| 🗺️ [**Explain Codebase**](#-explain-codebase) | Drop into any repo and understand it in minutes | explain this codebase, architecture overview |
| 🛡️ [**Git Guardian**](#-git-guardian) | Pre-commit safety — secrets, large files, debug artifacts, merge markers | check before commit, secrets check |
| 🧩 [**Cron Composer**](#-cron-composer) | Composable block system for managing dozens of cron prompts | cron management, compose cron |
| 🔍 [**Weekly Meta-Audit**](#-weekly-meta-audit) | 11-section operational self-audit — find gaps, fix assumptions, reduce debt | weekly review, meta-audit, retrospective |
| 📚 [**Daily Archivist**](#-daily-archivist) | Knowledge quality audit — fact-check memory, clean up safe issues, route findings | knowledge audit, fact check memory, archivist run |
| [**Static-site Release Verification**](static-site-release-verification/SKILL.md) | Source/build/deployed-revision contract, clean URL checks and asset/CDN parity | static release, stale production, CDN freshness |
| [**Approval-blocked Maintenance Loops**](approval-blocked-maintenance-loops/SKILL.md) | Consent checkpoints, bounded retries, unknown-outcome reconciliation | approval timeout, repeated prompts, blocked loop |
| [**Narrated Motion Explainers**](narrated-motion-explainers/SKILL.md) | Reproducible Pillow → FFmpeg motion, captions, optional narration and real MP4 verification | animated explainer, narrated process video |

---

## 🔧 Cron Doctor

**Diagnose and triage cron job failures in seconds.**

When your scheduled tasks silently fail at 3am, Cron Doctor pattern-matches error logs, prioritises by severity, and generates a health report with root cause analysis.

- 🔍 Scans cron logs, syslog, and journalctl for failure patterns
- 🏥 Triages by criticality: data-loss risks first, cosmetic issues last
- 📊 Generates structured health reports with recommended fixes
- 🔄 Identifies recurring failures vs one-offs
- ⚡ Checks cron daemon status, permissions, environment issues

---

## 💚 Self Monitor

**Proactive infrastructure health monitoring — catch problems before users do.**

Self Monitor checks disk, memory, CPU, services, and recent errors. It auto-fixes safe issues (like clearing temp files when disk is full) and alerts on everything else.

- 💾 Disk usage monitoring with configurable thresholds (80% warn, 90% critical)
- 🧠 Memory and CPU load tracking
- 🔄 Service health checks (systemd, Docker, custom processes)
- 🔧 Auto-fix safe issues (temp cleanup, log rotation)
- 📊 Structured health report output

---

## 🔒 Skill Security Scanner

**Audit AI agent skills before installing them. Trust, but verify.**

Analyses `SKILL.md` files and their scripts for credential harvesting, code injection, network exfiltration, and obfuscation.

- 🔑 Detects credential harvesting (API keys, tokens, passwords)
- 💉 Identifies code injection risks (eval, exec, dynamic imports)
- 🌐 Flags network exfiltration (unauthorized outbound calls)
- 🎭 Catches obfuscation (base64 encoded commands, hidden instructions)

**Scripts included:**
```bash
./skill-security/audit.sh /path/to/skill          # Audit a single skill
./skill-security/audit-all.sh                     # Scan OpenClaw built-ins and ~/skills
./skill-security/preinstall-check.sh /path/to/new  # Quick pre-install check
```

---

## 💰 Cost Tracker

**Know what your AI sessions actually cost — before the invoice surprises you.**

Track token usage and cumulative spend across OpenAI, Anthropic, Google, and other providers. Set session budgets and get warned at 50/80/95% thresholds.

- 💵 Per-turn cost calculation with running totals
- ⚠️ Budget warnings at configurable thresholds
- 🌐 Pricing tables for Claude, GPT-4, Gemini, Mistral, DeepSeek, and more
- 📋 Multi-model session tracking

---

## 🗺️ Explain Codebase

**Drop into any repo and understand it in minutes, not hours.**

Generates a structured architecture overview: tech stack, directory map, entry points, data flow, dependencies, and a "start here" guide.

- 🔍 Recon phase: directory tree, config files, entrypoints, CI/CD
- 🗂️ Annotated directory map with purpose for each folder
- 📦 Dependency breakdown with roles explained
- 🔄 Data flow diagram (request → response)
- 🌱 "Start here" contributor path

---

## 🛡️ Git Guardian

**Pre-commit safety for AI-assisted development.**

AI tools generate code fast — and sometimes include secrets from context, debug artifacts, or files that should never touch version control. 7 safety checks before every commit.

- 🔑 Secret detection: 12+ provider-specific patterns
- 📁 Sensitive file detection: `.env`, `.pem`, `.key`, `id_rsa`
- 📦 Large file detection (warn >1MB, block >10MB)
- ⚔️ Merge conflict marker detection
- 🐛 Debug artifact detection (`console.log`, `debugger`, `pdb.set_trace`)
- 🪝 Installable as a git pre-commit hook

---

## 🧩 Cron Composer

**71 cron jobs, one place to change them all.**

Define reusable markdown blocks and assemble cron prompts from a YAML manifest. Change error handling once — it updates everywhere.

- 🧱 Composable markdown blocks — write once, reuse across all crons
- 📋 YAML manifest maps cron IDs → block lists + task prompts
- 🔄 Variable substitution — `{{PROJECT}}`, `{{SITE}}`, etc.
- 🔍 Dry-run, diff, lint, sync — full lifecycle management

---

## 🔍 Weekly Meta-Audit

**Your agent audits its own operations — so you wake up to improvements, not fires.**

An 11-section structured review that surfaces operational debt: missing automations, wrong assumptions, context losses, wasted effort, and cross-project synergies nobody is pursuing.

- 🔧 **Missing automations** — what broke that should have been automated?
- ❌ **Wrong assumptions** — stale rules in memory that need updating
- 🔮 **Next week forecast** — ranked by likely human priority
- 🔗 **Connections unmade** — cross-project synergies nobody pursues
- ⚡ **Friction → Workflows** — recurring manual work mapped to automations
- 📝 **Auto-generates feedback entries** and appends them to your rules file
- ✅❌ **Honest retrospective** — forward momentum vs wasted effort
- 🏗️ **Compound system proposal** — one high-leverage tool to build next

### The 11 Sections
1. Missing Tools/Automations
2. Wrong Assumptions
3. Next Week Likely Needs
4. Skills to Develop
5. Context Losses
6. Connections Unmade
7. Friction → Workflows
8. New Feedback Entries
9. Last Week Audit (✅/❌)
10. Generic → Specific
11. Compound System Proposal

**Recommended as a weekly cron:**
```bash
openclaw cron add --name "weekly-meta-audit" --cron "0 20 * * 0" \
  --message "Perform the weekly meta-audit skill." \
  --model claude-sonnet-4-5 --timeout-seconds 300 --session isolated
```

---

## 📚 Daily Archivist

**Audit knowledge quality daily — verify facts, fix safe cleanup, and route the rest.**

Daily Archivist checks memory and knowledge files against the actual workspace, identifies stale or broken references, and leaves structured notes for the right agent when an issue needs specialist follow-up.

- ✅ Runs mechanical fact checks with [verify-facts.sh](daily-archivist/scripts/verify-facts.sh)
- 🔎 Scans recently changed memory files and inbox status
- 🧹 Auto-fixes safe quality issues like formatting and duplicate content
- 📬 Routes non-trivial findings to `memory/inbox/<agent>.md`
- 💸 Keeps scheduled audits cost-conscious by limiting scan scope

---

## Portable Examples and Requirements

The three new workflows are runtime-neutral; their support scripts use ordinary local tools:

| Package | Requirements | Tested example / boundary |
|---------|--------------|---------------------------|
| Static-site Release Verification | Python 3.11+; explicitly scoped HTTP(S) access | Loopback fixture proves clean URL/content/canonical checks, stale asset rejection, revision mismatch, redirects and byte/request limits; never deploys or purges |
| Approval-blocked Maintenance Loops | Python 3.11+ for the optional example; actual consent comes from your runtime | Synthetic state table holds denied/expired wakeups, bounds attempts and reconciles unknown outcomes; never executes actions or grants approval |
| Narrated Motion Explainers | Python 3.11+, pinned Pillow dependency, FFmpeg/ffprobe with libx264 and AAC | Real six-second MP4, captions and generated tone; full decode, codec/duration assertions and per-chapter motion checks. Tone is **not voiceover**; spoken narration is optional local input |

The older host-monitoring/scheduler packages are not universally portable: Linux service and shell commands need their documented host utilities; OpenClaw scheduling examples need OpenClaw. Format compatibility alone does not supply tools or consent. Use each package's `compatibility` field and inspect commands before use.

Run the non-mutating decision example:

```bash
python3 approval-blocked-maintenance-loops/scripts/decide.py \
  approval-blocked-maintenance-loops/assets/checkpoint.json
# hold: expired approval
```

Render and verify the real motion sample (output directory must not already exist):

```bash
python3 -m venv .motion-venv
.motion-venv/bin/python -m pip install -r narrated-motion-explainers/requirements.txt
# Install FFmpeg and ffprobe separately on your host.
.motion-venv/bin/python narrated-motion-explainers/scripts/render.py --output-dir motion-output
.motion-venv/bin/python narrated-motion-explainers/scripts/verify_video.py motion-output
```

The output includes `sample.mp4`, audio, `captions.srt`, `chapters.json`, render metadata, decoded inspection frames and verification evidence. No generated video, font binaries or virtualenv is shipped. On Windows, use `.motion-venv\Scripts\python.exe`. See each skill for scoped release-manifest usage, optional narration, and limitations.

---

## Installation

Install the **complete directory**, keeping `SKILL.md` at the package root and preserving all scripts, blocks, and supporting files. Do not rename it to a standalone `<skill>.md` file: that loses package discovery and resources.

From a clone of this repository, choose the skills directory documented by your agent:

```bash
# Replace this example destination with your agent's documented skills directory.
SKILLS_DIR="/path/to/agent/skills"
mkdir -p "$SKILLS_DIR"
cp -R cron-doctor "$SKILLS_DIR/cron-doctor"
# Repeat for another package; copy the entire package, not only SKILL.md.
```

These packages use the [Agent Skills format](https://agentskills.io/specification). Format support does not imply runtime portability: Linux commands need a suitable host, and OpenClaw scheduler commands are not Hermes commands. Check each package's `compatibility` field and use your runtime's documented scheduling interfaces.

## Format and Validation

All 12 package entry points are validated; the original nine identifiers and supporting files are retained. Custom `author`, `version`, and `tags` values live under `metadata` as strings. Additional files such as `README.md` and `blocks/` are permitted by the specification; emojis and gerund names are not required.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
# Optional locally; CI installs these and FFmpeg so video tests cannot skip.
.venv/bin/python -m pip install -r narrated-motion-explainers/requirements.txt
.venv/bin/python scripts/validate_skills.py
.venv/bin/python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for validation scope, the optional reference-validator check, and runtime-test limitations.
---

## Premium Skills

Want more? Premium skill packs at **[skillpacks.dev](https://skillpacks.dev)**:

| Pack | What's Inside | Price |
|------|---------------|-------|
| 🛡️ **Security Suite** | PII scanning, secrets detection, prompt injection defense | [$9.90](https://polycatai.gumroad.com/l/bsrugo) |
| 🧠 **Structured Memory** | Three-tier memory system replacing flat MEMORY.md | [$9.90](https://polycatai.gumroad.com/l/goawrg) |
| 📋 **Planning & Execution** | Systematic task planning with batch execution | [$9.90](https://polycatai.gumroad.com/l/uydfto) |
| 💎 **Bundle** | All 3 packs | [$24.90](https://polycatai.gumroad.com/l/atsrl) |

---

## Why These Skills Exist

We run 8 AI agents 24/7 on a single server. These skills emerged from real operational pain:

- **Cron Doctor** — born after a backup cron silently failed for 3 days
- **Self Monitor** — born after disk hit 95% and crashed a database
- **Skill Security** — born after auditing a skill that tried to exfiltrate API keys
- **Weekly Meta-Audit** — born after a week where 4 things broke silently and we only found them by accident

They're not theoretical — they run in production every day.

---

## Contributing

Found a bug? Have an improvement? PRs welcome.

## License

MIT — use these however you want.

---

**Built by Polycat 🐱** · ☕ [Support on Ko-fi](https://ko-fi.com/srvzt)
