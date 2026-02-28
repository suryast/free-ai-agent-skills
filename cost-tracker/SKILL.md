---
name: cost-tracker
version: 1.0.0
author: Polycat
tags: [cost, tokens, budget, llm, monitoring, api]
license: MIT
platform: universal
description: Track LLM API spend per session and task. Estimate token usage across providers. Warn before you blow your budget.
---

# 💰 Cost Tracker

> **Compatible with Claude Code, Codex CLI, Cursor, Windsurf, and any SKILL.md-compatible agent.**

Track what your AI sessions actually cost. Estimate token usage, cumulative spend, and warn you before you hit budget thresholds — across OpenAI, Anthropic, Google, and other major providers.

---

## Triggers

Activate this skill when:
- User asks "how much has this session cost?"
- User asks "what's my token usage?"
- User sets a session budget ("keep this under $2")
- User wants a cost estimate before a large task
- Cumulative session spend needs tracking
- "track my costs", "budget check", "token count", "how much am I spending"

---

## Pricing Reference (update as models change)

Use these rates to estimate costs. All prices are per 1M tokens (input / output).

### Anthropic
| Model | Input | Output |
|-------|-------|--------|
| claude-opus-4 | $15.00 | $75.00 |
| claude-sonnet-4 | $3.00 | $15.00 |
| claude-haiku-4 | $0.80 | $4.00 |
| claude-opus-3 | $15.00 | $75.00 |
| claude-sonnet-3.5 | $3.00 | $15.00 |
| claude-haiku-3.5 | $0.80 | $4.00 |

### OpenAI
| Model | Input | Output |
|-------|-------|--------|
| gpt-4o | $2.50 | $10.00 |
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4-turbo | $10.00 | $30.00 |
| gpt-4 | $30.00 | $60.00 |
| gpt-3.5-turbo | $0.50 | $1.50 |
| o1 | $15.00 | $60.00 |
| o1-mini | $3.00 | $12.00 |
| o3-mini | $1.10 | $4.40 |

### Google
| Model | Input | Output |
|-------|-------|--------|
| gemini-2.0-flash | $0.075 | $0.30 |
| gemini-2.0-pro | $1.25 | $5.00 |
| gemini-1.5-pro | $1.25 | $5.00 |
| gemini-1.5-flash | $0.075 | $0.30 |

### Other
| Model | Input | Output |
|-------|-------|--------|
| mistral-large | $3.00 | $9.00 |
| mistral-small | $0.20 | $0.60 |
| llama-3.3-70b (Groq) | $0.59 | $0.79 |
| deepseek-r1 | $0.55 | $2.19 |

> ⚠️ Prices change frequently. Always verify at the provider's pricing page before making financial decisions.

---

## How It Works

### Session Tracking

When activated, maintain a running cost ledger in the conversation context:

```
SESSION COST LEDGER
===================
Model: claude-sonnet-4
Started: [timestamp]

Turn  | Input tok | Output tok | Cost
------|-----------|------------|------
  1   |    2,340  |       450  | $0.0134
  2   |    4,120  |       890  | $0.0259
  3   |    1,870  |       340  | $0.0107
------|-----------|------------|------
Total |    8,330  |     1,680  | $0.0500

Budget: $2.00 | Used: $0.05 (2.5%) | Remaining: $1.95
```

### Token Estimation

When you can't read token counts directly from the API response, estimate:

**Quick estimates (rough, for planning):**
- 1 token ≈ 4 characters of English text
- 1 token ≈ ¾ of a word
- Code is denser: 1 token ≈ 3 characters
- 1 page of plain text ≈ 500–750 tokens
- 1,000-word article ≈ 1,300–1,500 tokens

**File size estimates:**
- Small file (<50 lines): ~500–1,000 tokens
- Medium file (50–200 lines): ~1,000–4,000 tokens
- Large file (200–500 lines): ~4,000–10,000 tokens
- Full codebase context: count with `wc -c` then divide by 4

