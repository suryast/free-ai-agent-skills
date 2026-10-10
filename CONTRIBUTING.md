# Contributing

## Package contract

Follow the [Agent Skills specification](https://agentskills.io/specification): an exact-case `SKILL.md` at the package root, YAML frontmatter with `name` and `description`, then Markdown instructions. Keep existing public names stable and matched to their directory. A description must explain the task and trigger; an optional `compatibility` string must explain real environment requirements, not claim universal script portability.

Use `metadata` for custom fields such as `author`, `version`, and `tags`; both keys and values must be strings. Quote version numbers and descriptions containing `: `. Retain the existing license and attribution. Additional files/directories are allowed: do not delete useful READMEs, scripts, or blocks just to impose a preferred layout. The recommended size of the main instructions is under 500 lines, not a hard validation limit. No mandatory emojis or gerund naming convention is imposed.

Link bundled resources relative to the package. Install/copy the entire directory. Runtime-specific examples must be labelled: OpenClaw commands must not be presented as Hermes commands, and host utilities require the documented OS, installed dependencies, and permissions.

## Deterministic local checks

Use Python 3.11+ for the repository checks (Cron Composer itself requires 3.10+):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s cron-composer/tests -v
git diff --check
```

The validator uses a safe YAML loader and checks required fields, names, length/type constraints, metadata strings, unsupported top-level fields, and exact-case entry points. Repository policy additionally rejects duplicate YAML keys and empty instructions. It dynamically enumerates top-level package directories; an empty inventory fails rather than passing silently.

Resource validation checks relative inline/reference-style Markdown destinations and literal `scripts/`, `references/`, and `assets/` paths in code spans across package Markdown files. It ignores external URLs, anchors, and fenced examples/templates. It resolves destinations, including symlinks, and rejects repository escapes. This focused parser is not a complete Markdown implementation; it does not validate fragment anchors, runtime-generated paths, or every shell example. Prefer explicit Markdown links for real bundled resources. Description trigger quality and runtime safety still require human review.

GitHub Actions runs the same package checks and unit tests for pull requests and pushes to `main`, with read-only repository permissions and pinned action revisions. No credentials or live agent operations are needed.

## Optional upstream reference check

The specification also recommends the [skills-ref reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref). Install it in a separate virtualenv using a reviewed immutable revision rather than an unpinned moving branch:

```bash
python3 -m venv .reference-venv
.reference-venv/bin/python -m pip install 'skills-ref @ git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref'
.reference-venv/bin/python - <<'PY'
from pathlib import Path
from skills_ref import validate
packages = sorted(Path('.').glob('*/SKILL.md'))
assert packages, 'No packages found'
errors = {p.parent.name: validate(p.parent) for p in packages}
for name, findings in errors.items():
    print(name, findings)
assert not any(errors.values()), errors
PY
```

This revision validated all nine packages during the format migration. It accepts some cases the repository deliberately rejects (for example lowercase `skill.md`); it is an additional check, not a substitute for the repository's type/link tests. The upstream dependency is optional and is not fetched by CI.

## Portable support-example coverage

The inventory is now 12 packages. The three new support packages are independent rewrites of generic workflow principles, not exports of runtime configuration or private project histories. Existing MIT license/attribution remains unchanged; no third-party media or font files are bundled.

`tests/test_portable_examples.py` adds 23 tests, including a dynamic README inventory/catalog/link check:

- Release checker: real loopback HTTP fixtures for clean URL/content/canonical and asset parity, revision evidence, stale CSS, HTTP errors/redirects, response limits and rejection of local/path/request-budget escapes before network access.
- Consent example: all checkpoint states, denied/expired scheduled wakeups, explicit scoped resume, retry exhaustion, unknown outcome reconciliation and read-back. This is a pure decision table, not a trusted authorization service or action executor.
- Motion sample: caption timing, deterministic scene motion and text width, duration/input bounds, real H.264/AAC render plus full decode/probe and subject-motion checks, overwrite refusal, optional local-audio input and narration-duration mismatch. Audio-input tests use a synthetic tone fixture, not spoken narration.

Install `narrated-motion-explainers/requirements.txt` and FFmpeg/ffprobe to run motion tests; they explicitly skip locally when unavailable. CI installs both and checks prerequisites before the suite, so all 41 root tests run, followed by the five inherited Cron Composer regressions (46 total). Python 3.11 is the CI target; local verification can use a newer compatible Python. FFmpeg builds must include libx264 and AAC. No real deployments, schedules, approvals or external TTS calls occur.

The release checker takes observed revision as operator-supplied evidence: it cannot attest hosting provenance, crawl every route, or prove all CDN edges. Motion checks do not prove speech alignment, audio quality, accessibility or layout at arbitrary custom text/font settings. Review decoded frames and listen to any narrated final output.

## Script-test scope and remaining limitations

The smoke suite syntax-checks every bundled Bash/Python script and exercises:

- Cron Composer's real offline `list`, `lint`, `stats`, and all four example jobs via `apply --all --dry-run`, with fully substituted prompts.
- Daily Archivist change scanning in a non-Git memory fixture, fact verification, and broken-symlink findings.
- Skill Security clean/high/critical fixtures, pre-install allow/block handling, and the all-installed-skills scanner in an isolated HOME.

All fixtures are temporary. The scanner is copied before execution because critical findings append to its own blocklist. Tests do not access an operator's HOME or install/modify real schedules. The existing six bundled scripts are intentionally unchanged in this format-only update.

This is not live OpenClaw integration coverage, a security assurance, or execution of all Markdown shell snippets. Live `apply`, `sync`, and `diff` require an explicitly authorized OpenClaw environment; no schedules are changed by the tests. Linux service commands, deletion examples, and Git-hook installation must only run against authorized targets.

Known pre-existing Archivist edge cases remain outside this format migration: `verify-facts.sh` exits nonzero when `~/bin` is absent, and `scan-changes.sh` exits nonzero in a Git workspace with no recent memory changes, because `set -euo pipefail` treats empty/missing probe results as failures. Workspace-specific customization and separate behavioral regressions are needed before deploying those templates unattended. Historical pricing examples in Cost Tracker must also be verified with the provider before use; this update does not refresh model prices.
