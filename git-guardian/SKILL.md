---
name: git-guardian
version: 1.0.0
author: Polycat
tags: [git, security, secrets, pre-commit, safety, devops]
license: MIT
platform: universal
description: Pre-commit safety checks for AI-assisted development. Detects secrets, large files, merge conflict markers, sensitive files, and common AI-coding mistakes before they hit your repo.
---

# 🛡️ Git Guardian

> **Compatible with Claude Code, Codex CLI, Cursor, Windsurf, and any SKILL.md-compatible agent.**

Pre-commit safety checks built for AI-assisted development. AI agents generate code fast — sometimes too fast. Git Guardian catches secrets, sensitive files, merge conflicts, and common AI mistakes before they land in your history.

---

## Triggers

Activate this skill when:
- "check before commit", "is this safe to commit", "pre-commit check"
- "any secrets in staged files?", "check for API keys"
- About to commit AI-generated code
- "run git guardian", "safety check", "audit staged changes"
- After a large AI-generated code dump, before pushing
- User sets up a new repo and wants pre-commit safety

---

## The Full Check Suite

Run these checks against staged changes (or a specified path). Report findings with severity: 🔴 BLOCK, 🟡 WARN, 🔵 INFO.

---

### Check 1: Secret Detection 🔴

**Patterns that indicate leaked credentials:**

```bash
# Check staged files for secrets
git diff --cached --name-only | while read f; do
  echo "=== $f ==="
  git show ":$f" 2>/dev/null
done | grep -inE \
  'api[_-]?key|apikey|api[_-]?secret|\
secret[_-]?key|secret[_-]?token|\
auth[_-]?token|access[_-]?token|bearer[_-]?\
private[_-]?key|ssh[_-]?key|rsa[_-]?private|\
password\s*=\s*["\x27][^\x27"]{6,}|\
passwd\s*=\s*["\x27][^\x27"]{6,}|\
aws_access_key_id|aws_secret_access_key|\
AKIA[0-9A-Z]{16}|\
ghp_[a-zA-Z0-9]{36}|github_pat_|\
sk-[a-zA-Z0-9]{32,}|\
xoxb-|xoxa-|xoxp-|\
glpat-|glcpat-|\
npm_[a-zA-Z0-9]{36}|\
-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY'
```

**High-risk literal patterns to check for:**
```bash
# Check for raw high-entropy strings (possible tokens/keys)
git diff --cached | grep "^+" | grep -vE "^(\\+\\+\\+)" | \
  grep -E '[a-zA-Z0-9+/]{40,}={0,2}' | \
  grep -vE '(hash|sha|digest|checksum|fingerprint|base64|encoded|example|placeholder|YOUR_|REPLACE_|<.*>)' | \
  head -20
```

**Common secret formats by provider:**
| Provider | Pattern | Example prefix |
|----------|---------|----------------|
| OpenAI | `sk-[a-zA-Z0-9]{48}` | `sk-proj-...` |
| Anthropic | `sk-ant-[a-zA-Z0-9-]{95}` | `sk-ant-api03-...` |
| GitHub | `ghp_[a-zA-Z0-9]{36}` | `ghp_abc...` |
| AWS | `AKIA[A-Z0-9]{16}` | `AKIAIOSFODNN7...` |
| Google API | `AIza[0-9A-Za-z-_]{35}` | `AIzaSy...` |
| Slack | `xoxb-[0-9-]{50,}` | `xoxb-123-...` |
| Stripe | `sk_live_[a-zA-Z0-9]{24}` | `sk_live_...` |
| Twilio | `SK[a-zA-Z0-9]{32}` | `SK1234...` |
| JWT | `eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.` | `eyJhbGc...` |

**Severity:** 🔴 BLOCK — never commit real credentials. If found:
1. Remove the secret from staged files
2. Rotate the credential immediately — assume it's compromised
3. Use environment variables, a secrets manager, or `.env` (gitignored)

---

### Check 2: Sensitive File Detection 🔴

```bash
# Check if sensitive file types are staged
git diff --cached --name-only | grep -iE \
  '\.(env|pem|key|p12|pfx|jks|keystore|ppk|ovpn)$|
  ^\.env(\.|$)|
  \.env\.(local|production|staging|dev|test)$|
  id_rsa|id_dsa|id_ecdsa|id_ed25519|
  \.ssh/|
  credentials$|credentials\.json|
  secrets\.json|secrets\.yaml|secrets\.yml|
  \.netrc$|
  wp-config\.php|
  database\.yml$|
  settings\/local\.py|
  config\/secrets\.'
```

