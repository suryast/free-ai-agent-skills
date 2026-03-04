## Error Handling

- If any command fails, stop immediately and report the error. Do not continue to the next step.
- Capture stderr: when running shell commands, check both stdout and stderr.
- If a required file or directory is missing, report the full expected path and exit.
- Do not silently swallow errors or proceed with partial results.
- On completion, report a brief summary: what succeeded, what was skipped, and any warnings.
