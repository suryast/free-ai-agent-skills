---
name: approval-blocked-maintenance-loops
description: Stops repetitive maintenance retries at consent boundaries and preserves resumable evidence. Use when scheduled agents stall on denied or timed-out approvals, repeatedly prompt, or cannot determine whether an action executed.
license: MIT
compatibility: Runtime-neutral consent workflow; use the host's actual approval interface. Optional synthetic decision example requires Python 3.11+ and performs no maintenance actions or permission changes.
---

# Approval-blocked maintenance loops

## Classify before retrying

| State | Meaning | Next decision |
|---|---|---|
| `awaiting_approval` | The actual approval prompt is still open | Wait; do not create another prompt |
| `denied` | Operator declined the named operation | Retain checkpoint; request changed scope once, not each wakeup |
| `expired` | Prompt timed out or closed without consent | Record no approval; automatic wakeups cannot renew it |
| `unknown` | Request was sent but outcome is ambiguous | Hold writes; reconcile through independently authorized read-back |
| `transient_failure` | Evidence proves no side effect occurred; a temporary failure is classified | Retry only within existing consent and bounded retry budget |
| `ready` | Explicit scope approval and prerequisites are current | Make one approved attempt, then verify |
| `completed` | Exact intended result was independently read back | Clear only the matching blocker |

A transport timeout after dispatch is `unknown`, not automatically transient. A retry may duplicate an action. A user message asking to continue may authorize one scoped approval attempt, but cannot replace a tool's approval interface. Track separate approval domains independently.

## Persist one bounded checkpoint

Record operation ID, exact target/action, scope exclusions, state, last known execution evidence, completed deliverables, verification method, retry count/budget, operator decision requested, and the event needed to resume. Use non-secret artifact references rather than full logs, credentials, private payloads, or unlimited histories. Set retention/size limits and atomically replace the checkpoint using the runtime's supported storage. See [synthetic checkpoint](assets/checkpoint.json).

At each scheduled wakeup:

1. Read the saved checkpoint; do not redispatch or reopen prompts merely because the clock fired.
2. Consider only new consent, changed prerequisites, or an explicitly required independently authorized read. A status check is not implementation progress. Never obtain a denied outcome through another tool, command, endpoint, or delegate.
3. Advance unrelated, independently authorized work only within its own scope; propagate denials to delegates. Do not bundle independent diagnostics with gated mutations.
4. Once independent work is exhausted, request the operator decision once: retry the exact named operation through normal approval, revise scope, or authorize a supported pause. Remain blocked if no answer arrives; never mark an unfinished task complete to stop a loop.
5. On approved resume, refresh source and uncommitted deliverables, verify target/scope, perform only the approved step, then read back the exact result. Clear stale blocker labels immediately after verified success. If approval expires again, return to the checkpoint rather than retrying on the next wakeup.

Use one concise changed-status notice; unchanged wakeups should be silent when the delivery contract permits. If a reply is mandatory, say the state is unchanged without inventing fresh verification.

## Synthetic decision example

[decide.py](scripts/decide.py) reads a checkpoint and prints `hold`, `attempt`, `reconcile`, `verify`, or `done`. It never saves state, executes operations, approves requests, or proves real authorization. Flags model facts an actual runtime must obtain from its trusted interface; a JSON field or CLI flag is not a permission grant.

```bash
python3 approval-blocked-maintenance-loops/scripts/decide.py \
  approval-blocked-maintenance-loops/assets/checkpoint.json
# hold: expired approval
```

Bound the real implementation's retries and notifications; preserve unknown outcomes until reconciliation. Tests exercise every state and denied/expired wakeups without dangerous actions.