**Never commit these:**
- `.env` files with real values
- Private key files (`.pem`, `.key`, `.p12`, `.ppk`)
- SSH private keys (`id_rsa`, `id_ed25519`, etc.)
- VPN configs (`.ovpn`)
- `credentials.json` (Google service accounts)
- `secrets.yaml` / `secrets.yml`

**Severity:** 🔴 BLOCK — add to `.gitignore` immediately.

---

### Check 3: Large Files 🟡

```bash
# Find staged files over 1MB
git diff --cached --name-only | while read f; do
  size=$(git cat-file -s ":$f" 2>/dev/null || echo 0)
  if [ "$size" -gt 1048576 ]; then
    echo "LARGE: $f ($(( size / 1024 ))KB)"
  fi
done
```

**Thresholds:**
- > 1MB: 🟡 WARN — is this intentional? Should it be in `.gitignore` or git-lfs?
- > 10MB: 🔴 BLOCK — almost certainly wrong. Binary, dataset, or dependency artifact.
- > 50MB: 🔴 BLOCK — will fail on GitHub/GitLab push limits.

**Common large file mistakes:**
- `node_modules/` committed by accident
- Binary build artifacts (`dist/`, `build/`, `*.pyc`, `*.class`)
- Datasets or fixtures that should be downloaded at runtime
- Media files (images, video) that should use git-lfs or external storage

---

### Check 4: Merge Conflict Markers 🔴

```bash
# Detect unresolved merge conflicts in staged files
git diff --cached --name-only | while read f; do
  if git show ":$f" 2>/dev/null | grep -qE '^(<{7}|>{7}|={7}|[|]{7}) '; then
    echo "CONFLICT MARKERS: $f"
    git show ":$f" | grep -nE '^(<{7}|>{7}|={7}|[|]{7}) ' | head -5
  fi
done
```

Markers to detect:
- `<<<<<<< HEAD`
- `=======`
- `>>>>>>> branch-name`
- `||||||| merged common ancestors` (diff3 style)

**Severity:** 🔴 BLOCK — code with conflict markers will not compile or run.

---

### Check 5: TODO/FIXME/HACK in New Code 🔵

```bash
# Find new lines with quality flags in staged diff
git diff --cached | grep "^+" | grep -vE "^\+\+\+" | \
  grep -iE '\b(TODO|FIXME|HACK|XXX|BUG|TEMP|KLUDGE|NOCOMMIT)\b' | \
  head -20
```

**Severity:** 🔵 INFO — not a blocker, but worth knowing what's going in.

Special case — 🔴 BLOCK on `NOCOMMIT`:
```bash
git diff --cached | grep "^+" | grep -iE '\bNOCOMMIT\b'
```
If found, stop — this was intentionally marked to not be committed.

---

### Check 6: `.gitignore` Coverage Audit 🟡

```bash
# Check if common sensitive paths are covered by .gitignore
cat .gitignore 2>/dev/null | sort > /tmp/gi_current.txt

echo "Checking .gitignore coverage..."

patterns=(
  "*.env"
  ".env"
  ".env.*"
  "*.pem"
  "*.key"
  "*.p12"
  "id_rsa"
  "id_ed25519"
  "*.log"
  "node_modules/"
  "__pycache__/"
  "*.pyc"
  "dist/"
  "build/"
  ".DS_Store"
  "Thumbs.db"
  "*.sqlite"
  "*.sqlite3"
  "venv/"
  ".venv/"
  "*.orig"
  "secrets.*"
  "credentials.json"
)

for p in "${patterns[@]}"; do
  if ! grep -qF "$p" .gitignore 2>/dev/null; then
    echo "MISSING: $p"
  fi
done
```

**Severity:** 🟡 WARN for missing patterns — add them before the next commit touches those file types.

**Recommended `.gitignore` additions for AI-assisted projects:**
```gitignore
# Secrets & credentials
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx
*.ppk
id_rsa
id_ed25519
id_ecdsa
credentials.json
secrets.yaml
secrets.yml
.netrc

# AI agent artifacts (if applicable)
.agent_memory/
agent_logs/
session_*.json

# Common build artifacts
node_modules/
dist/
build/
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/

# OS
.DS_Store
Thumbs.db
*.orig
```

---

