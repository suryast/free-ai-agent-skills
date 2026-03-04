## Check-and-Fix Pattern

Use this pattern for cron jobs that inspect a resource, find issues, and repair them.

1. **Check** — Read the current state. Capture the full output.
2. **Evaluate** — Determine if action is needed. If nothing is wrong, report "✅ OK" and stop.
3. **Fix** — Apply the minimal change needed. Do not make unrelated changes.
4. **Verify** — Re-run the check to confirm the fix worked.
5. **Report** — Summarise: what was wrong, what was changed, what the new state is.

**Constraints:**
- One issue per run. Fix the most critical issue; leave the rest for next run.
- If the fix fails, report the failure clearly and do not retry — let the human decide.
- Log what you did to `{{LOG_FILE}}` with a timestamp.
