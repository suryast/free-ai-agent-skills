#!/usr/bin/env python3
"""
cron-compose.py — Assemble and apply OpenClaw cron job prompts from composable blocks.

Usage:
  python3 cron-compose.py <manifest.yaml> list
  python3 cron-compose.py <manifest.yaml> apply <name> [--dry-run] [--diff]
  python3 cron-compose.py <manifest.yaml> apply --all [--dry-run] [--diff]
  python3 cron-compose.py <manifest.yaml> lint
  python3 cron-compose.py <manifest.yaml> sync
  python3 cron-compose.py <manifest.yaml> diff [<name>]
  python3 cron-compose.py <manifest.yaml> stats
"""

import sys
import re
import subprocess
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
VAR_RE = re.compile(r"\{\{(\w+)\}\}")


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML manifest using PyYAML if available, else subprocess fallback."""
    if yaml is not None:
        with open(path) as f:
            return yaml.safe_load(f)
    result = subprocess.run(
        ["python3", "-c",
         f"import yaml, json; print(json.dumps(yaml.safe_load(open('{path}'))))"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error loading YAML: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def resolve_blocks_dir(manifest: dict[str, Any], manifest_path: Path) -> Path:
    """Resolve the blocks directory from the manifest or defaults."""
    blocks_dir_raw = manifest.get("blocks_dir")
    if blocks_dir_raw:
        p = Path(blocks_dir_raw)
        if p.is_absolute():
            return p
        # relative to manifest file's directory
        return (manifest_path.parent / p).resolve()
    # Default: blocks/ next to manifest
    return (manifest_path.parent / "blocks").resolve()


def load_block(blocks_dir: Path, block_name: str) -> str:
    """Load a block file by name (e.g. 'env/error-handling')."""
    block_path = blocks_dir / f"{block_name}.md"
    if not block_path.exists():
        raise FileNotFoundError(f"Block file not found: {block_path}")
    return block_path.read_text()


def substitute_vars(text: str, vars_dict: dict[str, str]) -> str:
    """Replace {{VAR}} placeholders with values from vars dict."""
    for key, value in vars_dict.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))
    return text


def assemble_prompt(blocks_dir: Path, cron: dict[str, Any]) -> str:
    """Assemble the full prompt for a cron entry."""
    blocks = cron.get("blocks", [])
    vars_dict = cron.get("vars", {}) or {}
    task = cron.get("task", "").strip()

    missing = [
        str(blocks_dir / f"{b}.md")
        for b in blocks
        if not (blocks_dir / f"{b}.md").exists()
    ]
    if missing:
        raise FileNotFoundError("Missing block files:\n" + "\n".join(f"  {p}" for p in missing))

    parts = []
    for block_name in blocks:
        content = load_block(blocks_dir, block_name)
        content = substitute_vars(content, vars_dict)
        parts.append(content.strip())

    if task:
        task = substitute_vars(task, vars_dict)
        parts.append(task)

    return "\n\n".join(parts)


def get_live_crons() -> list[dict[str, Any]]:
    """Fetch live crons from openclaw."""
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error fetching live crons: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    return data.get("jobs", [])


def get_live_prompt(cron_id: str) -> str | None:
    """Fetch the current live prompt for a cron by ID."""
    result = subprocess.run(
        ["openclaw", "cron", "get", cron_id, "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
        return data.get("message") or data.get("prompt") or data.get("task") or None
    except (json.JSONDecodeError, AttributeError):
        return None


def diff_summary(old: str, new: str) -> str:
    """Return a simple diff summary."""
    old_lines = set(old.splitlines())
    new_lines = set(new.splitlines())
    added = len(new_lines - old_lines)
    removed = len(old_lines - new_lines)
    unchanged = len(old_lines & new_lines)
    if added == 0 and removed == 0:
        return "(no changes)"
    return f"+{added} lines added, -{removed} removed, {unchanged} unchanged"


# ──────────────────────────────────────────────
# Commands
# ──────────────────────────────────────────────

def cmd_list(manifest: dict[str, Any]) -> int:
    crons = manifest.get("crons", {})
    print(f"{'Name':<35} {'ID':<40} {'Blocks'}")
    print("-" * 100)
    for name, cron in crons.items():
        cron_id = cron.get("id", "???")
        blocks = ", ".join(cron.get("blocks", []))
        print(f"{name:<35} {cron_id:<40} {blocks}")
    print(f"\nTotal: {len(crons)} crons")
    return 0


def cmd_apply(blocks_dir: Path, manifest: dict[str, Any], name: str, dry_run: bool, show_diff: bool = False) -> int:
    crons = manifest.get("crons", {})
    if name not in crons:
        print(f"Error: cron '{name}' not found in manifest.", file=sys.stderr)
        print(f"Available: {', '.join(crons.keys())}", file=sys.stderr)
        return 1

    cron = crons[name]
    cron_id = cron.get("id")
    if not cron_id:
        print(f"Error: cron '{name}' has no id.", file=sys.stderr)
        return 1

    try:
        prompt = assemble_prompt(blocks_dir, cron)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if show_diff:
        live_prompt = get_live_prompt(cron_id)
        if live_prompt is None:
            print(f"  {name}: (could not fetch live prompt)")
        else:
            print(f"  {name}: {diff_summary(live_prompt, prompt)}")
        if not dry_run:
            return 0

    if dry_run:
        print(f"=== DRY RUN: {name} ({cron_id}) ===")
        print(prompt)
        print(f"\n=== END ({len(prompt)} chars) ===")
        return 0

    print(f"Applying {name} ({cron_id})...")
    result = subprocess.run(
        ["openclaw", "cron", "edit", cron_id, "--message", prompt],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error applying {name}: {result.stderr}", file=sys.stderr)
        return 1
    print(f"✓ {name} applied ({len(prompt)} chars)")
    return 0


def cmd_apply_all(blocks_dir: Path, manifest: dict[str, Any], dry_run: bool, show_diff: bool = False) -> int:
    crons = manifest.get("crons", {})
    errors = []
    for name in crons:
        rc = cmd_apply(blocks_dir, manifest, name, dry_run, show_diff)
        if rc != 0:
            errors.append(name)
    if errors:
        print(f"\nFailed: {', '.join(errors)}", file=sys.stderr)
        return 1
    print(f"\n✓ All {len(crons)} crons {'(dry-run) ' if dry_run else ''}processed.")
    return 0


def cmd_lint(blocks_dir: Path, manifest: dict[str, Any]) -> int:
    crons = manifest.get("crons", {})
    errors: list[str] = []
    seen_ids: dict[str, str] = {}

    for name, cron in crons.items():
        prefix = f"[{name}]"

        cron_id = cron.get("id", "")
        if not cron_id:
            errors.append(f"{prefix} missing id field")
        elif not UUID_RE.match(str(cron_id)):
            errors.append(f"{prefix} id is not a valid UUID: {cron_id!r}")
        else:
            cron_id_str = str(cron_id)
            if cron_id_str in seen_ids:
                errors.append(f"{prefix} duplicate id {cron_id_str!r} (also used by {seen_ids[cron_id_str]!r})")
            else:
                seen_ids[cron_id_str] = name

        task = cron.get("task", "")
        if not task or not str(task).strip():
            errors.append(f"{prefix} task field is empty")

        blocks = cron.get("blocks", [])
        for block_name in blocks:
            block_path = blocks_dir / f"{block_name}.md"
            if not block_path.exists():
                errors.append(f"{prefix} block file missing: {block_name}.md (looked in {blocks_dir})")

        vars_dict = cron.get("vars", {}) or {}
        all_text = str(task) if task else ""
        for block_name in blocks:
            block_path = blocks_dir / f"{block_name}.md"
            if block_path.exists():
                all_text += "\n" + block_path.read_text()
        for var_match in VAR_RE.finditer(all_text):
            var_name = var_match.group(1)
            if var_name not in vars_dict:
                errors.append(f"{prefix} {{{{'{var_name}'}}}} referenced but not defined in vars")

    total = len(crons)
    if errors:
        for err in errors:
            print(f"❌ {err}")
        print(f"\n💥 {total} crons, {len(errors)} error(s)")
        return 1
    print(f"✅ {total} crons, 0 errors")
    return 0


def cmd_sync(manifest: dict[str, Any]) -> int:
    crons = manifest.get("crons", {})
    manifest_by_id: dict[str, str] = {
        str(c.get("id", "")): name
        for name, c in crons.items()
        if c.get("id")
    }

    print("Fetching live crons...")
    live_jobs = get_live_crons()
    live_by_id: dict[str, str] = {j["id"]: j["name"] for j in live_jobs if "id" in j}

    missing_from_manifest = [
        (lid, lname) for lid, lname in live_by_id.items() if lid not in manifest_by_id
    ]
    name_mismatches = [
        (lid, manifest_by_id[lid], lname)
        for lid, lname in live_by_id.items()
        if lid in manifest_by_id and manifest_by_id[lid] != lname
    ]
    missing_from_live = [
        (mid, mname) for mid, mname in manifest_by_id.items() if mid not in live_by_id
    ]

    any_drift = bool(missing_from_manifest or name_mismatches or missing_from_live)

    if missing_from_manifest:
        print(f"\n⚠️  Missing from manifest ({len(missing_from_manifest)}) — unmanaged live crons:")
        for cid, cname in missing_from_manifest:
            print(f"  {cname:<35} {cid}")

    if missing_from_live:
        print(f"\n⚠️  Stale in manifest ({len(missing_from_live)}) — not found live:")
        for cid, cname in missing_from_live:
            print(f"  {cname:<35} {cid}")

    if name_mismatches:
        print(f"\n⚠️  Name mismatches ({len(name_mismatches)}):")
        for cid, mname, lname in name_mismatches:
            print(f"  {cid:<40} manifest={mname!r}  live={lname!r}")

    if not any_drift:
        print(f"✅ Manifest and live are in sync ({len(crons)} crons, {len(live_jobs)} live)")

    return 1 if any_drift else 0


def cmd_diff(blocks_dir: Path, manifest: dict[str, Any], name: str | None = None) -> int:
    crons = manifest.get("crons", {})
    targets = [(name, crons[name])] if name else list(crons.items())

    if name and name not in crons:
        print(f"Error: cron '{name}' not found.", file=sys.stderr)
        return 1

    for cron_name, cron in targets:
        cron_id = cron.get("id")
        if not cron_id:
            print(f"  {cron_name}: (no id, skipping)")
            continue
        try:
            new_prompt = assemble_prompt(blocks_dir, cron)
        except FileNotFoundError as e:
            print(f"  {cron_name}: ERROR — {e}")
            continue
        live_prompt = get_live_prompt(str(cron_id))
        if live_prompt is None:
            print(f"  {cron_name}: (could not fetch live prompt)")
            continue
        print(f"  {cron_name}: {diff_summary(live_prompt, new_prompt)}")
    return 0


def cmd_stats(blocks_dir: Path, manifest: dict[str, Any]) -> int:
    crons = manifest.get("crons", {})
    total = len(crons)

    block_freq: dict[str, int] = {}
    block_counts: list[int] = []
    prompt_lengths: list[int] = []
    shallow_crons: list[str] = []

    for name, cron in crons.items():
        blocks = cron.get("blocks", []) or []
        block_counts.append(len(blocks))
        for b in blocks:
            block_freq[b] = block_freq.get(b, 0) + 1

        non_env = [b for b in blocks if not b.startswith("env/")]
        if not non_env:
            shallow_crons.append(name)

        try:
            prompt = assemble_prompt(blocks_dir, cron)
            prompt_lengths.append(len(prompt))
        except FileNotFoundError:
            pass

    avg_prompt = int(sum(prompt_lengths) / len(prompt_lengths)) if prompt_lengths else 0
    avg_blocks = sum(block_counts) / total if total else 0

    print("═" * 60)
    print(f"  📊 cron-compose stats — {total} crons")
    print("═" * 60)
    print(f"\n  Avg blocks/cron:  {avg_blocks:.1f}")
    print(f"  Avg prompt chars: {avg_prompt:,}")

    dist: dict[int, int] = {}
    for c in block_counts:
        dist[c] = dist.get(c, 0) + 1
    print("\n  Blocks per cron:")
    for bc in sorted(dist):
        print(f"    {bc:>2} blocks: {dist[bc]:>3} crons  {'█' * dist[bc]}")

    print("\n  Block usage (by # of crons):")
    for block, count in sorted(block_freq.items(), key=lambda x: -x[1]):
        print(f"    {block:<35} {count:>3}  {'█' * count}")

    if shallow_crons:
        print(f"\n  ⚡ Env-only crons (candidates for decomposition): {len(shallow_crons)}")
        for n in shallow_crons:
            print(f"    - {n}")
    else:
        print("\n  ✅ All crons use ops/patterns blocks")

    print()
    return 0


def main() -> int:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if len(args) < 2:
        print("Error: usage: cron-compose.py <manifest.yaml> <command> [...]", file=sys.stderr)
        print(__doc__)
        return 1

    manifest_path = Path(args[0]).resolve()
    if not manifest_path.exists():
        print(f"Error: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_yaml(manifest_path)
    blocks_dir = resolve_blocks_dir(manifest, manifest_path)
    cmd = args[1]
    rest = args[2:]

    if cmd == "list":
        return cmd_list(manifest)

    if cmd == "apply":
        dry_run = "--dry-run" in rest
        show_diff = "--diff" in rest
        rest = [a for a in rest if a not in ("--dry-run", "--diff")]
        if not rest:
            print("Error: 'apply' requires a cron name or --all", file=sys.stderr)
            return 1
        if rest[0] == "--all":
            return cmd_apply_all(blocks_dir, manifest, dry_run, show_diff)
        return cmd_apply(blocks_dir, manifest, rest[0], dry_run, show_diff)

    if cmd == "lint":
        return cmd_lint(blocks_dir, manifest)

    if cmd == "sync":
        return cmd_sync(manifest)

    if cmd == "diff":
        name = rest[0] if rest else None
        return cmd_diff(blocks_dir, manifest, name)

    if cmd == "stats":
        return cmd_stats(blocks_dir, manifest)

    print(f"Unknown subcommand: {cmd}", file=sys.stderr)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