### Check 7: Accidental Debug Code 🔵

```bash
# Detect common debug artifacts in staged diff
git diff --cached | grep "^+" | grep -vE "^\+\+\+" | \
  grep -iE \
  'console\.log\(|print\(f?["\x27](debug|test|tmp|REMOVE|DELETE ME)|\
debugger;|\
pdb\.set_trace|breakpoint\(\)|\
binding\.pry|\
var_dump\(|die\(|exit\(1\)' | \
  head -20
```

**Severity:** 🔵 INFO — common in AI-generated code. Review before merging to main.

---

## Full Run Command

Run the complete suite against currently staged changes:

```bash
echo "🛡️  Git Guardian — Pre-Commit Safety Check"
echo "==========================================="
echo ""

# 1. What's staged?
echo "📋 Staged files:"
git diff --cached --name-only
echo ""

# 2. Run checks (see above for full implementations)
echo "🔴 Check 1: Secrets..."
echo "🔴 Check 2: Sensitive files..."
echo "🟡 Check 3: Large files..."
echo "🔴 Check 4: Merge conflict markers..."
echo "🔵 Check 5: TODO/FIXME/NOCOMMIT..."
echo "🟡 Check 6: .gitignore coverage..."
echo "🔵 Check 7: Debug artifacts..."
```

---

## Output Format

```
🛡️  Git Guardian — Pre-Commit Safety Check
===========================================
Staged files: 4 | Checks: 7 | Time: 0.3s

🔴 BLOCKED (2 issues — fix before committing)
─────────────────────────────────────────────
[1] SECRET DETECTED in src/config.py (line 14)
    OPENAI_API_KEY = "sk-proj-abc123..."
    → Remove key, rotate immediately, use env var

[2] MERGE CONFLICT MARKERS in src/api/routes.py
    Line 47: <<<<<<< HEAD
    Line 52: >>>>>>> feature/auth-refactor
    → Resolve conflict before committing

🟡 WARNINGS (1 issue — review recommended)
──────────────────────────────────────────
[3] LARGE FILE: data/fixtures.json (8.2MB)
    → Add to .gitignore or move to git-lfs

🔵 INFO (3 notes)
─────────────────
[4] TODO found in src/auth.py (line 88)
    # TODO: add rate limiting here
[5] console.log found in frontend/app.ts (line 23)
[6] .gitignore missing: *.pem, .env.*

══════════════════════════════════════════
❌ COMMIT BLOCKED — resolve 2 critical issue(s) first
```

```
🛡️  Git Guardian — Pre-Commit Safety Check
===========================================
Staged files: 3 | Checks: 7 | Time: 0.2s

✅ All checks passed — safe to commit
```

---

## Installing as a Git Hook

To run automatically before every commit in a project:

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Git Guardian pre-commit hook
# Runs basic safety checks before allowing commit

# Check for secrets
if git diff --cached | grep -qiE 'api[_-]?key\s*=\s*["\x27][^\x27"]{10,}|AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}'; then
  echo "🔴 Git Guardian: Possible secret detected in staged changes"
  echo "   Run a full check: ask your AI agent to run git-guardian"
  exit 1
fi

# Check for merge conflict markers
if git diff --cached | grep -qE '^(<{7}|>{7}|={7}) '; then
  echo "🔴 Git Guardian: Merge conflict markers detected"
  exit 1
fi

# Check for NOCOMMIT
if git diff --cached | grep -qiE '\bNOCOMMIT\b'; then
  echo "🔴 Git Guardian: NOCOMMIT marker found — this change was flagged to not be committed"
  exit 1
fi

echo "✅ Git Guardian: Basic checks passed"
exit 0
EOF

chmod +x .git/hooks/pre-commit
echo "✅ Git Guardian pre-commit hook installed"
```

---

## Why This Matters for AI-Assisted Development

AI coding tools are fast — sometimes too fast. Common failure modes:

1. **Context leakage** — agent reads a `.env` file for context, then writes the values into generated code
2. **Conflict confusion** — agent sees conflict markers and treats them as code, writes around them instead of resolving
3. **Overeager staging** — `git add .` after AI-generated files includes things that should be ignored
4. **Debug trails** — AI includes `console.log`, `print`, `breakpoint()` for its own reasoning, forgets to remove them
5. **Fixture bloat** — AI generates large test fixtures inline instead of loading from external source

Git Guardian is your last line of defense before those mistakes become permanent history.
