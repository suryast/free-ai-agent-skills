## Git Commit & Push

After making changes to the repository at `{{REPO}}`:

1. Stage all changes: `git -C {{REPO}} add -A`
2. Commit with a descriptive message:
   ```
   git -C {{REPO}} -c user.name="{{GIT_NAME}}" -c user.email="{{GIT_EMAIL}}" commit -m "<descriptive message>"
   ```
3. Pull with rebase to avoid conflicts: `git -C {{REPO}} pull --rebase origin {{BRANCH}}`
4. Push: `git -C {{REPO}} push origin {{BRANCH}}`

If push fails due to conflicts, report the error and stop — do not force-push.
