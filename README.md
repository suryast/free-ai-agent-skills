# 🐱 Free AI Agent Skills

[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-blue)](https://docs.anthropic.com/en/docs/claude-code)
[![Codex CLI](https://img.shields.io/badge/Codex_CLI-compatible-green)](https://github.com/openai/codex)
[![SKILL.md](https://img.shields.io/badge/SKILL.md-standard-orange)](https://docs.anthropic.com/en/docs/claude-code/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Battle-tested `SKILL.md` files for AI coding agents. Built from running **8 specialist agents 24/7 in production** — these skills solve real problems we hit daily.

Works with **Claude Code, Codex CLI, ChatGPT, Cursor, Windsurf, OpenClaw**, and any agent that supports the open `SKILL.md` standard.

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
./skill-security/audit-all.sh /path/to/skills/     # Audit all installed skills
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

## Installation

### Claude Code
```bash
cp -r cron-doctor ~/.claude/skills/cron-doctor
cp -r self-monitor ~/.claude/skills/self-monitor
cp -r weekly-meta-audit ~/.claude/skills/weekly-meta-audit
# ... same pattern for any skill
```

### Codex CLI / ChatGPT
```bash
cp cron-doctor/SKILL.md .codex/skills/cron-doctor.md
cp weekly-meta-audit/SKILL.md .codex/skills/weekly-meta-audit.md
```

### OpenClaw
```bash
clawhub install cron-doctor
clawhub install weekly-meta-audit
```

### Cursor / Windsurf
```bash
cp weekly-meta-audit/SKILL.md .cursor/skills/weekly-meta-audit.md
```

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
