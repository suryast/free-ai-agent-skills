---
name: weekly-meta-audit
description: Automated weekly self-audit of agent operations, cron health, memory gaps, and process failures. Use when performing periodic reviews, operational health checks, identifying automation gaps, surfacing wrong assumptions, or generating improvement recommendations. Triggers on: weekly review, meta-audit, operations audit, what broke this week, process review, improvement cycle, retrospective, week in review.
---

STARTER_CHARACTER = 🔍

# Weekly Meta-Audit

A structured weekly self-audit that examines your agent's operational health, identifies gaps, and generates concrete improvement actions. Inspired by [Outcome Engineering](https://o16g.com) principles — measure outcomes, not outputs.

## Purpose

Most AI agent setups accumulate invisible debt: silent cron failures, wrong assumptions in memory, manual work that should be automated, cross-project synergies nobody pursues. This skill surfaces all of it systematically.

## When to Run

- **Scheduled**: Sunday evening / Monday morning (end-of-week retrospective)
- **On demand**: After a week with notable failures or when things feel "off"
- **Recommended cadence**: Weekly (diminishing returns if more frequent)

## Prerequisites

The audit reads from your existing workspace structure. It works best with:

- **Memory files**: Daily logs (`memory/YYYY-MM-DD.md`) from the past 7 days
- **Feedback file**: Shared operational rules (`memory/feedback/feedback.md` or similar)
- **Long-term memory**: `MEMORY.md` with project state and decisions
- **Cron system**: OpenClaw crons (or any cron manager with `list` and `runs` commands)

If any of these don't exist, the audit adapts — it just has less data to work with.

## Audit Process

### Phase 1: Gather Context

Read these files (skip any that don't exist):

1. **Operating principles** — `AGENTS.md` or equivalent
2. **Current state** — `MEMORY.md`
3. **Shared rules** — `memory/feedback/feedback.md`
4. **Last 7 daily logs** — `ls memory/2*.md | tail -7`, read each
5. **Cron list** — Run `openclaw cron list` (or equivalent)
6. **Recent cron runs** — Run `openclaw cron runs --limit 50`

### Phase 2: Analyze (All 11 Sections Mandatory)

Work through each section. Be **specific, not generic** — name cron IDs, script paths, project names, dates, and incidents. Every finding must have a **concrete next action**.

---

#### 1. MISSING TOOLS/AUTOMATIONS
What broke or required manual intervention this week that should be automated?

**Format per finding:**
- **Incident**: What happened (date, project, impact)
- **Root cause**: Why it wasn't caught automatically
- **Proposed fix**: Script/cron/workflow to prevent recurrence
- **Build cost**: Estimate (trivial / 30min / 2h / half-day)

---

#### 2. WRONG ASSUMPTIONS
What assumptions in feedback.md, MEMORY.md, cron prompts, or operational rules turned out wrong?

**Check for:**
- Feedback entries that no longer apply
- Memory entries that are stale or incorrect
- Cron prompts with outdated paths, models, or logic
- Standing rules that were violated without consequence

---

#### 3. NEXT WEEK LIKELY NEEDS
Based on active projects, blockers, and the human's recent attention — what will matter next week?

**Rank by likely priority** (what the human will ask about, not what you think is important).

---

#### 4. SKILLS TO DEVELOP
What capability gaps appeared this week? Name the specific task that exposed each gap.

---

#### 5. CONTEXT LOSSES
What information was lost between sessions or between agents? What should have been written down but wasn't?

**Common patterns:**
- Sub-agent decisions not logged (WHY choices were made)
- Verbal corrections not appended to feedback
- Cron failures missing task context
- Architecture decisions only in chat, not in docs

---

#### 6. CONNECTIONS UNMADE
Cross-project synergies, shared components, or bundling opportunities nobody is pursuing.

**Think about:**
- Shared audiences across projects
- Reusable code/infrastructure
- Cross-promotion opportunities
- Data that could enrich another project

---

#### 7. FRICTION → WORKFLOWS
Recurring friction points that should become automated workflows.

**Format per finding:**
- **Friction**: What keeps happening manually
- **Frequency**: How often (daily / weekly / per-deploy)
- **Proposed workflow**: Tool chain to automate it
- **Compound value**: Why this gets better over time

---

#### 8. NEW FEEDBACK ENTRIES
Write new entries for the feedback file based on this week's lessons.

**Format:**
```
### Entry N — YYYY-MM-DD
- **Pattern:** [What went wrong or what was learned]
- **Rule:** [Concrete rule to prevent recurrence]
- **Source:** [Incident or observation that triggered this]
```

**Actually append them** to the feedback file — don't just list them.

---

#### 9. LAST WEEK AUDIT
Two lists:

**✅ Forward momentum** — What shipped, what progressed, what unblocked
**❌ Wasted effort** — What was abandoned, repeated, took too long, or produced nothing

Be honest. "We spent 2 hours debugging X when Y would have been faster" is useful. "Everything went great" is not.

---

#### 10. GENERIC → SPECIFIC
Which cron outputs, reports, or agent responses are too generic? How should they be made more specific and actionable?

**Test each report against:** "Could someone act on this without asking follow-up questions?"

---

#### 11. COMPOUND SYSTEM
Propose **ONE** compound system (tool/script/cron combo) that would have the highest leverage over the next month.

**Template:**
- **What it does**: [Concrete description]
- **What it replaces**: [Current manual process]
- **Build cost**: [Hours estimate]
- **Compound value**: [Why it gets more valuable over time]
- **First user**: [Which project/workflow benefits first]

---

## Output Format

Send the full audit as a **single message** with all 11 sections. Use headers, tables, and bullet points for scanability.

**Tone:** Brutally honest. This is an internal operations review, not a status report for a stakeholder. Name problems clearly. Don't soften findings.

## Cron Setup Example

```bash
openclaw cron add \
  --name "weekly-meta-audit" \
  --cron "0 20 * * 0" \
  --message "Perform the weekly meta-audit. Read the weekly-meta-audit skill instructions and follow them completely." \
  --model claude-sonnet-4-5 \
  --channel telegram \
  --to YOUR_CHAT_ID \
  --announce \
  --timeout-seconds 300 \
  --session isolated
```

Adjust the model based on your budget:
- **Opus**: Most thorough, catches subtle patterns
- **Sonnet**: Good balance of depth and cost (recommended)
- **Haiku**: Too shallow for meaningful audit — not recommended

## Anti-Patterns

- ❌ "Everything looks good this week" — If nothing needs fixing, the audit isn't looking hard enough
- ❌ Vague recommendations ("improve monitoring") — Every finding needs a concrete next action
- ❌ Listing only successes — The ❌ section matters more than the ✅ section
- ❌ Repeating last week's findings without checking if they were fixed
- ❌ Proposing new systems without estimating build cost
