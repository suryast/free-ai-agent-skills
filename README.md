# 🐱 Free AI Agent Skills

[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-blue)](https://docs.anthropic.com/en/docs/claude-code)
[![Codex CLI](https://img.shields.io/badge/Codex_CLI-compatible-green)](https://github.com/openai/codex)
[![SKILL.md](https://img.shields.io/badge/SKILL.md-standard-orange)](https://docs.anthropic.com/en/docs/claude-code/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Battle-tested `SKILL.md` files for AI coding agents. Built from running **8 specialist agents 24/7 in production** — these skills solve real problems we hit daily.

Works with **Claude Code, Codex CLI, ChatGPT, Cursor, Windsurf, OpenClaw**, and any agent that supports the open `SKILL.md` standard.

---

## 🔧 Cron Doctor

**Diagnose and triage cron job failures in seconds.**

When your scheduled tasks silently fail at 3am, Cron Doctor pattern-matches error logs, prioritises by severity, and generates a health report with root cause analysis. It knows the difference between "cron daemon not running" and "script exited with error" — and triages accordingly.

**Use when:** A cron job stopped working. Backups aren't running. Scheduled tasks are silently failing. You need a quick health check of all your crons.

```
Triggers: cron failure, job health check, scheduled task error, backup failed, job not running
```

### What it does
- 🔍 Scans cron logs, syslog, and journalctl for failure patterns
- 🏥 Triages by criticality: data-loss risks first, cosmetic issues last
- 📊 Generates structured health reports with recommended fixes
- 🔄 Identifies recurring failures vs one-offs
- ⚡ Checks cron daemon status, permissions, environment issues

---

## 💚 Self Monitor

**Proactive infrastructure health monitoring — catch problems before users do.**

Self Monitor checks disk, memory, CPU, services, and recent errors. It auto-fixes safe issues (like clearing temp files when disk is full) and alerts on everything else. Think of it as a lightweight Datadog that lives inside your agent.

**Use when:** Heartbeat checks. "Is everything OK?" health checks. Diagnosing slow performance. Monitoring after deployments. Automated infrastructure sweeps.

```
Triggers: health check, heartbeat, monitor status, service status, infrastructure check
```

### What it does
- 💾 Disk usage monitoring with configurable thresholds
- 🧠 Memory and CPU load tracking
- 🔄 Service health checks (systemd, Docker, custom processes)
- 📋 Cron job status verification
- 🔧 Auto-fix safe issues (temp cleanup, log rotation)
- 📊 Structured health report output

---

## 🔒 Skill Security Scanner

**Audit AI agent skills before installing them. Trust, but verify.**

The AI agent ecosystem is growing fast — and so are supply chain risks. Skill Security Scanner analyses `SKILL.md` files and their associated scripts for credential harvesting, code injection, network exfiltration, and obfuscation before you install them.

**Use when:** Installing a new skill from GitHub or any external source. Auditing your existing skills. Security review of a skill marketplace listing. Before trusting any third-party agent extension.

```
Triggers: new skill installation, skill audit, security scan, before loading external skill
```

### What it does
- 🔑 Detects credential harvesting (API keys, tokens, passwords in scripts)
- 💉 Identifies code injection risks (eval, exec, dynamic imports)
- 🌐 Flags network exfiltration (unauthorized outbound calls, data posting)
- 🎭 Catches obfuscation (base64 encoded commands, hidden instructions)
- 📋 Severity-scored findings with actionable recommendations
- 🛡️ Includes allowlist/blocklist for known-safe and known-bad patterns

### Scripts included
```bash
# Audit a single skill
./skill-security/audit.sh /path/to/skill

# Audit all installed skills at once
./skill-security/audit-all.sh /path/to/skills/

# Quick pre-install check
./skill-security/preinstall-check.sh /path/to/new-skill
```

---

---

## 💰 Cost Tracker

**Know what your AI sessions actually cost — before the invoice surprises you.**

Track token usage and cumulative spend across OpenAI, Anthropic, Google, and other providers. Set session budgets, get warned at 50/80/95% thresholds, and estimate costs before kicking off large tasks. Because "how much did that refactor cost?" is a totally valid question.

**Use when:** Monitoring AI API spend. Setting session budgets. Estimating cost of indexing a large repo. Multi-provider sessions. "How much has this conversation cost me?"

```
Triggers: how much did this cost, token usage, session budget, track costs, cost estimate
```

### What it does
- 💵 Per-turn cost calculation with running totals
- 📊 Full session cost reports (input/output tokens, cost breakdown)
- ⚠️ Budget warnings at 50%, 80%, and 95% thresholds
- 🔢 Token estimation commands for files and codebases
- 🌐 Pricing tables for Claude, GPT-4, Gemini, Mistral, DeepSeek, and more
- 📋 Multi-model session tracking when you switch providers mid-task

---

## 🗺️ Explain Codebase

**Drop into any repo and understand it in minutes, not hours.**

Generates a structured architecture overview: tech stack, directory map with purpose annotations, entry points, data flow diagram, key dependencies, environment variables, and a "start here" guide for new contributors. Works on any language or framework.

**Use when:** Starting work on an unfamiliar codebase. Onboarding a new contributor. Before a big refactor. "What does this project actually do?" Pre-PR context gathering.

```
Triggers: explain this codebase, architecture overview, how is this structured, onboarding guide, where do I start
```

### What it does
- 🔍 Recon phase: directory tree, config files, entrypoints, CI/CD, test structure
- 🗂️ Annotated directory map with purpose for each folder
- ⚡ Entry points table with run commands
- 📦 Dependency breakdown with roles explained
- 🔄 Data flow diagram (request → response)
- 🌱 "Start here" contributor path with files to read in order
- ⚠️ Flags non-obvious gotchas, known tech debt, and security issues spotted during analysis

---

## 🛡️ Git Guardian

**Pre-commit safety for AI-assisted development. Because agents are fast and history is forever.**

AI tools generate code quickly — and sometimes include secrets they read from context, leave behind debug artifacts, or stage files that should never touch version control. Git Guardian runs 7 safety checks before every commit: secrets, sensitive files, large files, merge conflict markers, NOCOMMIT flags, `.gitignore` coverage, and debug artifacts.

**Use when:** About to commit AI-generated code. Setting up a new repo. "Is this safe to commit?" Onboarding a team to AI-assisted workflows. Post-refactor safety sweep.

```
Triggers: check before commit, secrets check, pre-commit safety, git guardian, is this safe to commit, audit staged changes
```

### What it does
- 🔑 Secret detection: 12+ provider-specific patterns (OpenAI, Anthropic, AWS, GitHub, Slack, Stripe, JWT, etc.)
- 📁 Sensitive file detection: `.env`, `.pem`, `.key`, `id_rsa`, `credentials.json`, and more
- 📦 Large file detection with MB thresholds (warn >1MB, block >10MB)
- ⚔️ Merge conflict marker detection (including diff3-style `|||||||`)
- 🚩 TODO/FIXME/HACK/NOCOMMIT annotation scan
- 📋 `.gitignore` coverage audit with recommended additions for AI projects
- 🐛 Debug artifact detection (`console.log`, `debugger`, `pdb.set_trace`, etc.)
- 🪝 Installable as a git pre-commit hook for automatic protection

---

## Installation

### Claude Code
```bash
# Copy into your skills directory
cp -r cron-doctor ~/.claude/skills/cron-doctor
cp -r self-monitor ~/.claude/skills/self-monitor
cp -r skill-security ~/.claude/skills/skill-security
cp -r cost-tracker ~/.claude/skills/cost-tracker
cp -r explain-codebase ~/.claude/skills/explain-codebase
cp -r git-guardian ~/.claude/skills/git-guardian
```

### Codex CLI / ChatGPT
```bash
# Copy SKILL.md files to your agent's context
cp cron-doctor/SKILL.md .codex/skills/cron-doctor.md
cp cost-tracker/SKILL.md .codex/skills/cost-tracker.md
cp explain-codebase/SKILL.md .codex/skills/explain-codebase.md
cp git-guardian/SKILL.md .codex/skills/git-guardian.md
```

### OpenClaw / ClawHub
```bash
clawhub install cron-doctor
clawhub install self-monitor
clawhub install skill-security
clawhub install cost-tracker
clawhub install explain-codebase
clawhub install git-guardian
```

### Cursor / Windsurf
```bash
cp cost-tracker/SKILL.md .cursor/skills/cost-tracker.md
cp explain-codebase/SKILL.md .cursor/skills/explain-codebase.md
cp git-guardian/SKILL.md .cursor/skills/git-guardian.md
```

---

## Why These Skills Exist

We run a team of 8 AI agents (coordinator, coder, researcher, writer, security auditor, trader, teacher, janitor) on a single server, 24/7. These skills emerged from real operational pain:

- **Cron Doctor** was born after a backup cron silently failed for 3 days
- **Self Monitor** was born after disk hit 95% and crashed a database
- **Skill Security** was born after auditing a third-party skill that tried to exfiltrate API keys

They're not theoretical — they run in production every day.

---

## Premium Skills

Want more? We sell premium skill packs at **[skillpacks.dev](https://skillpacks.dev)**:

| Pack | What's Inside | Price |
|------|---------------|-------|
| 🛡️ **Security Suite** | PII scanning, secrets detection, prompt injection defense | [$9.90](https://polycatai.gumroad.com/l/bsrugo) |
| 🧠 **Structured Memory** | Three-tier memory system replacing flat MEMORY.md | [$9.90](https://polycatai.gumroad.com/l/goawrg) |
| 📋 **Planning & Execution** | Systematic task planning with batch execution | [$9.90](https://polycatai.gumroad.com/l/uydfto) |
| 💎 **Bundle** | All 3 packs | [$24.90](https://polycatai.gumroad.com/l/atsrl) |

---

## Contributing

Found a bug? Have an improvement? PRs welcome.

## License

MIT — use these however you want.

---

**Built by Polycat 🐱 — a curious cat who runs agents and worries about security.**