**Pre-task estimate command:**
```bash
# Estimate tokens in a file
wc -c myfile.py | awk '{printf "~%d tokens\n", $1/4}'

# Estimate tokens in entire codebase
find . -name "*.py" -o -name "*.ts" -o -name "*.js" | xargs wc -c 2>/dev/null | tail -1 | awk '{printf "~%d tokens (input)\n", $1/4}'

# Count words as rough proxy
wc -w myfile.txt | awk '{printf "~%d tokens\n", $1*1.3}'
```

### Budget Warnings

Issue warnings at these thresholds:
- **50%** of budget: ℹ️ Heads up — halfway through budget
- **80%** of budget: ⚠️ Approaching limit — consider wrapping up
- **95%** of budget: 🚨 Budget nearly exhausted — stop or expand

### Cost Estimation Before Large Tasks

Before any task involving large files or long conversations, estimate upfront:

```
📊 PRE-TASK ESTIMATE
====================
Task: Refactor entire codebase
Files to read: 23 files (~180,000 chars)
Estimated input: ~45,000 tokens
Expected output: ~8,000 tokens (code changes + explanation)
Model: claude-sonnet-4

Estimated cost: $0.255
  Input:  45,000 × $3.00/M  = $0.135
  Output:  8,000 × $15.00/M = $0.120

Proceed? This is ~13% of your $2.00 budget.
```

---

## Output Format

### Quick status (inline, on request)
```
💰 This session: ~$0.05 (8,330 tokens in / 1,680 out) | Budget: $1.95 remaining
```

### Full report (on request or at session end)
```
╔══════════════════════════════════════╗
║        SESSION COST REPORT           ║
╠══════════════════════════════════════╣
║ Model:    claude-sonnet-4            ║
║ Duration: 23 minutes                 ║
╠══════════════════════════════════════╣
║ INPUT TOKENS                         ║
║   Turns:          12                 ║
║   Total tokens:   42,840             ║
║   Cost:           $0.1285            ║
╠══════════════════════════════════════╣
║ OUTPUT TOKENS                        ║
║   Total tokens:   8,920              ║
║   Cost:           $0.1338            ║
╠══════════════════════════════════════╣
║ TOTAL COST:       $0.2623            ║
║ Budget used:      13.1% of $2.00     ║
║ Remaining:        $1.74              ║
╚══════════════════════════════════════╝
```

---

## Multi-Provider Session

If a session spans multiple models or providers:

```
MULTI-MODEL SESSION SUMMARY
============================
gpt-4o         → 12,000 in / 2,400 out → $0.054
claude-haiku-4 → 45,000 in / 8,000 out → $0.068
gemini-flash   →  8,000 in / 1,200 out → $0.001
────────────────────────────────────────────────
TOTAL          → 65,000 in / 11,600 out → $0.123
```

---

## Common Scenarios

### "How much did that last task cost?"
Calculate the tokens in the most recent exchange, apply the current model's rates, and report inline.

### "Estimate the cost of indexing my repo"
```bash
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.md" \) \
  | xargs wc -c 2>/dev/null | tail -1 \
  | awk '{
      tokens = $1/4
      cost_sonnet = (tokens/1000000) * 3.00
      cost_haiku  = (tokens/1000000) * 0.80
      cost_gpt4o  = (tokens/1000000) * 2.50
      printf "Repo size: ~%.0f tokens\n", tokens
      printf "claude-sonnet-4: $%.4f\n", cost_sonnet
      printf "claude-haiku-4:  $%.4f\n", cost_haiku
      printf "gpt-4o:          $%.4f\n", cost_gpt4o
    }'
```

### "Set a $5 budget for this session"
Acknowledge the budget, start tracking, and proactively warn at 50%, 80%, and 95% thresholds. If the budget would be exceeded by a planned task, warn before proceeding.

---

## Notes

- Token counts are **estimates** unless the model API returns exact counts in its response metadata
- Output tokens are typically 3–10× more expensive per token than input — optimize accordingly
- Caching (where available) can reduce input costs by 80–90% for repeated context
- Streaming responses don't change token costs — you pay for tokens regardless
- System prompts count as input tokens on every turn
