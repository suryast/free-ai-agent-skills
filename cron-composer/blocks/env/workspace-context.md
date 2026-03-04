## Workspace Context

- Working directory: {{WORKSPACE}}
- All file paths are absolute unless explicitly noted.
- Do not assume relative paths exist unless you have confirmed the current directory.
- Before reading or writing any file, verify it exists with `ls` or `test -f`.
- Prefer `exec` (shell commands) for file I/O over write/edit tools when in cron context.
