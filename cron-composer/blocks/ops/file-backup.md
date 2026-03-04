## File Backup

Before modifying any important file, create a timestamped backup:

```bash
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
cp {{TARGET_FILE}} {{TARGET_FILE}}.bak-$TIMESTAMP
```

- Keep backups for at least 7 days before cleaning up.
- If the backup fails (disk full, permission error), stop and report — do not proceed with modification.
- After the task completes, confirm the backup exists: `ls -lh {{TARGET_FILE}}.bak-*`
